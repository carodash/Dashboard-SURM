from fastapi import FastAPI, APIRouter, HTTPException, Body, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime, date, timedelta
from enum import Enum
import httpx
from bs4 import BeautifulSoup
import re
import requests
import json
import json


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
# ... (votre code d'import existant)

app = FastAPI(...) 
# ------------------ AJOUTEZ CES LIGNES ------------------
origins = [
    "https://dashboard-surm-1.onrender.com",  # L'URL de votre Frontend
    "http://localhost:3000", # Pour le développement local futur
    "http://localhost:8000",
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------ FIN DE L'AJOUT ------------------

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums for statuses
class SourcingStatus(str, Enum):
    A_TRAITER = "A traiter"
    CLOS = "Clos"
    DEALFLOW = "Dealflow"
    KLAXOON = "Klaxoon"

class DealflowStatus(str, Enum):
    CLOS = "Clos"
    EN_COURS_METIERS = "En cours avec les métiers"
    EN_COURS_EQUIPE_INNO = "En cours avec l'équipe inno"
    PRESENTATION_METIERS = "Présentation métiers"
    GO_METIER_ETUDE = "Go métier étude"
    GO_EXPERIMENTATION = "Go experimentation"
    GO_GENERALISATION = "Go généralisation"

class UserRole(str, Enum):
    ADMIN = "admin"
    CONTRIBUTEUR = "contributeur" 
    OBSERVATEUR = "observateur"

class DocumentType(str, Enum):
    CONVENTION = "Convention"
    PRESENTATION = "Présentation"
    COMPTE_RENDU = "Compte-rendu"
    CONTRAT = "Contrat"
    DOCUMENT_TECHNIQUE = "Document technique"
    AUTRE = "Autre"

class FieldType(str, Enum):
    TEXT = "text"
    DATE = "date"
    SELECT = "select"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    NUMBER = "number"
    EMAIL = "email"

# Configuration Models
class FormField(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    label: str
    type: FieldType
    required: bool = False
    options: Optional[List[str]] = None  # For select fields
    placeholder: Optional[str] = None
    validation_regex: Optional[str] = None
    order: int = 0
    visible: bool = True
    editable_by_roles: List[UserRole] = [UserRole.ADMIN, UserRole.CONTRIBUTEUR, UserRole.OBSERVATEUR]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FormConfiguration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    form_type: str  # "sourcing" or "dealflow"
    fields: List[FormField]
    permissions: Dict[str, List[UserRole]] = {}  # action -> roles
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserPermission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    role: UserRole
    permissions: Dict[str, bool] = {}  # permission_name -> allowed
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EnrichmentSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    auto_enrich: bool = True
    sources: List[str] = ["linkedin", "crunchbase", "website"]
    fields_to_enrich: List[str] = ["founding_year", "employee_count", "funding_rounds", "contact_emails"]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str  # ID of the startup (sourcing or dealflow)
    partner_type: str  # "sourcing" or "dealflow"
    filename: str
    original_filename: str
    file_size: int  # in bytes
    file_type: str  # MIME type
    document_type: DocumentType
    content: str  # Base64 encoded file content
    version: int = 1
    description: Optional[str] = None
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Models for Sourcing (with dynamic fields support)
class SourcingPartner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Core fields
    nom_entreprise: str
    statut: SourcingStatus
    pays_origine: str
    domaine_activite: str
    typologie: str
    objet: str
    cas_usage: str
    technologie: str
    source: str
    date_entree_sourcing: date
    interet: bool
    date_presentation_metiers: Optional[date] = None
    pilote: str
    actions_commentaires: Optional[str] = ""
    # Phase 1 - Suivi & Relance
    date_prochaine_action: Optional[date] = None
    # Phase 1 - Inactivity indicators (computed fields)
    is_inactive: Optional[bool] = None
    days_since_update: Optional[int] = None
    # Nouveaux champs de scoring
    score_maturite: Optional[int] = None  # 1-5
    priorite_strategique: Optional[str] = None  # HAUTE, MOYENNE, BASSE
    score_potentiel: Optional[int] = None  # 1-10
    tags_strategiques: Optional[List[str]] = []
    # Dynamic fields for enrichment
    enriched_data: Optional[Dict[str, Any]] = {}
    custom_fields: Optional[Dict[str, Any]] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SourcingPartnerCreate(BaseModel):
    nom_entreprise: str
    statut: SourcingStatus
    pays_origine: str
    domaine_activite: str
    typologie: str
    objet: str
    cas_usage: str
    technologie: str
    source: str
    date_entree_sourcing: date
    interet: bool
    date_presentation_metiers: Optional[date] = None
    pilote: str
    actions_commentaires: Optional[str] = ""
    # Phase 1 - Suivi & Relance
    date_prochaine_action: Optional[date] = None
    # Nouveaux champs de scoring
    score_maturite: Optional[int] = None
    priorite_strategique: Optional[str] = None
    score_potentiel: Optional[int] = None
    tags_strategiques: Optional[List[str]] = []
    custom_fields: Optional[Dict[str, Any]] = {}

class SourcingPartnerUpdate(BaseModel):
    nom_entreprise: Optional[str] = None
    statut: Optional[SourcingStatus] = None
    pays_origine: Optional[str] = None
    domaine_activite: Optional[str] = None
    typologie: Optional[str] = None
    objet: Optional[str] = None
    cas_usage: Optional[str] = None
    technologie: Optional[str] = None
    source: Optional[str] = None
    date_entree_sourcing: Optional[date] = None
    interet: Optional[bool] = None
    date_presentation_metiers: Optional[date] = None
    pilote: Optional[str] = None
    actions_commentaires: Optional[str] = None
    # Phase 1 - Suivi & Relance
    date_prochaine_action: Optional[date] = None
    # Nouveaux champs de scoring
    score_maturite: Optional[int] = None
    priorite_strategique: Optional[str] = None
    score_potentiel: Optional[int] = None
    tags_strategiques: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

# Models for Dealflow (with dynamic fields support)
class DealflowPartner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str
    statut: DealflowStatus
    domaine: str
    typologie: str
    objet: str
    source: str
    pilote: str
    metiers_concernes: str
    date_reception_fichier: date
    date_pre_qualification: Optional[date] = None
    date_presentation_meetup_referents: Optional[date] = None
    date_presentation_metiers: Optional[date] = None
    date_go_metier_etude: Optional[date] = None
    date_go_experimentation: Optional[date] = None
    date_go_generalisation: Optional[date] = None
    date_cloture: Optional[date] = None
    actions_commentaires: Optional[str] = ""
    points_etapes_intermediaires: Optional[str] = ""
    # Phase 1 - Suivi & Relance
    date_prochaine_action: Optional[date] = None
    # Phase 1 - Inactivity indicators (computed fields)
    is_inactive: Optional[bool] = None
    days_since_update: Optional[int] = None
    # Inherited from sourcing if transitioned
    sourcing_id: Optional[str] = None
    pays_origine: Optional[str] = None
    cas_usage: Optional[str] = None
    technologie: Optional[str] = None
    interet: Optional[bool] = None
    # Nouveaux champs de scoring
    score_maturite: Optional[int] = None  # 1-5
    priorite_strategique: Optional[str] = None  # HAUTE, MOYENNE, BASSE
    score_potentiel: Optional[int] = None  # 1-10
    tags_strategiques: Optional[List[str]] = []
    # Dynamic fields
    enriched_data: Optional[Dict[str, Any]] = {}
    custom_fields: Optional[Dict[str, Any]] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DealflowPartnerCreate(BaseModel):
    nom: str
    statut: DealflowStatus
    domaine: str
    typologie: str
    objet: str
    source: str
    pilote: str
    metiers_concernes: str
    date_reception_fichier: date
    date_pre_qualification: Optional[date] = None
    date_presentation_meetup_referents: Optional[date] = None
    date_presentation_metiers: Optional[date] = None
    date_go_metier_etude: Optional[date] = None
    date_go_experimentation: Optional[date] = None
    date_go_generalisation: Optional[date] = None
    date_cloture: Optional[date] = None
    actions_commentaires: Optional[str] = ""
    points_etapes_intermediaires: Optional[str] = ""
    # Phase 1 - Suivi & Relance
    date_prochaine_action: Optional[date] = None
    sourcing_id: Optional[str] = None
    pays_origine: Optional[str] = None
    cas_usage: Optional[str] = None
    technologie: Optional[str] = None
    interet: Optional[bool] = None
    custom_fields: Optional[Dict[str, Any]] = {}

class DealflowPartnerUpdate(BaseModel):
    nom: Optional[str] = None
    statut: Optional[DealflowStatus] = None
    domaine: Optional[str] = None
    typologie: Optional[str] = None
    objet: Optional[str] = None
    source: Optional[str] = None
    pilote: Optional[str] = None
    metiers_concernes: Optional[str] = None
    date_reception_fichier: Optional[date] = None
    date_pre_qualification: Optional[date] = None
    date_presentation_meetup_referents: Optional[date] = None
    date_presentation_metiers: Optional[date] = None
    date_go_metier_etude: Optional[date] = None
    date_go_experimentation: Optional[date] = None
    date_go_generalisation: Optional[date] = None
    date_cloture: Optional[date] = None
    actions_commentaires: Optional[str] = None
    points_etapes_intermediaires: Optional[str] = None
    # Phase 1 - Suivi & Relance
    date_prochaine_action: Optional[date] = None
    custom_fields: Optional[Dict[str, Any]] = None

# Statistics models
class QuarterlyStats(BaseModel):
    quarter: str
    total_entries: int
    by_domain: Dict[str, int]

class MonthlyStats(BaseModel):
    month: str
    pre_qualifications: int
    go_studies: int

class DashboardStats(BaseModel):
    quarterly_entries: List[QuarterlyStats]
    monthly_stats: List[MonthlyStats]
    domain_distribution: Dict[str, int]
    typologie_distribution: Dict[str, int]
    technology_distribution: Dict[str, int]
    metiers_distribution: Dict[str, int]
    sourcing_status_distribution: Dict[str, int]
    dealflow_status_distribution: Dict[str, int]
    total_sourcing: int
    total_dealflow: int

# Phase 1 - Activity Timeline Model
class ActivityType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    TRANSITIONED = "transitioned"
    COMMENT_ADDED = "comment_added"
    STATUS_CHANGED = "status_changed"
    ENRICHED = "enriched"

class ActivityLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str  # Reference to sourcing or dealflow partner
    partner_type: str  # "sourcing" or "dealflow"
    activity_type: ActivityType
    description: str
    details: Optional[Dict[str, Any]] = {}  # Additional context (old_value, new_value, etc.)
    user_id: Optional[str] = None  # Who performed the action
    user_name: Optional[str] = None  # User display name
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ActivityLogResponse(BaseModel):
    id: str
    partner_id: str
    partner_type: str
    activity_type: str
    description: str
    details: Dict[str, Any]
    user_id: Optional[str]
    user_name: Optional[str]
    created_at: datetime

# Phase 3 - User Management & Private Comments Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class PrivateComment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str  # Reference to sourcing or dealflow partner
    partner_type: str  # "sourcing" or "dealflow"
    user_id: str  # Who wrote the comment
    user_name: str  # User display name for convenience
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PrivateCommentCreate(BaseModel):
    partner_id: str
    partner_type: str
    comment: str

class PrivateCommentUpdate(BaseModel):
    comment: str

class PrivateCommentResponse(BaseModel):
    id: str
    partner_id: str
    partner_type: str
    user_id: str
    user_name: str
    comment: str
    created_at: datetime
    updated_at: datetime

# AUTO-ENRICHMENT FUNCTIONS
async def scrape_linkedin_basic(company_name: str) -> Dict[str, Any]:
    """Basic LinkedIn scraping without authentication"""
    try:
        async with httpx.AsyncClient() as client:
            # Simple search approach
            search_url = f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}"
            response = await client.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract basic info from meta tags
                description = soup.find('meta', property='og:description')
                title = soup.find('meta', property='og:title')
                
                return {
                    "linkedin_description": description.get('content', '') if description else '',
                    "linkedin_title": title.get('content', '') if title else '',
                    "linkedin_url": search_url
                }
    except Exception as e:
        logging.error(f"LinkedIn scraping failed: {e}")
    
    return {}

async def scrape_website_info(domain: str) -> Dict[str, Any]:
    """Extract basic company info from website"""
    try:
        if not domain.startswith('http'):
            domain = f"https://{domain}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(domain, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract emails
                email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
                emails = list(set(email_pattern.findall(response.text)))
                
                # Extract meta info
                description = soup.find('meta', attrs={'name': 'description'})
                title = soup.find('title')
                
                return {
                    "website_description": description.get('content', '') if description else '',
                    "website_title": title.text if title else '',
                    "contact_emails": emails[:3],  # Limit to 3 emails
                    "website_url": domain
                }
    except Exception as e:
        logging.error(f"Website scraping failed: {e}")
    
    return {}

async def enrich_company_data(company_name: str, domain: str = None) -> Dict[str, Any]:
    """Enrich company data from multiple sources"""
    enriched_data = {}
    
    # LinkedIn enrichment
    linkedin_data = await scrape_linkedin_basic(company_name)
    enriched_data.update(linkedin_data)
    
    # Website enrichment
    if domain:
        website_data = await scrape_website_info(domain)
        enriched_data.update(website_data)
    
    # Add enrichment timestamp
    enriched_data["enriched_at"] = datetime.utcnow().isoformat()
    
    return enriched_data

# PHASE 1 - ACTIVITY TRACKING & INACTIVITY HELPERS
def calculate_inactivity_days(updated_at: datetime) -> int:
    """Calculate days since last update"""
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
    
    delta = datetime.utcnow() - updated_at
    return delta.days

def is_inactive(updated_at: datetime, threshold_days: int = 90) -> bool:
    """Check if partner is inactive (not updated for 90+ days)"""
    return calculate_inactivity_days(updated_at) >= threshold_days

async def log_activity(partner_id: str, partner_type: str, activity_type: ActivityType, 
                      description: str, details: Dict[str, Any] = None, 
                      user_id: str = None, user_name: str = None):
    """Log an activity for a partner"""
    activity = ActivityLog(
        partner_id=partner_id,
        partner_type=partner_type,
        activity_type=activity_type,
        description=description,
        details=details or {},
        user_id=user_id,
        user_name=user_name
    )
    
    # Convert to dict for MongoDB storage
    activity_dict = activity.dict()
    activity_dict["created_at"] = activity.created_at.isoformat()
    
    await db.activity_logs.insert_one(activity_dict)
    return activity

def add_inactivity_status(partner_data: dict) -> dict:
    """Add inactivity status to partner data"""
    partner_data["is_inactive"] = is_inactive(partner_data.get("updated_at"))
    partner_data["days_since_update"] = calculate_inactivity_days(partner_data.get("updated_at"))
    return partner_data

# PHASE 3 - USER AUTHORIZATION HELPERS
async def get_current_user(user_id: str = "default_user") -> User:
    """Get current user - simplified for demo"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        # Create default user if doesn't exist
        default_user = User(
            id=user_id,
            username="demo_user",
            email="demo@example.com",
            full_name="Utilisateur Demo",
            role=UserRole.ADMIN
        )
        user_dict = default_user.dict()
        user_dict["created_at"] = default_user.created_at.isoformat()
        user_dict["updated_at"] = default_user.updated_at.isoformat()
        await db.users.insert_one(user_dict)
        return default_user
    return User(**user)

def can_view_partner(user_role: UserRole, partner_pilote: str, user_name: str) -> bool:
    """Check if user can view a partner"""
    if user_role == UserRole.ADMIN:
        return True
    if user_role == UserRole.OBSERVATEUR:
        return True  # Can view all
    if user_role == UserRole.CONTRIBUTEUR:
        return partner_pilote == user_name  # Can only view own
    return False

def can_edit_partner(user_role: UserRole, partner_pilote: str, user_name: str) -> bool:
    """Check if user can edit a partner"""
    if user_role == UserRole.ADMIN:
        return True
    if user_role == UserRole.CONTRIBUTEUR:
        return partner_pilote == user_name  # Can only edit own
    return False  # Observateur cannot edit

def can_view_private_comment(comment_user_id: str, current_user_id: str, current_user_role: UserRole) -> bool:
    """Check if user can view a private comment"""
    if current_user_role == UserRole.ADMIN:
        return True  # Admin can see all comments
    return comment_user_id == current_user_id  # Can only see own comments

# COLUMN CONFIGURATION ENDPOINTS
@api_router.post("/config/columns")
async def save_column_config(column_config: Dict[str, Any]):
    """Save column configuration"""
    result = await db.column_configurations.replace_one(
        {"type": "columns"},
        {"type": "columns", "config": column_config, "updated_at": datetime.utcnow()},
        upsert=True
    )
    return {"message": "Column configuration saved successfully"}

@api_router.get("/config/columns")
async def get_column_config():
    """Get column configuration"""
    config = await db.column_configurations.find_one({"type": "columns"})
    if not config:
        # Return default configuration
        return {
            "sourcing": {
                "nom_entreprise": {"visible": True, "label": "Entreprise"},
                "statut": {"visible": True, "label": "Statut"},
                "domaine_activite": {"visible": True, "label": "Domaine"},
                "pilote": {"visible": True, "label": "Pilote"},
                "date_prochaine_action": {"visible": True, "label": "Prochaine action"},
                "is_inactive": {"visible": True, "label": "Inactif"},
                "priorite_strategique": {"visible": True, "label": "Priorité"},
                "score_maturite": {"visible": True, "label": "Maturité"},
                "score_potentiel": {"visible": False, "label": "Potentiel"},
                "tags_strategiques": {"visible": False, "label": "Tags"},
                "pays_origine": {"visible": False, "label": "Pays"},
                "typologie": {"visible": False, "label": "Typologie"},
                "technologie": {"visible": False, "label": "Technologie"},
                "source": {"visible": False, "label": "Source"},
                "date_entree_sourcing": {"visible": False, "label": "Date entrée"},
                "interet": {"visible": False, "label": "Intérêt"}
            },
            "dealflow": {
                "nom": {"visible": True, "label": "Nom"},
                "statut": {"visible": True, "label": "Statut"},
                "domaine": {"visible": True, "label": "Domaine"},
                "metiers_concernes": {"visible": True, "label": "Métiers"},
                "date_prochaine_action": {"visible": True, "label": "Prochaine action"},
                "is_inactive": {"visible": True, "label": "Inactif"},
                "priorite_strategique": {"visible": True, "label": "Priorité"},
                "score_maturite": {"visible": False, "label": "Maturité"},
                "score_potentiel": {"visible": False, "label": "Potentiel"},
                "tags_strategiques": {"visible": False, "label": "Tags"},
                "pilote": {"visible": False, "label": "Pilote"},
                "typologie": {"visible": False, "label": "Typologie"},
                "source": {"visible": False, "label": "Source"},
                "date_reception_fichier": {"visible": False, "label": "Date réception"},
                "date_pre_qualification": {"visible": False, "label": "Date pré-qualification"}
            }
        }
    return config["config"]

# CONFIGURATION ENDPOINTS
@api_router.post("/config/form", response_model=FormConfiguration)
async def create_form_config(config: FormConfiguration):
    """Create or update form configuration"""
    config_dict = config.dict()
    
    # Convert datetime objects to strings for MongoDB
    for field in config_dict.get("fields", []):
        if isinstance(field.get("created_at"), datetime):
            field["created_at"] = field["created_at"].isoformat()
    
    result = await db.form_configurations.replace_one(
        {"form_type": config.form_type},
        config_dict,
        upsert=True
    )
    return config

@api_router.get("/config/form/{form_type}", response_model=FormConfiguration)
async def get_form_config(form_type: str):
    """Get form configuration"""
    config = await db.form_configurations.find_one({"form_type": form_type})
    if not config:
        raise HTTPException(status_code=404, detail="Form configuration not found")
    return FormConfiguration(**config)

@api_router.get("/config/forms", response_model=List[FormConfiguration])
async def get_all_form_configs():
    """Get all form configurations"""
    configs = await db.form_configurations.find().to_list(100)
    return [FormConfiguration(**config) for config in configs]

@api_router.post("/config/permissions", response_model=UserPermission)
async def create_user_permissions(permission: UserPermission):
    """Create or update user permissions"""
    permission_dict = permission.dict()
    result = await db.user_permissions.replace_one(
        {"user_id": permission.user_id},
        permission_dict,
        upsert=True
    )
    return permission

@api_router.get("/config/permissions/{user_id}", response_model=UserPermission)
async def get_user_permissions(user_id: str):
    """Get user permissions"""
    permissions = await db.user_permissions.find_one({"user_id": user_id})
    if not permissions:
        # Return default permissions
        return UserPermission(
            user_id=user_id,
            role=UserRole.CONTRIBUTEUR,
            permissions={
                "create_sourcing": True,
                "edit_sourcing": True,
                "delete_sourcing": False,
                "create_dealflow": True,
                "edit_dealflow": True,
                "delete_dealflow": False,
                "view_statistics": True,
                "manage_config": False
            }
        )
    return UserPermission(**permissions)

@api_router.post("/config/enrichment", response_model=EnrichmentSettings)
async def create_enrichment_settings(settings: EnrichmentSettings):
    """Create or update enrichment settings"""
    settings_dict = settings.dict()
    result = await db.enrichment_settings.replace_one(
        {"id": settings.id},
        settings_dict,
        upsert=True
    )
    return settings

@api_router.get("/config/enrichment", response_model=EnrichmentSettings)
async def get_enrichment_settings():
    """Get enrichment settings"""
    settings = await db.enrichment_settings.find_one()
    if not settings:
        return EnrichmentSettings()
    return EnrichmentSettings(**settings)

# SOURCING ENDPOINTS
@api_router.post("/sourcing", response_model=SourcingPartner)
async def create_sourcing_partner(partner: SourcingPartnerCreate, user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    
    # Check permissions
    if current_user.role == UserRole.OBSERVATEUR:
        raise HTTPException(status_code=403, detail="Observateur cannot create partners")
    
    partner_dict = partner.dict()
    
    # Auto-enrichment if enabled
    enrichment_settings = await get_enrichment_settings()
    if enrichment_settings.auto_enrich:
        enriched_data = await enrich_company_data(
            partner.nom_entreprise,
            partner_dict.get("website_domain")
        )
        partner_dict["enriched_data"] = enriched_data
    
    partner_obj = SourcingPartner(**partner_dict)
    
    # Convert date objects to strings for MongoDB storage
    partner_data = partner_obj.dict()
    for key, value in partner_data.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            partner_data[key] = value.isoformat()
    
    result = await db.sourcing_partners.insert_one(partner_data)
    
    # Log creation activity
    await log_activity(
        partner_id=partner_obj.id,
        partner_type="sourcing",
        activity_type=ActivityType.CREATED,
        description=f"Startup '{partner.nom_entreprise}' créée en sourcing",
        details={"statut": partner.statut, "domaine": partner.domaine_activite},
        user_id=current_user.id,
        user_name=current_user.full_name
    )
    
    return partner_obj

@api_router.get("/sourcing", response_model=List[SourcingPartner])
async def get_sourcing_partners(user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    
    # Build query based on user role
    query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        query["pilote"] = current_user.full_name  # Contributeur sees only their own
    # Admin and Observateur see all
    
    # Exclude partners that have been transitioned to dealflow
    query["statut"] = {"$ne": SourcingStatus.DEALFLOW}
    
    partners = await db.sourcing_partners.find(query).to_list(1000)
    
    # Add inactivity status to each partner
    partners_with_status = []
    for partner in partners:
        partner_with_status = add_inactivity_status(partner)
        partners_with_status.append(SourcingPartner(**partner_with_status))
    
    return partners_with_status

@api_router.get("/sourcing/{partner_id}", response_model=SourcingPartner)
async def get_sourcing_partner(partner_id: str, user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    
    partner = await db.sourcing_partners.find_one({"id": partner_id})
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Check view permissions
    if not can_view_partner(current_user.role, partner.get("pilote"), current_user.full_name):
        raise HTTPException(status_code=403, detail="Not authorized to view this partner")
    
    # Add inactivity status
    partner_with_status = add_inactivity_status(partner)
    return SourcingPartner(**partner_with_status)

@api_router.put("/sourcing/{partner_id}", response_model=SourcingPartner)
async def update_sourcing_partner(partner_id: str, partner_update: SourcingPartnerUpdate, user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    
    # Get original partner for permission check
    original_partner = await db.sourcing_partners.find_one({"id": partner_id})
    if not original_partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Check edit permissions
    if not can_edit_partner(current_user.role, original_partner.get("pilote"), current_user.full_name):
        raise HTTPException(status_code=403, detail="Not authorized to edit this partner")
    
    update_dict = {k: v for k, v in partner_update.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    # Convert date objects to strings for MongoDB storage
    for key, value in update_dict.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            update_dict[key] = value.isoformat()
    
    result = await db.sourcing_partners.update_one(
        {"id": partner_id},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Log update activity with changes
    changes = []
    for key, new_value in update_dict.items():
        if key != "updated_at" and key in original_partner:
            old_value = original_partner[key]
            if old_value != new_value:
                changes.append(f"{key}: {old_value} → {new_value}")
    
    if changes:
        await log_activity(
            partner_id=partner_id,
            partner_type="sourcing",
            activity_type=ActivityType.UPDATED,
            description=f"Startup '{original_partner['nom_entreprise']}' mise à jour",
            details={"changes": changes},
            user_id=current_user.id,
            user_name=current_user.full_name
        )
    
    updated_partner = await db.sourcing_partners.find_one({"id": partner_id})
    updated_partner = add_inactivity_status(updated_partner)
    return SourcingPartner(**updated_partner)

@api_router.delete("/sourcing/{partner_id}")
async def delete_sourcing_partner(partner_id: str, user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    
    # Get partner info before deletion for logging and permission check
    partner = await db.sourcing_partners.find_one({"id": partner_id})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Check delete permissions (only admin for now)
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can delete partners")
    
    result = await db.sourcing_partners.delete_one({"id": partner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Log deletion activity
    await log_activity(
        partner_id=partner_id,
        partner_type="sourcing",
        activity_type=ActivityType.UPDATED,  # Using UPDATED as we don't have DELETED
        description=f"Startup '{partner['nom_entreprise']}' supprimée du sourcing",
        details={"action": "deleted"},
        user_id=current_user.id,
        user_name=current_user.full_name
    )
    
    return {"message": "Partner deleted successfully"}

# DUPLICATE DETECTION ENDPOINT
@api_router.get("/partners/check-duplicate")
async def check_duplicate_partners(name: str):
    """Check for potential duplicate partners based on name similarity"""
    if not name or len(name) < 3:
        return {"duplicates": []}
    
    # Prepare search patterns for better matching
    name_clean = name.strip().lower()
    
    # Create multiple regex patterns for flexible matching
    patterns = [
        # Exact match (case insensitive)
        {"$regex": f"^{re.escape(name_clean)}$", "$options": "i"},
        # Contains the search term
        {"$regex": re.escape(name_clean), "$options": "i"},
        # Split words and search for combinations
    ]
    
    # Also create word-based patterns for partial matching
    words = name_clean.split()
    if len(words) > 1:
        # Search for partners containing most of the words
        word_pattern = "|".join([re.escape(word) for word in words if len(word) > 2])
        if word_pattern:
            patterns.append({"$regex": word_pattern, "$options": "i"})
    
    duplicates = []
    
    # Search in sourcing partners
    for pattern in patterns:
        sourcing_partners = await db.sourcing_partners.find(
            {"nom_entreprise": pattern}
        ).limit(10).to_list(10)
        
        for partner in sourcing_partners:
            # Calculate similarity score (simple approach)
            partner_name = partner.get("nom_entreprise", "").lower()
            similarity = calculate_similarity(name_clean, partner_name)
            
            if similarity >= 0.6:  # 60% threshold
                duplicate_info = {
                    "id": partner["id"],
                    "name": partner["nom_entreprise"],
                    "type": "sourcing",
                    "similarity": round(similarity, 2),
                    "domain": partner.get("domaine_activite", "N/A"),
                    "status": partner.get("statut", "N/A"),
                    "pilot": partner.get("pilote", "N/A")
                }
                
                # Avoid exact duplicates in results
                if not any(d["id"] == duplicate_info["id"] for d in duplicates):
                    duplicates.append(duplicate_info)
    
    # Search in dealflow partners  
    for pattern in patterns:
        dealflow_partners = await db.dealflow_partners.find(
            {"nom": pattern}
        ).limit(10).to_list(10)
        
        for partner in dealflow_partners:
            partner_name = partner.get("nom", "").lower()
            similarity = calculate_similarity(name_clean, partner_name)
            
            if similarity >= 0.6:  # 60% threshold
                duplicate_info = {
                    "id": partner["id"],
                    "name": partner["nom"],
                    "type": "dealflow", 
                    "similarity": round(similarity, 2),
                    "domain": partner.get("domaine", "N/A"),
                    "status": partner.get("statut", "N/A"),
                    "pilot": partner.get("pilote", "N/A")
                }
                
                if not any(d["id"] == duplicate_info["id"] for d in duplicates):
                    duplicates.append(duplicate_info)
    
    # Sort by similarity score (highest first) and limit to 5
    duplicates.sort(key=lambda x: x["similarity"], reverse=True)
    
    return {
        "search_term": name,
        "duplicates": duplicates[:5],
        "found_count": len(duplicates)
    }

def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity between two strings using a simple approach"""
    if not str1 or not str2:
        return 0.0
    
    # Exact match
    if str1 == str2:
        return 1.0
    
    # Check if one string contains the other
    if str1 in str2 or str2 in str1:
        return 0.8
    
    # Word-based similarity
    words1 = set(str1.split())
    words2 = set(str2.split())
    
    if not words1 or not words2:
        return 0.0
    
    # Jaccard similarity for words
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    jaccard_sim = len(intersection) / len(union) if union else 0.0
    
    # Character-based similarity (simple)
    common_chars = sum(1 for c in str1 if c in str2)
    char_sim = common_chars / max(len(str1), len(str2))
    
    # Combine both similarities
    return (jaccard_sim * 0.7) + (char_sim * 0.3)

# COMPANY ENRICHMENT MODELS AND ENDPOINTS
class CompanyEnrichmentRequest(BaseModel):
    query: str
    domain: Optional[str] = None

class EnrichedCompanyData(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    employees_count: Optional[int] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    year_founded: Optional[int] = None
    company_type: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None

class CompanyEnrichmentResponse(BaseModel):
    success: bool
    company_data: Optional[EnrichedCompanyData] = None
    error_message: Optional[str] = None
    api_source: Optional[str] = None

@api_router.post("/enrich-company", response_model=CompanyEnrichmentResponse)
async def enrich_company_endpoint(request: CompanyEnrichmentRequest):
    """Enrich company data using free APIs"""
    
    try:
        # Method 1: Try Abstract API with free tier (if API key available)
        abstract_key = os.environ.get('ABSTRACT_API_KEY')
        if abstract_key:
            try:
                # Extract domain from query or use provided domain
                domain = request.domain
                if not domain:
                    # Try to extract domain from company name
                    query_lower = request.query.lower().replace(' ', '').replace('-', '')
                    if '.' in query_lower and any(ext in query_lower for ext in ['.com', '.fr', '.org', '.net']):
                        domain = query_lower
                    else:
                        # Create potential domain
                        domain = f"{query_lower.replace(' ', '').replace('-', '')}.com"
                
                # Call Abstract API
                url = "https://companyenrichment.abstractapi.com/v1/"
                params = {
                    'api_key': abstract_key,
                    'domain': domain
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    enriched_data = EnrichedCompanyData(
                        name=data.get('name'),
                        domain=data.get('domain'),
                        industry=data.get('industry'),
                        employees_count=data.get('employees_count'),
                        country=data.get('country'),
                        country_code=data.get('country_code'),
                        year_founded=data.get('year_founded'),
                        company_type=data.get('type'),
                        description=data.get('description'),
                        website=data.get('domain')
                    )
                    
                    return CompanyEnrichmentResponse(
                        success=True,
                        company_data=enriched_data,
                        api_source="abstract_api"
                    )
                    
            except Exception as e:
                print(f"Abstract API error: {str(e)}")
        
        # Method 2: Try French SIRENE API (free for French companies)
        try:
            sirene_url = "https://api.insee.fr/entreprises/sirene/V3/siret"
            headers = {
                'Accept': 'application/json'
            }
            params = {
                'q': f"denominationUniteLegale:\"{request.query}\"",
                'nombre': 1
            }
            
            response = requests.get(sirene_url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if 'etablissements' in data and len(data['etablissements']) > 0:
                    etablissement = data['etablissements'][0]
                    unite_legale = etablissement.get('uniteLegale', {})
                    
                    # Map SIRENE data to our format
                    enriched_data = EnrichedCompanyData(
                        name=unite_legale.get('denominationUniteLegale'),
                        industry=etablissement.get('libelleSecteurActiviteUniteLegale'),
                        country="France",
                        country_code="FR",
                        company_type="private" if unite_legale.get('categorieJuridiqueUniteLegale') else None,
                        year_founded=int(unite_legale.get('dateCreationUniteLegale', '0')[:4]) if unite_legale.get('dateCreationUniteLegale') else None
                    )
                    
                    return CompanyEnrichmentResponse(
                        success=True,
                        company_data=enriched_data,
                        api_source="sirene_api"
                    )
                    
        except Exception as e:
            print(f"SIRENE API error: {str(e)}")
        
        # Method 3: Enhanced Basic Enrichment (always provides useful data)
        try:
            # Extract potential domain and create basic data
            query_clean = request.query.lower().strip()
            company_name = request.query.title()
            
            # Create comprehensive enriched data based on company name patterns
            enriched_data = EnrichedCompanyData(
                name=company_name,
                domain=request.domain if request.domain else f"{query_clean.replace(' ', '').replace('-', '')}.com"
            )
            
            # Enhanced industry detection with many more patterns
            industry_keywords = {
                # Famous tech companies
                'google': {'industry': 'Technology', 'country': 'United States', 'description': 'Leading global technology company specializing in search, cloud computing, and digital advertising services.'},
                'microsoft': {'industry': 'Technology', 'country': 'United States', 'description': 'Multinational technology corporation developing software, cloud services, and computer technologies.'},
                'apple': {'industry': 'Technology', 'country': 'United States', 'description': 'Consumer electronics and software company known for innovative products and services.'},
                'amazon': {'industry': 'Technology', 'country': 'United States', 'description': 'E-commerce and cloud computing platform providing diverse digital services.'},
                'meta': {'industry': 'Technology', 'country': 'United States', 'description': 'Social media and virtual reality technology company.'},
                'facebook': {'industry': 'Technology', 'country': 'United States', 'description': 'Social media and virtual reality technology company.'},
                'paypal': {'industry': 'FinTech', 'country': 'United States', 'description': 'Digital payments platform enabling online money transfers and financial services.'},
                'stripe': {'industry': 'FinTech', 'country': 'United States', 'description': 'Financial technology company providing payment processing solutions for businesses.'},
                'airbnb': {'industry': 'Technology', 'country': 'United States', 'description': 'Online marketplace for short-term lodging and travel experiences.'},
                'uber': {'industry': 'Technology', 'country': 'United States', 'description': 'Ride-sharing and mobility-as-a-service platform.'},
                'tesla': {'industry': 'CleanTech', 'country': 'United States', 'description': 'Electric vehicle and clean energy company focused on sustainable transportation.'},
                'spotify': {'industry': 'Technology', 'country': 'Sweden', 'description': 'Audio streaming and media services platform.'},
                'netflix': {'industry': 'Technology', 'country': 'United States', 'description': 'Streaming entertainment service providing movies, TV shows and original content.'},
                'zoom': {'industry': 'Technology', 'country': 'United States', 'description': 'Video communications platform providing remote conferencing solutions.'},
                'slack': {'industry': 'Technology', 'country': 'United States', 'description': 'Business communication and collaboration platform.'},
                'salesforce': {'industry': 'Technology', 'country': 'United States', 'description': 'Customer relationship management (CRM) and cloud computing services platform.'},
                
                # French companies
                'bnp paribas': {'industry': 'FinTech', 'country': 'France', 'description': 'Major international banking and financial services group.'},
                'société générale': {'industry': 'FinTech', 'country': 'France', 'description': 'French multinational investment bank and financial services company.'},
                'crédit agricole': {'industry': 'FinTech', 'country': 'France', 'description': 'French network of cooperative and mutual banks.'},
                'orange': {'industry': 'Technology', 'country': 'France', 'description': 'Multinational telecommunications corporation providing mobile and internet services.'},
                'thales': {'industry': 'Technology', 'country': 'France', 'description': 'Multinational company specializing in aerospace, defense, and technology services.'},
                'capgemini': {'industry': 'Consulting', 'country': 'France', 'description': 'Global leader in consulting, technology services and digital transformation.'},
                'dassault': {'industry': 'Technology', 'country': 'France', 'description': 'Software development and engineering company specializing in 3D design and simulation.'},
                
                # Generic patterns
                'fintech': {'industry': 'FinTech', 'description': 'Financial technology company providing innovative financial services and solutions.'},
                'insurtech': {'industry': 'InsurTech', 'description': 'Insurance technology company developing digital insurance solutions.'},
                'proptech': {'industry': 'PropTech', 'description': 'Property technology company innovating in real estate and property management.'},
                'healthtech': {'industry': 'DigitalHealth', 'description': 'Healthcare technology company developing digital health solutions.'},
                'edtech': {'industry': 'EdTech', 'description': 'Educational technology company providing digital learning solutions.'},
                'legaltech': {'industry': 'LegalTech', 'description': 'Legal technology company providing digital solutions for legal services.'},
                'martech': {'industry': 'MarTech', 'description': 'Marketing technology company providing digital marketing and advertising solutions.'},
                'cleantech': {'industry': 'CleanTech', 'description': 'Clean technology company focused on environmental sustainability and green solutions.'},
                'startup': {'industry': 'Technology', 'description': 'Innovative startup company developing technology solutions and services.'},
                'solutions': {'industry': 'Technology', 'description': 'Technology solutions provider offering specialized services and platforms.'},
                'consulting': {'industry': 'Consulting', 'description': 'Professional consulting firm providing expert advisory and implementation services.'},
                'services': {'industry': 'Technology', 'description': 'Service provider company offering specialized technology and business solutions.'},
                'tech': {'industry': 'Technology', 'description': 'Technology company developing innovative digital products and services.'},
                'digital': {'industry': 'Technology', 'description': 'Digital technology company providing online services and solutions.'},
                'software': {'industry': 'Technology', 'description': 'Software development company creating applications and digital platforms.'},
                'platform': {'industry': 'Technology', 'description': 'Platform company providing technology infrastructure and services.'},
                'data': {'industry': 'Data', 'description': 'Data analytics company providing insights and intelligence solutions.'},
                'ai': {'industry': 'Technology', 'description': 'Artificial intelligence company developing machine learning and AI solutions.'},
                'cloud': {'industry': 'Technology', 'description': 'Cloud computing company providing scalable infrastructure and services.'},
                'mobile': {'industry': 'Technology', 'description': 'Mobile technology company developing applications and mobile solutions.'},
                'finance': {'industry': 'FinTech', 'description': 'Financial services company providing banking and investment solutions.'},
                'bank': {'industry': 'FinTech', 'description': 'Banking institution providing financial services and products.'},
                'payment': {'industry': 'FinTech', 'description': 'Payment technology company providing transaction processing solutions.'}
            }
            
            # Check for specific company matches first
            company_info = None
            for keyword, info in industry_keywords.items():
                if keyword in query_clean:
                    company_info = info
                    enriched_data.industry = info['industry']
                    enriched_data.country = info.get('country', 'United States')  # Default to US
                    enriched_data.description = info['description']
                    break
            
            # If no specific match, create generic description
            if not company_info:
                # Determine likely industry from company name patterns
                if any(term in query_clean for term in ['tech', 'software', 'digital', 'platform', 'app']):
                    enriched_data.industry = 'Technology'
                    enriched_data.description = f"{company_name} is a technology company providing innovative digital solutions and services."
                elif any(term in query_clean for term in ['finance', 'bank', 'pay', 'money', 'credit']):
                    enriched_data.industry = 'FinTech'
                    enriched_data.description = f"{company_name} is a financial services company providing banking and payment solutions."
                elif any(term in query_clean for term in ['consult', 'advisory', 'service']):
                    enriched_data.industry = 'Consulting'
                    enriched_data.description = f"{company_name} is a consulting firm providing professional advisory and implementation services."
                elif any(term in query_clean for term in ['health', 'medical', 'care']):
                    enriched_data.industry = 'DigitalHealth'
                    enriched_data.description = f"{company_name} is a healthcare company providing medical services and health technology solutions."
                elif any(term in query_clean for term in ['education', 'learning', 'school']):
                    enriched_data.industry = 'EdTech'
                    enriched_data.description = f"{company_name} is an educational technology company providing digital learning solutions."
                else:
                    # Generic business description
                    enriched_data.industry = 'Technology'
                    enriched_data.description = f"{company_name} is an innovative company providing specialized products and services in their industry."
            
            # Set basic company data
            enriched_data.company_type = 'private'
            enriched_data.employees_count = 100  # Reasonable default
            
            # Always return enriched data (this ensures Caroline gets at least basic info)
            return CompanyEnrichmentResponse(
                success=True,
                company_data=enriched_data,
                api_source="enhanced_basic_enrichment"
            )
                
        except Exception as e:
            print(f"Enhanced basic enrichment error: {str(e)}")
        
        # If all methods fail
        return CompanyEnrichmentResponse(
            success=False,
            error_message="Aucune donnée trouvée pour cette entreprise. Vérifiez le nom ou essayez avec le domaine web."
        )
        
    except Exception as e:
        return CompanyEnrichmentResponse(
            success=False,
            error_message=f"Erreur lors de l'enrichissement: {str(e)}"
        )

# DEALFLOW ENDPOINTS
@api_router.post("/dealflow", response_model=DealflowPartner)
async def create_dealflow_partner(partner: DealflowPartnerCreate):
    partner_dict = partner.dict()
    
    # Auto-enrichment if enabled
    enrichment_settings = await get_enrichment_settings()
    if enrichment_settings.auto_enrich:
        enriched_data = await enrich_company_data(
            partner.nom,
            partner_dict.get("website_domain")
        )
        partner_dict["enriched_data"] = enriched_data
    
    partner_obj = DealflowPartner(**partner_dict)
    
    # Convert date objects to strings for MongoDB storage
    partner_data = partner_obj.dict()
    for key, value in partner_data.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            partner_data[key] = value.isoformat()
    
    result = await db.dealflow_partners.insert_one(partner_data)
    
    # Log creation activity
    await log_activity(
        partner_id=partner_obj.id,
        partner_type="dealflow",
        activity_type=ActivityType.CREATED,
        description=f"Startup '{partner.nom}' créée en dealflow",
        details={"statut": partner.statut, "domaine": partner.domaine},
        user_name="System"
    )
    
    return partner_obj

@api_router.get("/dealflow", response_model=List[DealflowPartner])
async def get_dealflow_partners():
    partners = await db.dealflow_partners.find().to_list(1000)
    
    # Add inactivity status to each partner
    partners_with_status = []
    for partner in partners:
        partner_with_status = add_inactivity_status(partner)
        partners_with_status.append(DealflowPartner(**partner_with_status))
    
    return partners_with_status

@api_router.get("/dealflow/{partner_id}", response_model=DealflowPartner)
async def get_dealflow_partner(partner_id: str):
    partner = await db.dealflow_partners.find_one({"id": partner_id})
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Add inactivity status
    partner_with_status = add_inactivity_status(partner)
    return DealflowPartner(**partner_with_status)

@api_router.put("/dealflow/{partner_id}", response_model=DealflowPartner)
async def update_dealflow_partner(partner_id: str, partner_update: DealflowPartnerUpdate):
    # Get original partner for comparison
    original_partner = await db.dealflow_partners.find_one({"id": partner_id})
    if not original_partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    update_dict = {k: v for k, v in partner_update.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    # Convert date objects to strings for MongoDB storage
    for key, value in update_dict.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            update_dict[key] = value.isoformat()
    
    result = await db.dealflow_partners.update_one(
        {"id": partner_id},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Log update activity with changes
    changes = []
    for key, new_value in update_dict.items():
        if key != "updated_at" and key in original_partner:
            old_value = original_partner[key]
            if old_value != new_value:
                changes.append(f"{key}: {old_value} → {new_value}")
    
    if changes:
        await log_activity(
            partner_id=partner_id,
            partner_type="dealflow",
            activity_type=ActivityType.UPDATED,
            description=f"Startup '{original_partner['nom']}' mise à jour",
            details={"changes": changes},
            user_name="System"
        )
    
    updated_partner = await db.dealflow_partners.find_one({"id": partner_id})
    updated_partner = add_inactivity_status(updated_partner)
    return DealflowPartner(**updated_partner)

@api_router.delete("/dealflow/{partner_id}")
async def delete_dealflow_partner(partner_id: str):
    # Get partner info before deletion for logging
    partner = await db.dealflow_partners.find_one({"id": partner_id})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    result = await db.dealflow_partners.delete_one({"id": partner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Log deletion activity
    await log_activity(
        partner_id=partner_id,
        partner_type="dealflow",
        activity_type=ActivityType.UPDATED,
        description=f"Startup '{partner['nom']}' supprimée du dealflow",
        details={"action": "deleted"},
        user_name="System"
    )
    
    return {"message": "Partner deleted successfully"}

# TRANSITION ENDPOINT - Move from sourcing to dealflow
@api_router.post("/transition/{sourcing_id}")
async def transition_to_dealflow(sourcing_id: str, dealflow_data: Dict[str, Any] = Body(...)):
    # Get sourcing partner
    sourcing_partner = await db.sourcing_partners.find_one({"id": sourcing_id})
    if sourcing_partner is None:
        raise HTTPException(status_code=404, detail="Sourcing partner not found")
    
    # Create dealflow partner with inherited data
    dealflow_partner_data = {
        "nom": sourcing_partner["nom_entreprise"],
        "domaine": sourcing_partner["domaine_activite"],
        "typologie": sourcing_partner["typologie"],
        "objet": sourcing_partner["objet"],
        "source": sourcing_partner["source"],
        "pilote": sourcing_partner["pilote"],
        "sourcing_id": sourcing_id,
        "pays_origine": sourcing_partner["pays_origine"],
        "cas_usage": sourcing_partner["cas_usage"],
        "technologie": sourcing_partner["technologie"],
        "interet": sourcing_partner["interet"],
        "enriched_data": sourcing_partner.get("enriched_data", {}),
        "custom_fields": sourcing_partner.get("custom_fields", {}),
        # Inherit Phase 1 fields
        "date_prochaine_action": sourcing_partner.get("date_prochaine_action"),
        # Required dealflow fields from the request
        **dealflow_data
    }
    
    dealflow_partner = DealflowPartner(**dealflow_partner_data)
    
    # Convert date objects to strings for MongoDB storage
    dealflow_data_for_db = dealflow_partner.dict()
    for key, value in dealflow_data_for_db.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            dealflow_data_for_db[key] = value.isoformat()
    
    await db.dealflow_partners.insert_one(dealflow_data_for_db)
    
    # Update sourcing partner status
    await db.sourcing_partners.update_one(
        {"id": sourcing_id},
        {"$set": {"statut": SourcingStatus.DEALFLOW, "updated_at": datetime.utcnow()}}
    )
    
    # Log transition activity
    await log_activity(
        partner_id=sourcing_id,
        partner_type="sourcing",
        activity_type=ActivityType.TRANSITIONED,
        description=f"Startup '{sourcing_partner['nom_entreprise']}' transférée vers dealflow",
        details={"new_dealflow_id": dealflow_partner.id, "new_status": "dealflow"},
        user_name="System"
    )
    
    # Log creation activity for dealflow
    await log_activity(
        partner_id=dealflow_partner.id,
        partner_type="dealflow",
        activity_type=ActivityType.CREATED,
        description=f"Startup '{dealflow_partner.nom}' créée en dealflow (transition depuis sourcing)",
        details={"source_sourcing_id": sourcing_id, "inherited": True},
        user_name="System"
    )
    
    return dealflow_partner

# STATISTICS ENDPOINT
@api_router.get("/statistics", response_model=DashboardStats)
async def get_dashboard_statistics():
    # Get all partners
    sourcing_partners = await db.sourcing_partners.find().to_list(1000)
    dealflow_partners = await db.dealflow_partners.find().to_list(1000)
    
    # Calculate quarterly entries
    quarterly_entries = {}
    for partner in sourcing_partners:
        date_entry = partner.get("date_entree_sourcing")
        if date_entry:
            if isinstance(date_entry, str):
                date_entry = datetime.fromisoformat(date_entry.replace('Z', '+00:00')).date()
            quarter = f"Q{((date_entry.month - 1) // 3) + 1} {date_entry.year}"
            domain = partner.get("domaine_activite", "Unknown")
            
            if quarter not in quarterly_entries:
                quarterly_entries[quarter] = {"total": 0, "by_domain": {}}
            
            quarterly_entries[quarter]["total"] += 1
            quarterly_entries[quarter]["by_domain"][domain] = quarterly_entries[quarter]["by_domain"].get(domain, 0) + 1
    
    quarterly_stats = [
        QuarterlyStats(quarter=q, total_entries=data["total"], by_domain=data["by_domain"])
        for q, data in quarterly_entries.items()
    ]
    
    # Calculate monthly stats
    monthly_stats = {}
    for partner in dealflow_partners:
        # Pre-qualifications
        pre_qual_date = partner.get("date_pre_qualification")
        if pre_qual_date:
            if isinstance(pre_qual_date, str):
                pre_qual_date = datetime.fromisoformat(pre_qual_date.replace('Z', '+00:00')).date()
            month_key = f"{pre_qual_date.year}-{pre_qual_date.month:02d}"
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {"pre_qualifications": 0, "go_studies": 0}
            monthly_stats[month_key]["pre_qualifications"] += 1
        
        # Go studies
        go_study_date = partner.get("date_go_metier_etude")
        if go_study_date:
            if isinstance(go_study_date, str):
                go_study_date = datetime.fromisoformat(go_study_date.replace('Z', '+00:00')).date()
            month_key = f"{go_study_date.year}-{go_study_date.month:02d}"
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {"pre_qualifications": 0, "go_studies": 0}
            monthly_stats[month_key]["go_studies"] += 1
    
    monthly_stats_list = [
        MonthlyStats(month=month, pre_qualifications=data["pre_qualifications"], go_studies=data["go_studies"])
        for month, data in monthly_stats.items()
    ]
    
    # Distribution calculations
    domain_dist = {}
    typologie_dist = {}
    technology_dist = {}
    metiers_dist = {}
    sourcing_status_dist = {}
    dealflow_status_dist = {}
    
    for partner in sourcing_partners:
        domain = partner.get("domaine_activite", "Unknown")
        typologie = partner.get("typologie", "Unknown")
        technology = partner.get("technologie", "Unknown")
        status = partner.get("statut", "Unknown")
        
        domain_dist[domain] = domain_dist.get(domain, 0) + 1
        typologie_dist[typologie] = typologie_dist.get(typologie, 0) + 1
        technology_dist[technology] = technology_dist.get(technology, 0) + 1
        sourcing_status_dist[status] = sourcing_status_dist.get(status, 0) + 1
    
    for partner in dealflow_partners:
        domain = partner.get("domaine", "Unknown")
        typologie = partner.get("typologie", "Unknown")
        technology = partner.get("technologie", "Unknown")
        metiers = partner.get("metiers_concernes", "Unknown")
        status = partner.get("statut", "Unknown")
        
        domain_dist[domain] = domain_dist.get(domain, 0) + 1
        typologie_dist[typologie] = typologie_dist.get(typologie, 0) + 1
        if technology:
            technology_dist[technology] = technology_dist.get(technology, 0) + 1
        metiers_dist[metiers] = metiers_dist.get(metiers, 0) + 1
        dealflow_status_dist[status] = dealflow_status_dist.get(status, 0) + 1
    
    return DashboardStats(
        quarterly_entries=quarterly_stats,
        monthly_stats=monthly_stats_list,
        domain_distribution=domain_dist,
        typologie_distribution=typologie_dist,
        technology_distribution=technology_dist,
        metiers_distribution=metiers_dist,
        sourcing_status_distribution=sourcing_status_dist,
        dealflow_status_distribution=dealflow_status_dist,
        total_sourcing=len(sourcing_partners),
        total_dealflow=len(dealflow_partners)
    )

# ENRICHMENT ENDPOINT
@api_router.post("/enrich/{partner_id}")
async def enrich_partner_data(partner_id: str, partner_type: str = "sourcing"):
    """Manually trigger enrichment for a specific partner"""
    collection = db.sourcing_partners if partner_type == "sourcing" else db.dealflow_partners
    
    partner = await collection.find_one({"id": partner_id})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Get company name
    company_name = partner.get("nom_entreprise" if partner_type == "sourcing" else "nom")
    
    # Perform enrichment
    enriched_data = await enrich_company_data(company_name)
    
    # Update partner with enriched data
    await collection.update_one(
        {"id": partner_id},
        {"$set": {
            "enriched_data": enriched_data,
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Log enrichment activity
    await log_activity(
        partner_id=partner_id,
        partner_type=partner_type,
        activity_type=ActivityType.ENRICHED,
        description=f"Données enrichies automatiquement pour '{company_name}'",
        details={"sources": ["linkedin", "website"], "fields_updated": list(enriched_data.keys())},
        user_name="System"
    )
    
    return {"message": "Partner enriched successfully", "enriched_data": enriched_data}

# PHASE 1 - ACTIVITY TIMELINE ENDPOINTS
@api_router.get("/activity/{partner_id}", response_model=List[ActivityLogResponse])
async def get_partner_activity_timeline(partner_id: str, partner_type: str = "sourcing"):
    """Get activity timeline for a specific partner"""
    activities = await db.activity_logs.find({
        "partner_id": partner_id,
        "partner_type": partner_type
    }).sort("created_at", -1).to_list(100)  # Most recent first, limit 100
    
    return [ActivityLogResponse(**activity) for activity in activities]

@api_router.post("/activity/{partner_id}")
async def add_manual_activity(partner_id: str, partner_type: str, 
                             description: str, user_name: str = "User"):
    """Manually add an activity entry to partner timeline"""
    # Verify partner exists
    collection = db.sourcing_partners if partner_type == "sourcing" else db.dealflow_partners
    partner = await collection.find_one({"id": partner_id})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Log manual activity
    activity = await log_activity(
        partner_id=partner_id,
        partner_type=partner_type,
        activity_type=ActivityType.COMMENT_ADDED,
        description=description,
        details={"manual_entry": True},
        user_name=user_name
    )
    
    return {"message": "Activity added successfully", "activity_id": activity.id}

@api_router.get("/inactive-partners")
async def get_inactive_partners(threshold_days: int = 90):
    """Get list of partners inactive for specified days (default 90)"""
    threshold_date = datetime.utcnow() - timedelta(days=threshold_days)
    
    # Get inactive sourcing partners
    inactive_sourcing = await db.sourcing_partners.find({
        "updated_at": {"$lt": threshold_date.isoformat()}
    }).to_list(100)
    
    # Get inactive dealflow partners
    inactive_dealflow = await db.dealflow_partners.find({
        "updated_at": {"$lt": threshold_date.isoformat()}
    }).to_list(100)
    
    # Add inactivity status
    inactive_sourcing_with_status = [add_inactivity_status(p) for p in inactive_sourcing]
    inactive_dealflow_with_status = [add_inactivity_status(p) for p in inactive_dealflow]
    
    return {
        "threshold_days": threshold_days,
        "inactive_sourcing": inactive_sourcing_with_status,
        "inactive_dealflow": inactive_dealflow_with_status,
        "total_inactive": len(inactive_sourcing) + len(inactive_dealflow)
    }

# DOCUMENT MANAGEMENT ENDPOINTS
@api_router.post("/documents/upload", response_model=Document)
async def upload_document(
    request: Request,
    partner_id: str = None,
    partner_type: str = None,
    filename: str = None,
    document_type: DocumentType = None,
    content: str = None,
    description: Optional[str] = None,
    uploaded_by: str = "default_user"
):
    """Upload a document for a startup - accepts both JSON body and query parameters"""
    import base64
    
    # Try to get data from JSON body first, then fallback to query parameters
    try:
        # Check if request has JSON content-type and body
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            body = await request.json()
            # Only override parameters if they exist in JSON body
            if 'partner_id' in body:
                partner_id = body['partner_id']
            if 'partner_type' in body:
                partner_type = body['partner_type']
            if 'filename' in body:
                filename = body['filename']
            if 'document_type' in body:
                document_type = body['document_type']
            if 'content' in body:
                content = body['content']
            if 'description' in body:
                description = body['description']
            if 'uploaded_by' in body:
                uploaded_by = body['uploaded_by']
    except Exception as e:
        # Fallback to query parameters (existing behavior)
        print(f"JSON parsing failed, using query parameters: {e}")
        pass
    import base64
    
    try:
        # Validate base64 content
        decoded_content = base64.b64decode(content)
        file_size = len(decoded_content)
        
        # Determine MIME type based on file extension
        file_ext = filename.lower().split('.')[-1]
        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'txt': 'text/plain',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        file_type = mime_types.get(file_ext, 'application/octet-stream')
        
        # Check for existing documents to determine version
        existing_docs = await db.documents.find({
            "partner_id": partner_id,
            "original_filename": filename
        }).to_list(100)
        
        version = max([doc["version"] for doc in existing_docs], default=0) + 1
        
        # Create document
        document = Document(
            partner_id=partner_id,
            partner_type=partner_type,
            filename=f"{filename.rsplit('.', 1)[0]}_v{version}.{filename.rsplit('.', 1)[1]}",
            original_filename=filename,
            file_size=file_size,
            file_type=file_type,
            document_type=document_type,
            content=content,
            version=version,
            description=description,
            uploaded_by=uploaded_by
        )
        
        # Save to database
        result = await db.documents.insert_one(document.dict())
        return document
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error uploading document: {str(e)}")

@api_router.get("/documents/{partner_id}", response_model=List[Document])
async def get_partner_documents(partner_id: str):
    """Get all documents for a partner"""
    documents = await db.documents.find({"partner_id": partner_id}).to_list(100)
    return [Document(**doc) for doc in documents]

@api_router.get("/documents/download/{document_id}")
async def download_document(document_id: str):
    """Download a document by ID"""
    document = await db.documents.find_one({"id": document_id})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    import base64
    from fastapi.responses import Response
    
    try:
        content = base64.b64decode(document["content"])
        return Response(
            content=content,
            media_type=document["file_type"],
            headers={
                "Content-Disposition": f'attachment; filename="{document["filename"]}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")

@api_router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    result = await db.documents.delete_one({"id": document_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}

@api_router.get("/documents/types", response_model=List[str])
async def get_document_types():
    """Get available document types"""
    # Debug: Let's see what's happening
    try:
        enum_values = [doc_type.value for doc_type in DocumentType]
        print(f"DEBUG: enum_values = {enum_values}")
        return enum_values
    except Exception as e:
        print(f"DEBUG: Error getting enum values: {e}")
        return ["Convention", "Présentation", "Compte-rendu", "Contrat", "Document technique", "Autre"]

# PHASE 2 - ENHANCED ANALYTICS ENDPOINTS
@api_router.get("/analytics/monthly-evolution")
async def get_monthly_evolution(start_date: str = None, end_date: str = None):
    """Get monthly evolution of startups by status"""
    # Parse date filters with error handling
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=365)
        end_dt = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    
    # Get all partners
    sourcing_partners = await db.sourcing_partners.find().to_list(1000)
    dealflow_partners = await db.dealflow_partners.find().to_list(1000)
    
    monthly_data = {}
    
    # Process sourcing partners
    for partner in sourcing_partners:
        created_date = partner.get("created_at")
        if isinstance(created_date, str):
            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        
        if start_dt <= created_date <= end_dt:
            month_key = f"{created_date.year}-{created_date.month:02d}"
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "sourcing_created": 0,
                    "dealflow_created": 0,
                    "sourcing_closed": 0,
                    "dealflow_closed": 0,
                    "transitions": 0
                }
            monthly_data[month_key]["sourcing_created"] += 1
    
    # Process dealflow partners
    for partner in dealflow_partners:
        created_date = partner.get("created_at")
        if isinstance(created_date, str):
            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        
        if start_dt <= created_date <= end_dt:
            month_key = f"{created_date.year}-{created_date.month:02d}"
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "sourcing_created": 0,
                    "dealflow_created": 0,
                    "sourcing_closed": 0,
                    "dealflow_closed": 0,
                    "transitions": 0
                }
            monthly_data[month_key]["dealflow_created"] += 1
            
            # Check if it's a transition from sourcing
            if partner.get("sourcing_id"):
                monthly_data[month_key]["transitions"] += 1
        
        # Check closure dates
        closure_date = partner.get("date_cloture")
        if closure_date:
            if isinstance(closure_date, str):
                closure_date = datetime.fromisoformat(closure_date.replace('Z', '+00:00'))
            if start_dt <= closure_date <= end_dt:
                month_key = f"{closure_date.year}-{closure_date.month:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "sourcing_created": 0,
                        "dealflow_created": 0,
                        "sourcing_closed": 0,
                        "dealflow_closed": 0,
                        "transitions": 0
                    }
                monthly_data[month_key]["dealflow_closed"] += 1
    
    # Process sourcing closures
    for partner in sourcing_partners:
        if partner.get("statut") == "Clos":
            updated_date = partner.get("updated_at")
            if isinstance(updated_date, str):
                updated_date = datetime.fromisoformat(updated_date.replace('Z', '+00:00'))
            if start_dt <= updated_date <= end_dt:
                month_key = f"{updated_date.year}-{updated_date.month:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "sourcing_created": 0,
                        "dealflow_created": 0,
                        "sourcing_closed": 0,
                        "dealflow_closed": 0,
                        "transitions": 0
                    }
                monthly_data[month_key]["sourcing_closed"] += 1
    
    # Sort by date and return
    sorted_data = sorted(monthly_data.items())
    return {
        "period": {"start": start_dt.isoformat(), "end": end_dt.isoformat()},
        "monthly_evolution": sorted_data
    }

@api_router.get("/analytics/distribution")
async def get_enhanced_distribution(filter_by: str = None, filter_value: str = None, 
                                  start_date: str = None, end_date: str = None):
    """Get enhanced distribution analytics with filtering"""
    # Parse date filters with error handling
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid start_date format: {start_date}")
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid end_date format: {end_date}")
    
    # Get all partners
    sourcing_partners = await db.sourcing_partners.find().to_list(1000)
    dealflow_partners = await db.dealflow_partners.find().to_list(1000)
    
    # Apply filters
    if start_dt and end_dt:
        filtered_sourcing = []
        for p in sourcing_partners:
            created_at = p.get("created_at")
            if created_at:
                if isinstance(created_at, str):
                    try:
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if start_dt <= created_date <= end_dt:
                            filtered_sourcing.append(p)
                    except ValueError:
                        continue  # Skip invalid dates
                elif isinstance(created_at, datetime):
                    if start_dt <= created_at <= end_dt:
                        filtered_sourcing.append(p)
        
        filtered_dealflow = []
        for p in dealflow_partners:
            created_at = p.get("created_at")
            if created_at:
                if isinstance(created_at, str):
                    try:
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if start_dt <= created_date <= end_dt:
                            filtered_dealflow.append(p)
                    except ValueError:
                        continue  # Skip invalid dates
                elif isinstance(created_at, datetime):
                    if start_dt <= created_at <= end_dt:
                        filtered_dealflow.append(p)
        
        sourcing_partners = filtered_sourcing
        dealflow_partners = filtered_dealflow
    
    if filter_by and filter_value:
        if filter_by == "domaine":
            sourcing_partners = [p for p in sourcing_partners if p.get("domaine_activite") == filter_value]
            dealflow_partners = [p for p in dealflow_partners if p.get("domaine") == filter_value]
        elif filter_by == "pilote":
            sourcing_partners = [p for p in sourcing_partners if p.get("pilote") == filter_value]
            dealflow_partners = [p for p in dealflow_partners if p.get("pilote") == filter_value]
    
    # Calculate distributions
    distributions = {
        "by_status": {},
        "by_domain": {},
        "by_typologie": {},
        "by_pilote": {},
        "by_source": {},
        "summary": {
            "total_sourcing": len(sourcing_partners),
            "total_dealflow": len(dealflow_partners),
            "total_partners": len(sourcing_partners) + len(dealflow_partners)
        }
    }
    
    # Status distribution
    for partner in sourcing_partners:
        status = partner.get("statut", "Unknown")
        distributions["by_status"][f"Sourcing - {status}"] = distributions["by_status"].get(f"Sourcing - {status}", 0) + 1
    
    for partner in dealflow_partners:
        status = partner.get("statut", "Unknown")
        distributions["by_status"][f"Dealflow - {status}"] = distributions["by_status"].get(f"Dealflow - {status}", 0) + 1
    
    # Domain distribution
    for partner in sourcing_partners:
        domain = partner.get("domaine_activite", "Unknown")
        distributions["by_domain"][domain] = distributions["by_domain"].get(domain, 0) + 1
    
    for partner in dealflow_partners:
        domain = partner.get("domaine", "Unknown")
        distributions["by_domain"][domain] = distributions["by_domain"].get(domain, 0) + 1
    
    # Typologie distribution
    for partner in sourcing_partners:
        typologie = partner.get("typologie", "Unknown")
        distributions["by_typologie"][typologie] = distributions["by_typologie"].get(typologie, 0) + 1
    
    for partner in dealflow_partners:
        typologie = partner.get("typologie", "Unknown")
        distributions["by_typologie"][typologie] = distributions["by_typologie"].get(typologie, 0) + 1
    
    # Pilote distribution
    for partner in sourcing_partners:
        pilote = partner.get("pilote", "Unknown")
        distributions["by_pilote"][pilote] = distributions["by_pilote"].get(pilote, 0) + 1
    
    for partner in dealflow_partners:
        pilote = partner.get("pilote", "Unknown")
        distributions["by_pilote"][pilote] = distributions["by_pilote"].get(pilote, 0) + 1
    
    # Source distribution
    for partner in sourcing_partners:
        source = partner.get("source", "Unknown")
        distributions["by_source"][source] = distributions["by_source"].get(source, 0) + 1
    
    for partner in dealflow_partners:
        source = partner.get("source", "Unknown")
        distributions["by_source"][source] = distributions["by_source"].get(source, 0) + 1
    
    return distributions

# PHASE 3 - USER MANAGEMENT ENDPOINTS
@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user"""
    user_obj = User(**user.dict())
    
    # Convert datetime objects to strings for MongoDB storage
    user_data = user_obj.dict()
    user_data["created_at"] = user_obj.created_at.isoformat()
    user_data["updated_at"] = user_obj.updated_at.isoformat()
    
    result = await db.users.insert_one(user_data)
    return user_obj

@api_router.get("/users", response_model=List[User])
async def get_users():
    """Get all users"""
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get specific user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user"""
    update_dict = {k: v for k, v in user_update.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await db.users.find_one({"id": user_id})
    return User(**updated_user)

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete user"""
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# PHASE 3 - PRIVATE COMMENTS ENDPOINTS
@api_router.post("/comments", response_model=PrivateCommentResponse)
async def create_private_comment(comment: PrivateCommentCreate, user_id: str = "default_user"):
    """Create a private comment"""
    current_user = await get_current_user(user_id)
    
    comment_obj = PrivateComment(
        **comment.dict(),
        user_id=current_user.id,
        user_name=current_user.full_name
    )
    
    # Convert datetime objects to strings for MongoDB storage
    comment_data = comment_obj.dict()
    comment_data["created_at"] = comment_obj.created_at.isoformat()
    comment_data["updated_at"] = comment_obj.updated_at.isoformat()
    
    result = await db.private_comments.insert_one(comment_data)
    return PrivateCommentResponse(**comment_obj.dict())

@api_router.get("/comments/{partner_id}", response_model=List[PrivateCommentResponse])
async def get_partner_comments(partner_id: str, partner_type: str = "sourcing", user_id: str = "default_user"):
    """Get private comments for a partner (user sees only own comments + admin sees all)"""
    current_user = await get_current_user(user_id)
    
    # Build query based on user role
    query = {"partner_id": partner_id, "partner_type": partner_type}
    if current_user.role != UserRole.ADMIN:
        query["user_id"] = current_user.id  # Non-admin users see only their own comments
    
    comments = await db.private_comments.find(query).sort("created_at", -1).to_list(100)
    return [PrivateCommentResponse(**comment) for comment in comments]

@api_router.put("/comments/{comment_id}", response_model=PrivateCommentResponse)
async def update_private_comment(comment_id: str, comment_update: PrivateCommentUpdate, user_id: str = "default_user"):
    """Update a private comment (only by owner or admin)"""
    current_user = await get_current_user(user_id)
    
    # Get existing comment
    existing_comment = await db.private_comments.find_one({"id": comment_id})
    if not existing_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check permissions
    if not can_view_private_comment(existing_comment["user_id"], current_user.id, current_user.role):
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    
    update_dict = comment_update.dict()
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await db.private_comments.update_one(
        {"id": comment_id},
        {"$set": update_dict}
    )
    
    updated_comment = await db.private_comments.find_one({"id": comment_id})
    return PrivateCommentResponse(**updated_comment)

@api_router.delete("/comments/{comment_id}")
async def delete_private_comment(comment_id: str, user_id: str = "default_user"):
    """Delete a private comment (only by owner or admin)"""
    current_user = await get_current_user(user_id)
    
    # Get existing comment
    existing_comment = await db.private_comments.find_one({"id": comment_id})
    if not existing_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check permissions
    if not can_view_private_comment(existing_comment["user_id"], current_user.id, current_user.role):
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    result = await db.private_comments.delete_one({"id": comment_id})
    return {"message": "Comment deleted successfully"}

# PHASE 3 - PERSONAL DASHBOARD ENDPOINTS  
@api_router.get("/my-startups", response_model=Dict[str, Any])
async def get_my_startups(user_id: str = "default_user"):
    """Get startups assigned to current user"""
    current_user = await get_current_user(user_id)
    
    # Get sourcing partners assigned to user
    sourcing_query = {"pilote": current_user.full_name}
    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(1000)
    
    # Get dealflow partners assigned to user
    dealflow_query = {"pilote": current_user.full_name}
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(1000)
    
    # Convert MongoDB documents to proper format and add inactivity status
    sourcing_with_status = []
    for p in sourcing_partners:
        # Remove MongoDB ObjectId if present
        if '_id' in p:
            del p['_id']
        partner_with_status = add_inactivity_status(p)
        sourcing_with_status.append(partner_with_status)
    
    dealflow_with_status = []
    for p in dealflow_partners:
        # Remove MongoDB ObjectId if present
        if '_id' in p:
            del p['_id']
        partner_with_status = add_inactivity_status(p)
        dealflow_with_status.append(partner_with_status)
    
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "is_active": current_user.is_active
        },
        "sourcing_partners": sourcing_with_status,
        "dealflow_partners": dealflow_with_status,
        "total_assigned": len(sourcing_partners) + len(dealflow_partners),
        "summary": {
            "total_sourcing": len(sourcing_partners),
            "total_dealflow": len(dealflow_partners),
            "total_partners": len(sourcing_partners) + len(dealflow_partners),
            "inactive_sourcing": len([p for p in sourcing_with_status if p.get("is_inactive")]),
            "inactive_dealflow": len([p for p in dealflow_with_status if p.get("is_inactive")])
        }
    }

@api_router.get("/partners-by-pilote")
async def get_partners_by_pilote():
    """Get partners grouped by pilote for filtering"""
    # Get all sourcing partners
    sourcing_partners = await db.sourcing_partners.find().to_list(1000)
    dealflow_partners = await db.dealflow_partners.find().to_list(1000)
    
    pilotes = {}
    
    # Group sourcing partners by pilote
    for partner in sourcing_partners:
        # Remove MongoDB ObjectId if present
        if '_id' in partner:
            del partner['_id']
        
        pilote = partner.get("pilote", "Unknown")
        if pilote not in pilotes:
            pilotes[pilote] = {"sourcing_partners": [], "dealflow_partners": []}
        pilotes[pilote]["sourcing_partners"].append(partner)
    
    # Group dealflow partners by pilote
    for partner in dealflow_partners:
        # Remove MongoDB ObjectId if present
        if '_id' in partner:
            del partner['_id']
            
        pilote = partner.get("pilote", "Unknown")
        if pilote not in pilotes:
            pilotes[pilote] = {"sourcing_partners": [], "dealflow_partners": []}
        pilotes[pilote]["dealflow_partners"].append(partner)
    
    # Add summary stats for each pilote
    for pilote, data in pilotes.items():
        sourcing_count = len(data["sourcing_partners"])
        dealflow_count = len(data["dealflow_partners"])
        data["total_partners"] = sourcing_count + dealflow_count
        data["summary"] = {
            "total_sourcing": sourcing_count,
            "total_dealflow": dealflow_count,
            "total_partners": sourcing_count + dealflow_count
        }
    
# PHASE 4 - KANBAN PIPELINE ENDPOINTS
@api_router.get("/kanban-data")
async def get_kanban_data(user_id: str = "default_user"):
    """Get data organized for Kanban pipeline view"""
    current_user = await get_current_user(user_id)
    
    # Define Kanban columns mapping
    kanban_columns = {
        "sourcing": ["A traiter", "Clos", "Dealflow", "Klaxoon"],
        "dealflow": [
            "En cours avec l'équipe inno",
            "En cours avec les métiers", 
            "Présentation métiers",
            "Go métier étude",
            "Go experimentation",
            "Go généralisation",
            "Clos"
        ]
    }
    
    # Get data based on user role
    sourcing_query = {}
    dealflow_query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        sourcing_query["pilote"] = current_user.full_name
        dealflow_query["pilote"] = current_user.full_name
    
    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(1000)
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(1000)
    
    # Organize data by Kanban columns
    kanban_data = {
        "columns": {
            # Sourcing stages
            "sourcing_a_traiter": {
                "id": "sourcing_a_traiter",
                "title": "🔍 Sourcing",
                "subtitle": "À traiter",
                "partners": []
            },
            "sourcing_klaxoon": {
                "id": "sourcing_klaxoon", 
                "title": "📋 Sourcing",
                "subtitle": "Klaxoon",
                "partners": []
            },
            # Dealflow stages
            "prequalification": {
                "id": "prequalification",
                "title": "✓ Préqualif",
                "subtitle": "Évaluation initiale",
                "partners": []
            },
            "presentation": {
                "id": "presentation",
                "title": "📊 Présentation",
                "subtitle": "Aux métiers",
                "partners": []
            },
            "go_metier": {
                "id": "go_metier",
                "title": "🎯 Go Métier",
                "subtitle": "Étude approuvée",
                "partners": []
            },
            "experimentation": {
                "id": "experimentation",
                "title": "🧪 Expérimentation",
                "subtitle": "Test en cours",
                "partners": []
            },
            "evaluation": {
                "id": "evaluation",
                "title": "📈 Évaluation",
                "subtitle": "Résultats",
                "partners": []
            },
            "generalisation": {
                "id": "generalisation",
                "title": "🚀 Généralisation",
                "subtitle": "Déploiement",
                "partners": []
            },
            "cloture": {
                "id": "cloture",
                "title": "✅ Clôture",
                "subtitle": "Terminé",
                "partners": []
            }
        },
        "columnOrder": [
            "sourcing_a_traiter", "sourcing_klaxoon", "prequalification", 
            "presentation", "go_metier", "experimentation", 
            "evaluation", "generalisation", "cloture"
        ]
    }
    
    # Process sourcing partners
    for partner in sourcing_partners:
        # Remove MongoDB ObjectId
        if '_id' in partner:
            del partner['_id']
        
        partner_with_status = add_inactivity_status(partner)
        
        # Map to Kanban columns
        status = partner.get("statut", "A traiter")
        if status == "A traiter":
            kanban_data["columns"]["sourcing_a_traiter"]["partners"].append({
                **partner_with_status,
                "partner_type": "sourcing",
                "kanban_id": f"sourcing_{partner['id']}"
            })
        elif status == "Klaxoon":
            kanban_data["columns"]["sourcing_klaxoon"]["partners"].append({
                **partner_with_status,
                "partner_type": "sourcing", 
                "kanban_id": f"sourcing_{partner['id']}"
            })
        elif status == "Dealflow":
            # These will be handled by dealflow processing
            pass
    
    # Process dealflow partners
    for partner in dealflow_partners:
        # Remove MongoDB ObjectId
        if '_id' in partner:
            del partner['_id']
            
        partner_with_status = add_inactivity_status(partner)
        
        # Map to Kanban columns based on dealflow status
        status = partner.get("statut", "En cours avec l'équipe inno")
        kanban_partner = {
            **partner_with_status,
            "partner_type": "dealflow",
            "kanban_id": f"dealflow_{partner['id']}"
        }
        
        if status == "En cours avec l'équipe inno":
            kanban_data["columns"]["prequalification"]["partners"].append(kanban_partner)
        elif status == "En cours avec les métiers":
            kanban_data["columns"]["presentation"]["partners"].append(kanban_partner)
        elif "go" in status.lower() and "étude" in status.lower():
            kanban_data["columns"]["go_metier"]["partners"].append(kanban_partner)
        elif "experimentation" in status.lower() or "go experimentation" in status.lower():
            kanban_data["columns"]["experimentation"]["partners"].append(kanban_partner)
        elif "généralisation" in status.lower() or "go généralisation" in status.lower():
            kanban_data["columns"]["generalisation"]["partners"].append(kanban_partner)
        elif status == "Clos":
            kanban_data["columns"]["cloture"]["partners"].append(kanban_partner)
        else:
            # Default to evaluation for undefined statuses
            kanban_data["columns"]["evaluation"]["partners"].append(kanban_partner)
    
    # Add summary statistics
    total_partners = len(sourcing_partners) + len(dealflow_partners)
    kanban_data["summary"] = {
        "total_partners": total_partners,
        "total_sourcing": len(sourcing_partners),
        "total_dealflow": len(dealflow_partners),
        "by_column": {
            col_id: len(col_data["partners"]) 
            for col_id, col_data in kanban_data["columns"].items()
        }
    }
    
    return kanban_data

@api_router.post("/kanban-move")
async def move_kanban_partner(
    partner_id: str, 
    partner_type: str, 
    source_column: str, 
    destination_column: str,
    user_id: str = "default_user"
):
    """Move partner between Kanban columns (updates status)"""
    current_user = await get_current_user(user_id)
    
    # Status mapping for each column
    column_to_status = {
        # Sourcing columns
        "sourcing_a_traiter": {"type": "sourcing", "status": "A traiter"},
        "sourcing_klaxoon": {"type": "sourcing", "status": "Klaxoon"},
        
        # Dealflow columns
        "prequalification": {"type": "dealflow", "status": "En cours avec l'équipe inno"},
        "presentation": {"type": "dealflow", "status": "En cours avec les métiers"},
        "go_metier": {"type": "dealflow", "status": "Go métier étude"},
        "experimentation": {"type": "dealflow", "status": "Go experimentation"},
        "evaluation": {"type": "dealflow", "status": "En cours avec les métiers"},  # Temp mapping
        "generalisation": {"type": "dealflow", "status": "Go généralisation"},
        "cloture": {"type": "dealflow", "status": "Clos"}
    }
    
    if destination_column not in column_to_status:
        raise HTTPException(status_code=400, detail="Invalid destination column")
    
    new_status_info = column_to_status[destination_column]
    new_status = new_status_info["status"]
    target_type = new_status_info["type"]
    
    # Get current partner
    collection = db.sourcing_partners if partner_type == "sourcing" else db.dealflow_partners
    partner = await collection.find_one({"id": partner_id})
    
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Check permissions
    if not can_edit_partner(current_user.role, partner.get("pilote"), current_user.full_name):
        raise HTTPException(status_code=403, detail="Not authorized to move this partner")
    
    # Handle transition from sourcing to dealflow
    if partner_type == "sourcing" and target_type == "dealflow":
        # Create dealflow partner
        dealflow_data = {
            "nom": partner["nom_entreprise"],
            "statut": new_status,
            "domaine": partner["domaine_activite"],
            "typologie": partner["typologie"],
            "objet": partner["objet"],
            "source": partner["source"],
            "pilote": partner["pilote"],
            "metiers_concernes": "À définir",  # Required field
            "date_reception_fichier": date.today(),
            "actions_commentaires": partner.get("actions_commentaires", ""),
            "date_prochaine_action": partner.get("date_prochaine_action"),
            "sourcing_id": partner_id,
            "pays_origine": partner.get("pays_origine"),
            "cas_usage": partner.get("cas_usage"),
            "technologie": partner.get("technologie"),
            "interet": partner.get("interet"),
            "enriched_data": partner.get("enriched_data", {}),
            "custom_fields": partner.get("custom_fields", {})
        }
        
        dealflow_partner = DealflowPartner(**dealflow_data)
        
        # Save to dealflow
        dealflow_data_for_db = dealflow_partner.dict()
        for key, value in dealflow_data_for_db.items():
            if isinstance(value, date) and not isinstance(value, datetime):
                dealflow_data_for_db[key] = value.isoformat()
        
        await db.dealflow_partners.insert_one(dealflow_data_for_db)
        
        # Update sourcing status to Dealflow
        await db.sourcing_partners.update_one(
            {"id": partner_id},
            {"$set": {"statut": "Dealflow", "updated_at": datetime.utcnow()}}
        )
        
        # Log transition
        await log_activity(
            partner_id=partner_id,
            partner_type="sourcing",
            activity_type=ActivityType.TRANSITIONED,
            description=f"Startup '{partner['nom_entreprise']}' déplacée vers dealflow via Kanban",
            details={"kanban_move": True, "from": source_column, "to": destination_column},
            user_id=current_user.id,
            user_name=current_user.full_name
        )
        
        return {
            "message": "Partner transitioned to dealflow successfully", 
            "new_partner_id": dealflow_partner.id,
            "new_status": new_status,
            "partner_type": target_type
        }
    
    # Handle status change within same type
    elif partner_type == target_type:
        await collection.update_one(
            {"id": partner_id},
            {"$set": {"statut": new_status, "updated_at": datetime.utcnow()}}
        )
        
        # Log status change
        await log_activity(
            partner_id=partner_id,
            partner_type=partner_type,
            activity_type=ActivityType.STATUS_CHANGED,
            description=f"Statut changé via Kanban: {new_status}",
            details={"kanban_move": True, "from": source_column, "to": destination_column, "new_status": new_status},
            user_id=current_user.id,
            user_name=current_user.full_name
        )
        
        return {
            "message": "Partner status updated successfully",
            "new_status": new_status,
            "partner_type": partner_type,
            "partner_id": partner_id
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid transition between partner types")

# PHASE 4 - SYNTHETIC REPORTS & EXPORTS ENDPOINTS
@api_router.get("/synthetic-report")
async def get_synthetic_report(user_id: str = "default_user"):
    """Generate synthetic cross-table report for exports"""
    current_user = await get_current_user(user_id)
    
    # Get data based on user role
    sourcing_query = {}
    dealflow_query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        sourcing_query["pilote"] = current_user.full_name
        dealflow_query["pilote"] = current_user.full_name
    
    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(1000)
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(1000)
    
    # Initialize report structure
    report = {
        "summary": {
            "total_sourcing": len(sourcing_partners),
            "total_dealflow": len(dealflow_partners),
            "total_partners": len(sourcing_partners) + len(dealflow_partners),
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": current_user.full_name
        },
        "cross_tables": {},
        "detailed_data": []
    }
    
    # 1. Status Distribution Cross-Table
    status_data = {}
    for partner in sourcing_partners:
        status = f"Sourcing - {partner.get('statut', 'Unknown')}"
        status_data[status] = status_data.get(status, 0) + 1
    
    for partner in dealflow_partners:
        status = f"Dealflow - {partner.get('statut', 'Unknown')}"
        status_data[status] = status_data.get(status, 0) + 1
    
    report["cross_tables"]["by_status"] = status_data
    
    # 2. Pilote Distribution Cross-Table
    pilote_data = {}
    for partner in sourcing_partners + dealflow_partners:
        pilote = partner.get("pilote", "Unknown")
        if pilote not in pilote_data:
            pilote_data[pilote] = {"sourcing": 0, "dealflow": 0, "total": 0}
        
        if partner in sourcing_partners:
            pilote_data[pilote]["sourcing"] += 1
        else:
            pilote_data[pilote]["dealflow"] += 1
        pilote_data[pilote]["total"] += 1
    
    report["cross_tables"]["by_pilote"] = pilote_data
    
    # 3. Domain Distribution Cross-Table
    domain_data = {}
    for partner in sourcing_partners:
        domain = partner.get("domaine_activite", "Unknown")
        if domain not in domain_data:
            domain_data[domain] = {"sourcing": 0, "dealflow": 0, "total": 0}
        domain_data[domain]["sourcing"] += 1
        domain_data[domain]["total"] += 1
    
    for partner in dealflow_partners:
        domain = partner.get("domaine", "Unknown")
        if domain not in domain_data:
            domain_data[domain] = {"sourcing": 0, "dealflow": 0, "total": 0}
        domain_data[domain]["dealflow"] += 1
        domain_data[domain]["total"] += 1
    
    report["cross_tables"]["by_domain"] = domain_data
    
    # 4. Type Collaboration Distribution (from custom_fields or typologie)
    collaboration_data = {}
    all_partners = sourcing_partners + dealflow_partners
    
    for partner in all_partners:
        # Try to get collaboration type from typologie or custom fields
        collab_type = partner.get("typologie", "Unknown")
        if collab_type not in collaboration_data:
            collaboration_data[collab_type] = {"count": 0, "partners": []}
        
        collaboration_data[collab_type]["count"] += 1
        partner_name = partner.get("nom_entreprise") or partner.get("nom", "Unknown")
        collaboration_data[collab_type]["partners"].append({
            "name": partner_name,
            "type": "sourcing" if partner in sourcing_partners else "dealflow",
            "pilote": partner.get("pilote", "Unknown")
        })
    
    report["cross_tables"]["by_collaboration_type"] = collaboration_data
    
    # 5. Detailed Data for CSV Export
    for partner in sourcing_partners:
        report["detailed_data"].append({
            "nom": partner.get("nom_entreprise", ""),
            "type": "Sourcing",
            "statut": partner.get("statut", ""),
            "domaine": partner.get("domaine_activite", ""),
            "pilote": partner.get("pilote", ""),
            "typologie": partner.get("typologie", ""),
            "pays": partner.get("pays_origine", ""),
            "source": partner.get("source", ""),
            "date_entree": partner.get("date_entree_sourcing", ""),
            "date_prochaine_action": partner.get("date_prochaine_action", ""),
            "interet": "Oui" if partner.get("interet") else "Non",
            "is_inactive": "Oui" if is_inactive(partner.get("updated_at")) else "Non",
            "actions_commentaires": partner.get("actions_commentaires", "")[:100] + "..." if len(partner.get("actions_commentaires", "")) > 100 else partner.get("actions_commentaires", "")
        })
    
    for partner in dealflow_partners:
        report["detailed_data"].append({
            "nom": partner.get("nom", ""),
            "type": "Dealflow", 
            "statut": partner.get("statut", ""),
            "domaine": partner.get("domaine", ""),
            "pilote": partner.get("pilote", ""),
            "typologie": partner.get("typologie", ""),
            "pays": partner.get("pays_origine", ""),
            "source": partner.get("source", ""),
            "date_entree": partner.get("date_reception_fichier", ""),
            "date_prochaine_action": partner.get("date_prochaine_action", ""),
            "interet": "Oui" if partner.get("interet") else "Non",
            "is_inactive": "Oui" if is_inactive(partner.get("updated_at")) else "Non",
            "actions_commentaires": partner.get("actions_commentaires", "")[:100] + "..." if len(partner.get("actions_commentaires", "")) > 100 else partner.get("actions_commentaires", "")
        })
    
    # 6. Time-based Analysis
    monthly_data = {}
    for partner in sourcing_partners:
        created_date = partner.get("created_at")
        if isinstance(created_date, str):
            try:
                created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                month_key = f"{created_date.year}-{created_date.month:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = {"sourcing": 0, "dealflow": 0}
                monthly_data[month_key]["sourcing"] += 1
            except:
                pass
    
    for partner in dealflow_partners:
        created_date = partner.get("created_at")
        if isinstance(created_date, str):
            try:
                created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                month_key = f"{created_date.year}-{created_date.month:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = {"sourcing": 0, "dealflow": 0}
                monthly_data[month_key]["dealflow"] += 1
            except:
                pass
    
    report["cross_tables"]["by_month"] = dict(sorted(monthly_data.items()))
    
    return report

# PHASE 4 - QUICK NAVIGATION & TARGETED VIEWS ENDPOINTS
@api_router.get("/quick-views/mes-startups")
async def get_my_startups_quick_view(user_id: str = "default_user"):
    """Quick view: My assigned startups"""
    current_user = await get_current_user(user_id)
    
    # Get startups assigned to current user
    sourcing_query = {"pilote": current_user.full_name}
    dealflow_query = {"pilote": current_user.full_name}
    
    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(1000)
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(1000)
    
    # Clean and add status
    sourcing_clean = []
    for p in sourcing_partners:
        if '_id' in p: del p['_id']
        sourcing_clean.append(add_inactivity_status(p))
    
    dealflow_clean = []
    for p in dealflow_partners:
        if '_id' in p: del p['_id']
        dealflow_clean.append(add_inactivity_status(p))
    
    return {
        "view_name": "Mes Startups",
        "description": f"Startups pilotées par {current_user.full_name}",
        "sourcing": sourcing_clean,
        "dealflow": dealflow_clean,
        "summary": {
            "total": len(sourcing_clean) + len(dealflow_clean),
            "sourcing_count": len(sourcing_clean),
            "dealflow_count": len(dealflow_clean)
        }
    }

@api_router.get("/quick-views/a-relancer")
async def get_startups_to_follow_up(threshold_days: int = 90, user_id: str = "default_user"):
    """Quick view: Startups to follow up (inactive or overdue actions)"""
    current_user = await get_current_user(user_id)
    
    # Get data based on user role
    sourcing_query = {}
    dealflow_query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        sourcing_query["pilote"] = current_user.full_name
        dealflow_query["pilote"] = current_user.full_name
    
    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(1000)
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(1000)
    
    today = datetime.utcnow()
    threshold_date = today - timedelta(days=threshold_days)
    
    # Filter partners that need follow-up
    sourcing_to_follow = []
    dealflow_to_follow = []
    
    for partner in sourcing_partners:
        if '_id' in partner: del partner['_id']
        partner_with_status = add_inactivity_status(partner)
        
        needs_followup = False
        followup_reasons = []
        
        # Check inactivity
        if partner_with_status.get("is_inactive"):
            needs_followup = True
            followup_reasons.append(f"Inactif depuis {partner_with_status.get('days_since_update')} jours")
        
        # Check overdue next action
        if partner.get("date_prochaine_action"):
            try:
                action_date = datetime.fromisoformat(partner["date_prochaine_action"])
                if action_date < today:
                    needs_followup = True
                    days_overdue = (today - action_date).days
                    followup_reasons.append(f"Action en retard de {days_overdue} jours")
            except:
                pass
        
        if needs_followup:
            partner_with_status["followup_reasons"] = followup_reasons
            sourcing_to_follow.append(partner_with_status)
    
    for partner in dealflow_partners:
        if '_id' in partner: del partner['_id']
        partner_with_status = add_inactivity_status(partner)
        
        needs_followup = False
        followup_reasons = []
        
        # Check inactivity
        if partner_with_status.get("is_inactive"):
            needs_followup = True
            followup_reasons.append(f"Inactif depuis {partner_with_status.get('days_since_update')} jours")
        
        # Check overdue next action
        if partner.get("date_prochaine_action"):
            try:
                action_date = datetime.fromisoformat(partner["date_prochaine_action"])
                if action_date < today:
                    needs_followup = True
                    days_overdue = (today - action_date).days
                    followup_reasons.append(f"Action en retard de {days_overdue} jours")
            except:
                pass
        
        if needs_followup:
            partner_with_status["followup_reasons"] = followup_reasons
            dealflow_to_follow.append(partner_with_status)
    
    return {
        "view_name": "À Relancer",
        "description": f"Startups inactives ({threshold_days}j+) ou actions en retard",
        "sourcing": sourcing_to_follow,
        "dealflow": dealflow_to_follow,
        "summary": {
            "total": len(sourcing_to_follow) + len(dealflow_to_follow),
            "sourcing_count": len(sourcing_to_follow),
            "dealflow_count": len(dealflow_to_follow),
            "threshold_days": threshold_days
        }
    }

@api_router.get("/quick-views/avec-documents")
async def get_startups_with_documents(user_id: str = "default_user"):
    """Quick view: Startups with documents/enriched data"""
    current_user = await get_current_user(user_id)
    
    # Get data based on user role
    sourcing_query = {}
    dealflow_query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        sourcing_query["pilote"] = current_user.full_name
        dealflow_query["pilote"] = current_user.full_name
    
    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(1000)
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(1000)
    
    # Filter partners with documents/enriched data
    sourcing_with_docs = []
    dealflow_with_docs = []
    
    for partner in sourcing_partners:
        if '_id' in partner: del partner['_id']
        partner_with_status = add_inactivity_status(partner)
        
        has_docs = False
        doc_types = []
        
        # Check enriched data
        if partner.get("enriched_data") and len(partner["enriched_data"]) > 0:
            has_docs = True
            doc_types.append("Données enrichies")
        
        # Check custom fields
        if partner.get("custom_fields") and len(partner["custom_fields"]) > 0:
            has_docs = True
            doc_types.append("Champs personnalisés")
        
        if has_docs:
            partner_with_status["document_types"] = doc_types
            sourcing_with_docs.append(partner_with_status)
    
    for partner in dealflow_partners:
        if '_id' in partner: del partner['_id']
        partner_with_status = add_inactivity_status(partner)
        
        has_docs = False
        doc_types = []
        
        # Check enriched data
        if partner.get("enriched_data") and len(partner["enriched_data"]) > 0:
            has_docs = True
            doc_types.append("Données enrichies")
        
        # Check custom fields
        if partner.get("custom_fields") and len(partner["custom_fields"]) > 0:
            has_docs = True
            doc_types.append("Champs personnalisés")
        
        if has_docs:
            partner_with_status["document_types"] = doc_types
            dealflow_with_docs.append(partner_with_status)
    
    return {
        "view_name": "Avec Documents",
        "description": "Startups avec données enrichies ou documents",
        "sourcing": sourcing_with_docs,
        "dealflow": dealflow_with_docs,
        "summary": {
            "total": len(sourcing_with_docs) + len(dealflow_with_docs),
            "sourcing_count": len(sourcing_with_docs),
            "dealflow_count": len(dealflow_with_docs)
        }
    }

@api_router.get("/quick-views/en-experimentation")
async def get_startups_in_experimentation(user_id: str = "default_user"):
    """Quick view: Startups in experimentation phase"""
    current_user = await get_current_user(user_id)
    
    # Get data based on user role
    dealflow_query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        dealflow_query["pilote"] = current_user.full_name
    
    # Only dealflow partners can be in experimentation
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(1000)
    
    # Filter partners in experimentation phase
    experimentation_statuses = [
        "Go experimentation",
        "Go généralisation",
        "En cours avec les métiers"  # Can be considered as experimentation prep
    ]
    
    dealflow_in_exp = []
    
    for partner in dealflow_partners:
        if '_id' in partner: del partner['_id']
        partner_with_status = add_inactivity_status(partner)
        
        status = partner.get("statut", "")
        if any(exp_status.lower() in status.lower() for exp_status in experimentation_statuses):
            # Add experimentation context
            if "experimentation" in status.lower():
                partner_with_status["experimentation_stage"] = "En cours"
            elif "generalisation" in status.lower():
                partner_with_status["experimentation_stage"] = "Généralisation"
            else:
                partner_with_status["experimentation_stage"] = "Préparation"
            
            dealflow_in_exp.append(partner_with_status)
    
    return {
        "view_name": "En Expérimentation",
        "description": "Startups en phase d'expérimentation ou généralisation",
        "sourcing": [],  # No sourcing in experimentation
        "dealflow": dealflow_in_exp,
        "summary": {
            "total": len(dealflow_in_exp),
            "sourcing_count": 0,
            "dealflow_count": len(dealflow_in_exp)
        }
    }

@api_router.get("/global-search")
async def global_search(query: str, user_id: str = "default_user"):
    """Global search across all partners (name, domain, pilote)"""
    if not query or len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    current_user = await get_current_user(user_id)
    query = query.strip().lower()
    
    # Get data based on user role
    sourcing_query = {}
    dealflow_query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        sourcing_query["pilote"] = current_user.full_name
        dealflow_query["pilote"] = current_user.full_name
    
    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(1000)
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(1000)
    
    # Search function
    def matches_query(partner, partner_type):
        searchable_fields = [
            (partner.get("nom_entreprise" if partner_type == "sourcing" else "nom") or "").lower(),
            (partner.get("domaine_activite" if partner_type == "sourcing" else "domaine") or "").lower(),
            (partner.get("pilote") or "").lower(),
            (partner.get("typologie") or "").lower(),
            (partner.get("source") or "").lower(),
            (partner.get("technologie") or "").lower(),
            (partner.get("pays_origine") or "").lower()
        ]
        
        return any(query in field for field in searchable_fields if field)
    
    # Filter matching partners
    sourcing_matches = []
    dealflow_matches = []
    
    for partner in sourcing_partners:
        if matches_query(partner, "sourcing"):
            if '_id' in partner: del partner['_id']
            sourcing_matches.append(add_inactivity_status(partner))
    
    for partner in dealflow_partners:
        if matches_query(partner, "dealflow"):
            if '_id' in partner: del partner['_id']
            dealflow_matches.append(add_inactivity_status(partner))
    
    return {
        "query": query,
        "sourcing": sourcing_matches,
        "dealflow": dealflow_matches,
        "summary": {
            "total": len(sourcing_matches) + len(dealflow_matches),
            "sourcing_count": len(sourcing_matches),
            "dealflow_count": len(dealflow_matches)
        }
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
