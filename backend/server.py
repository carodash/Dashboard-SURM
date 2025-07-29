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
from datetime import datetime, date
from enum import Enum
import httpx
from bs4 import BeautifulSoup
import re
import json


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

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

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

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
    editable_by_roles: List[UserRole] = [UserRole.ADMIN, UserRole.MANAGER, UserRole.USER]
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
            role=UserRole.USER,
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
async def create_sourcing_partner(partner: SourcingPartnerCreate):
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
    return partner_obj

@api_router.get("/sourcing", response_model=List[SourcingPartner])
async def get_sourcing_partners():
    partners = await db.sourcing_partners.find().to_list(1000)
    return [SourcingPartner(**partner) for partner in partners]

@api_router.get("/sourcing/{partner_id}", response_model=SourcingPartner)
async def get_sourcing_partner(partner_id: str):
    partner = await db.sourcing_partners.find_one({"id": partner_id})
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return SourcingPartner(**partner)

@api_router.put("/sourcing/{partner_id}", response_model=SourcingPartner)
async def update_sourcing_partner(partner_id: str, partner_update: SourcingPartnerUpdate):
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
    
    updated_partner = await db.sourcing_partners.find_one({"id": partner_id})
    return SourcingPartner(**updated_partner)

@api_router.delete("/sourcing/{partner_id}")
async def delete_sourcing_partner(partner_id: str):
    result = await db.sourcing_partners.delete_one({"id": partner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")
    return {"message": "Partner deleted successfully"}

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
    return partner_obj

@api_router.get("/dealflow", response_model=List[DealflowPartner])
async def get_dealflow_partners():
    partners = await db.dealflow_partners.find().to_list(1000)
    return [DealflowPartner(**partner) for partner in partners]

@api_router.get("/dealflow/{partner_id}", response_model=DealflowPartner)
async def get_dealflow_partner(partner_id: str):
    partner = await db.dealflow_partners.find_one({"id": partner_id})
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return DealflowPartner(**partner)

@api_router.put("/dealflow/{partner_id}", response_model=DealflowPartner)
async def update_dealflow_partner(partner_id: str, partner_update: DealflowPartnerUpdate):
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
    
    updated_partner = await db.dealflow_partners.find_one({"id": partner_id})
    return DealflowPartner(**updated_partner)

@api_router.delete("/dealflow/{partner_id}")
async def delete_dealflow_partner(partner_id: str):
    result = await db.dealflow_partners.delete_one({"id": partner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")
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
    
    return {"message": "Partner enriched successfully", "enriched_data": enriched_data}

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