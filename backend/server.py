# ============================================================
# CORRECTIONS APPLIQUÉES — server.py
# ============================================================
# BUG 1 : double "import json" supprimé
# BUG 2 : double déclaration openai_client + has_openai() supprimée
# BUG 3 : get_sourcing_partners — gestion robuste _id / id
# BUG 4 : /partners-by-pilote — return manquant ajouté
# BUG 5 : /kanban-move — recherche par _id OU id string
# ============================================================

from fastapi import FastAPI, APIRouter, HTTPException, Body, Request
from dotenv import load_dotenv
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
import json                          # ← BUG 1 CORRIGÉ : un seul import json
from bson.objectid import ObjectId
from bson.errors import InvalidId
import math
from tavily import TavilyClient
from openai import OpenAI

tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY", ""))

def has_tavily():
    return bool(os.environ.get("TAVILY_API_KEY"))

# ← BUG 2 CORRIGÉ : openai_client et has_openai() déclarés UNE SEULE FOIS ici
openai_client = None
if os.environ.get("OPENAI_API_KEY"):
    openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def has_openai():
    return openai_client is not None


def clean_nans(obj):
    if isinstance(obj, float):
        if math.isnan(obj):
            return 0
        return obj
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nans(v) for v in obj]
    return obj


def llm_enrich_fr(company_name: str, website_url: str | None,
                  tavily_answer: str | None, tavily_urls: list[str]) -> dict:
    if not has_openai():
        return {}

    urls_str = "\n".join(tavily_urls[:5]) if tavily_urls else ""

    prompt = f"""
Tu es analyste Open Innovation dans l'assurance.

À partir des informations suivantes, retourne UNIQUEMENT un JSON valide
(sans texte autour) avec les clés suivantes :
- description_fr : 2 à 3 phrases en français (ton professionnel)
- technologies : liste de technologies utilisées
- use_cases_insurance : liste de cas d'usages concrets pour un assureur

Startup : {company_name}
Site : {website_url or "inconnu"}
Résumé web : {tavily_answer or "indisponible"}
Liens :
{urls_str}

Contraintes :
- JSON strict
- listes pour technologies et use_cases_insurance
"""

    try:
        resp = openai_client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = resp.choices[0].message.content.strip()
        data = json.loads(content)

        if not isinstance(data, dict):
            return {}

        data.setdefault("description_fr", "")
        data.setdefault("technologies", [])
        data.setdefault("use_cases_insurance", [])
        return data

    except Exception as e:
        print(f"OpenAI enrich error: {str(e)}")
        return {}

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="SURM Dashboard API", description="API pour la gestion des partenaires de sourcing.")

from fastapi.middleware.cors import CORSMiddleware

default_origins = [
    "https://dashboard-surm-1.onrender.com",
    "https://dashboard-surm.onrender.com",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
]

configured_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOW_ORIGINS", "").split(",")
    if origin.strip()
]

cors_allow_origins = configured_origins or default_origins
cors_allow_origin_regex = os.environ.get("CORS_ALLOW_ORIGIN_REGEX")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins,
    allow_origin_regex=cors_allow_origin_regex,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

# --- Enums ---
class SourcingStatus(str, Enum):
    A_TRAITER = "A traiter"
    CLOS = "Clos"
    DEALFLOW = "Dealflow"
    KLAXOON = "Klaxoon"
    EN_COURS = "EN COURS"

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

# --- Models (inchangés) ---
class FormField(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    label: str
    type: FieldType
    required: bool = False
    options: Optional[List[str]] = None
    placeholder: Optional[str] = None
    validation_regex: Optional[str] = None
    order: int = 0
    visible: bool = True
    editable_by_roles: List[UserRole] = [UserRole.ADMIN, UserRole.CONTRIBUTEUR, UserRole.OBSERVATEUR]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FormConfiguration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    form_type: str
    fields: List[FormField]
    permissions: Dict[str, List[UserRole]] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserPermission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    role: UserRole
    permissions: Dict[str, bool] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EnrichmentSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    auto_enrich: bool = True
    sources: List[str] = ["linkedin", "crunchbase", "website"]
    fields_to_enrich: List[str] = ["founding_year", "employee_count", "funding_rounds", "contact_emails"]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str
    partner_type: str
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    document_type: DocumentType
    content: str
    version: int = 1
    description: Optional[str] = None
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SourcingPartner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
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
    date_prochaine_action: Optional[date] = None
    is_inactive: Optional[bool] = None
    days_since_update: Optional[int] = None
    score_maturite: Optional[int] = None
    priorite_strategique: Optional[str] = None
    score_potentiel: Optional[int] = None
    tags_strategiques: Optional[List[str]] = []
    logo_url: Optional[str] = None
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
    date_prochaine_action: Optional[date] = None
    score_maturite: Optional[int] = None
    priorite_strategique: Optional[str] = None
    score_potentiel: Optional[int] = None
    tags_strategiques: Optional[List[str]] = []
    logo_url: Optional[str] = None
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
    date_prochaine_action: Optional[date] = None
    score_maturite: Optional[int] = None
    priorite_strategique: Optional[str] = None
    score_potentiel: Optional[int] = None
    tags_strategiques: Optional[List[str]] = None
    logo_url: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

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
    date_prochaine_action: Optional[date] = None
    is_inactive: Optional[bool] = None
    days_since_update: Optional[int] = None
    sourcing_id: Optional[str] = None
    pays_origine: Optional[str] = None
    cas_usage: Optional[str] = None
    technologie: Optional[str] = None
    interet: Optional[bool] = None
    score_maturite: Optional[int] = None
    priorite_strategique: Optional[str] = None
    score_potentiel: Optional[int] = None
    tags_strategiques: Optional[List[str]] = []
    logo_url: Optional[str] = None
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
    date_prochaine_action: Optional[date] = None
    sourcing_id: Optional[str] = None
    pays_origine: Optional[str] = None
    cas_usage: Optional[str] = None
    technologie: Optional[str] = None
    interet: Optional[bool] = None
    logo_url: Optional[str] = None
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
    date_prochaine_action: Optional[date] = None
    logo_url: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

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

class ActivityType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    TRANSITIONED = "transitioned"
    COMMENT_ADDED = "comment_added"
    STATUS_CHANGED = "status_changed"
    ENRICHED = "enriched"

class ActivityLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str
    partner_type: str
    activity_type: ActivityType
    description: str
    details: Optional[Dict[str, Any]] = {}
    user_id: Optional[str] = None
    user_name: Optional[str] = None
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
    partner_id: str
    partner_type: str
    user_id: str
    user_name: str
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

# --- Scraping & enrichment helpers (inchangés) ---
async def scrape_linkedin_basic(company_name: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            search_url = f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}"
            response = await client.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
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
    try:
        if not domain.startswith('http'):
            domain = f"https://{domain}"
        async with httpx.AsyncClient() as client:
            response = await client.get(domain, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
                emails = list(set(email_pattern.findall(response.text)))
                description = soup.find('meta', attrs={'name': 'description'})
                title = soup.find('title')
                return {
                    "website_description": description.get('content', '') if description else '',
                    "website_title": title.text if title else '',
                    "contact_emails": emails[:3],
                    "website_url": domain
                }
    except Exception as e:
        logging.error(f"Website scraping failed: {e}")
    return {}

async def enrich_company_data(company_name: str, domain: str = None) -> Dict[str, Any]:
    enriched_data = {}
    linkedin_data = await scrape_linkedin_basic(company_name)
    enriched_data.update(linkedin_data)
    if domain:
        website_data = await scrape_website_info(domain)
        enriched_data.update(website_data)
    enriched_data["enriched_at"] = datetime.utcnow().isoformat()
    return enriched_data

# --- Inactivity helpers ---
def calculate_inactivity_days(updated_at: datetime) -> int:
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
    delta = datetime.utcnow() - updated_at
    return delta.days

def is_inactive(updated_at: datetime, threshold_days: int = 90) -> bool:
    return calculate_inactivity_days(updated_at) >= threshold_days

async def log_activity(partner_id: str, partner_type: str, activity_type: ActivityType,
                      description: str, details: Dict[str, Any] = None,
                      user_id: str = None, user_name: str = None):
    activity = ActivityLog(
        partner_id=partner_id,
        partner_type=partner_type,
        activity_type=activity_type,
        description=description,
        details=details or {},
        user_id=user_id,
        user_name=user_name
    )
    activity_dict = activity.dict()
    activity_dict["created_at"] = activity.created_at.isoformat()
    await db.activity_logs.insert_one(activity_dict)
    return activity

def add_inactivity_status(partner_data: dict) -> dict:
    partner_data["is_inactive"] = is_inactive(partner_data.get("updated_at"))
    partner_data["days_since_update"] = calculate_inactivity_days(partner_data.get("updated_at"))
    return partner_data

# --- User helpers ---
async def get_current_user(user_id: str = "default_user") -> User:
    user = await db.users.find_one({"id": user_id})
    if not user:
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
    if user_role == UserRole.ADMIN:
        return True
    if user_role == UserRole.OBSERVATEUR:
        return True
    if user_role == UserRole.CONTRIBUTEUR:
        return partner_pilote == user_name
    return False

def can_edit_partner(user_role: UserRole, partner_pilote: str, user_name: str) -> bool:
    if user_role == UserRole.ADMIN:
        return True
    if user_role == UserRole.CONTRIBUTEUR:
        return partner_pilote == user_name
    return False

def can_view_private_comment(comment_user_id: str, current_user_id: str, current_user_role: UserRole) -> bool:
    if current_user_role == UserRole.ADMIN:
        return True
    return comment_user_id == current_user_id


# ============================================================
# HELPER — BUG 3 CORRIGÉ
# Normalise un document MongoDB : garantit la présence d'un
# champ "id" (string) et supprime "_id" (ObjectId).
# ============================================================
def normalize_doc(doc: dict) -> dict:
    """
    Garantit que le document a un champ 'id' (string)
    et supprime '_id' pour éviter les erreurs Pydantic.
    """
    if doc is None:
        return doc
    _id = doc.get("_id")
    existing_id = doc.get("id")

    if existing_id:
        # id string déjà présent → on garde, on supprime juste _id
        doc.pop("_id", None)
    elif _id:
        # Pas d'id string mais _id ObjectId présent → on convertit
        doc["id"] = str(_id)
        doc.pop("_id", None)
    # Si ni l'un ni l'autre → on laisse tel quel (Pydantic génèrera une erreur explicite)
    return doc


# --- Config endpoints (inchangés) ---
@api_router.post("/config/columns")
async def save_column_config(column_config: Dict[str, Any]):
    await db.column_configurations.replace_one(
        {"type": "columns"},
        {"type": "columns", "config": column_config, "updated_at": datetime.utcnow()},
        upsert=True
    )
    return {"message": "Column configuration saved successfully"}

@api_router.get("/config/columns")
async def get_column_config():
    config = await db.column_configurations.find_one({"type": "columns"})
    if not config:
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

@api_router.post("/config/form", response_model=FormConfiguration)
async def create_form_config(config: FormConfiguration):
    config_dict = config.dict()
    for field in config_dict.get("fields", []):
        if isinstance(field.get("created_at"), datetime):
            field["created_at"] = field["created_at"].isoformat()
    await db.form_configurations.replace_one(
        {"form_type": config.form_type},
        config_dict,
        upsert=True
    )
    return config

@api_router.get("/config/form/{form_type}", response_model=FormConfiguration)
async def get_form_config(form_type: str):
    config = await db.form_configurations.find_one({"form_type": form_type})
    if not config:
        raise HTTPException(status_code=404, detail="Form configuration not found")
    return FormConfiguration(**config)

@api_router.get("/config/forms", response_model=List[FormConfiguration])
async def get_all_form_configs():
    configs = await db.form_configurations.find().to_list(100)
    return [FormConfiguration(**config) for config in configs]

@api_router.post("/config/permissions", response_model=UserPermission)
async def create_user_permissions(permission: UserPermission):
    permission_dict = permission.dict()
    await db.user_permissions.replace_one(
        {"user_id": permission.user_id},
        permission_dict,
        upsert=True
    )
    return permission

@api_router.get("/config/permissions/{user_id}", response_model=UserPermission)
async def get_user_permissions(user_id: str):
    permissions = await db.user_permissions.find_one({"user_id": user_id})
    if not permissions:
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
    settings_dict = settings.dict()
    await db.enrichment_settings.replace_one(
        {"id": settings.id},
        settings_dict,
        upsert=True
    )
    return settings

@api_router.get("/config/enrichment", response_model=EnrichmentSettings)
async def get_enrichment_settings():
    settings = await db.enrichment_settings.find_one()
    if not settings:
        return EnrichmentSettings()
    return EnrichmentSettings(**settings)


# --- Sourcing endpoints ---
@api_router.post("/sourcing", response_model=SourcingPartner)
async def create_sourcing_partner(partner: SourcingPartnerCreate, user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    if current_user.role == UserRole.OBSERVATEUR:
        raise HTTPException(status_code=403, detail="Observateur cannot create partners")

    partner_dict = partner.dict()
    enrichment_settings = await get_enrichment_settings()
    if enrichment_settings.auto_enrich:
        enriched_data = await enrich_company_data(
            partner.nom_entreprise,
            partner_dict.get("website_domain")
        )
        partner_dict["enriched_data"] = enriched_data

    partner_obj = SourcingPartner(**partner_dict)
    partner_data = partner_obj.dict()
    for key, value in partner_data.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            partner_data[key] = value.isoformat()

    await db.sourcing_partners.insert_one(partner_data)

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


# ============================================================
# BUG 3 CORRIGÉ — get_sourcing_partners
# Utilise normalize_doc() pour garantir la présence de 'id'
# ============================================================
@api_router.get("/sourcing", response_model=List[SourcingPartner])
async def get_sourcing_partners(user_id: str = "default_user"):
    current_user = await get_current_user(user_id)

    query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        query["pilote"] = current_user.full_name

   
    partners = await db.sourcing_partners.find(query).to_list(2000)

    partners_with_status = []
    for partner in partners:
        partner = normalize_doc(partner)          # ← BUG 3 CORRIGÉ
        partner_with_status = add_inactivity_status(partner)
        partners_with_status.append(SourcingPartner(**partner_with_status))

    return partners_with_status


@api_router.get("/sourcing/{partner_id}", response_model=SourcingPartner)
async def get_sourcing_partner(partner_id: str, user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    partner = await db.sourcing_partners.find_one({"id": partner_id})
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    if not can_view_partner(current_user.role, partner.get("pilote"), current_user.full_name):
        raise HTTPException(status_code=403, detail="Not authorized to view this partner")
    partner = normalize_doc(partner)
    partner_with_status = add_inactivity_status(partner)
    return SourcingPartner(**partner_with_status)


@api_router.put("/sourcing/{partner_id}", response_model=SourcingPartner)
async def update_sourcing_partner(
    partner_id: str,
    partner_update: SourcingPartnerUpdate,
    user_id: str = "default_user"
):
    current_user = await get_current_user(user_id)

    try:
        query = {"$or": [{"id": partner_id}, {"_id": ObjectId(partner_id)}]}
    except (InvalidId, TypeError):
        query = {"id": partner_id}

    original_partner = await db.sourcing_partners.find_one(query)
    if original_partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")

    if not can_edit_partner(current_user.role, original_partner.get("pilote"), current_user.full_name):
        raise HTTPException(status_code=403, detail="Not authorized to edit this partner")

    update_dict = {k: v for k, v in partner_update.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()

    for key, value in list(update_dict.items()):
        if isinstance(value, date) and not isinstance(value, datetime):
            update_dict[key] = value.isoformat()

    result = await db.sourcing_partners.update_one(query, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")

    changes = []
    for key, new_value in update_dict.items():
        if key != "updated_at" and key in original_partner:
            old_value = original_partner.get(key)
            if old_value != new_value:
                changes.append(f"{key}: '{old_value}' -> '{new_value}'")

    if changes:
        await log_activity(
            partner_id=partner_id,
            partner_type="sourcing",
            activity_type=ActivityType.UPDATED,
            description=f"Partenaire sourcing modifié. Champs: {', '.join(changes)}",
            details={"changes": changes},
            user_id=current_user.id,
            user_name=current_user.full_name
        )

    updated_partner_doc = await db.sourcing_partners.find_one(query)
    if updated_partner_doc is None:
        raise HTTPException(status_code=404, detail="Partner not found")

    updated_partner_doc = normalize_doc(updated_partner_doc)   # ← normalize ici aussi
    partner_with_status = add_inactivity_status(updated_partner_doc)
    return SourcingPartner(**partner_with_status)


@api_router.delete("/sourcing/{partner_id}")
async def delete_sourcing_partner(partner_id: str, user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    partner = await db.sourcing_partners.find_one({"id": partner_id})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can delete partners")
    result = await db.sourcing_partners.delete_one({"id": partner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")
    await log_activity(
        partner_id=partner_id,
        partner_type="sourcing",
        activity_type=ActivityType.UPDATED,
        description=f"Startup '{partner['nom_entreprise']}' supprimée du sourcing",
        details={"action": "deleted"},
        user_id=current_user.id,
        user_name=current_user.full_name
    )
    return {"message": "Partner deleted successfully"}


# --- Duplicate detection ---
@api_router.get("/partners/check-duplicate")
async def check_duplicate_partners(name: str):
    if not name or len(name) < 3:
        return {"duplicates": []}

    name_clean = name.strip().lower()
    patterns = [
        {"$regex": f"^{re.escape(name_clean)}$", "$options": "i"},
        {"$regex": re.escape(name_clean), "$options": "i"},
    ]
    words = name_clean.split()
    if len(words) > 1:
        word_pattern = "|".join([re.escape(word) for word in words if len(word) > 2])
        if word_pattern:
            patterns.append({"$regex": word_pattern, "$options": "i"})

    duplicates = []

    for pattern in patterns:
        sourcing_partners = await db.sourcing_partners.find(
            {"nom_entreprise": pattern}
        ).limit(10).to_list(10)
        for partner in sourcing_partners:
            partner = normalize_doc(partner)
            partner_name = partner.get("nom_entreprise", "").lower()
            similarity = calculate_similarity(name_clean, partner_name)
            if similarity >= 0.6:
                duplicate_info = {
                    "id": partner["id"],
                    "name": partner["nom_entreprise"],
                    "type": "sourcing",
                    "similarity": round(similarity, 2),
                    "domain": partner.get("domaine_activite", "N/A"),
                    "status": partner.get("statut", "N/A"),
                    "pilot": partner.get("pilote", "N/A")
                }
                if not any(d["id"] == duplicate_info["id"] for d in duplicates):
                    duplicates.append(duplicate_info)

    for pattern in patterns:
        dealflow_partners = await db.dealflow_partners.find(
            {"nom": pattern}
        ).limit(10).to_list(10)
        for partner in dealflow_partners:
            partner = normalize_doc(partner)
            partner_name = partner.get("nom", "").lower()
            similarity = calculate_similarity(name_clean, partner_name)
            if similarity >= 0.6:
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

    duplicates.sort(key=lambda x: x["similarity"], reverse=True)
    return {"search_term": name, "duplicates": duplicates[:5], "found_count": len(duplicates)}


def calculate_similarity(str1: str, str2: str) -> float:
    if not str1 or not str2:
        return 0.0
    if str1 == str2:
        return 1.0
    if str1 in str2 or str2 in str1:
        return 0.8
    words1 = set(str1.split())
    words2 = set(str2.split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    jaccard_sim = len(intersection) / len(union) if union else 0.0
    common_chars = sum(1 for c in str1 if c in str2)
    char_sim = common_chars / max(len(str1), len(str2))
    return (jaccard_sim * 0.7) + (char_sim * 0.3)


# --- Company enrichment models + endpoint (inchangés) ---
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
    logo_url: Optional[str] = None

class CompanyEnrichmentResponse(BaseModel):
    success: bool
    company_data: Optional[EnrichedCompanyData] = None
    error_message: Optional[str] = None
    api_source: Optional[str] = None

@api_router.post("/enrich-company", response_model=CompanyEnrichmentResponse)
async def enrich_company_endpoint(request: CompanyEnrichmentRequest):
    try:
        if has_tavily():
            try:
                query = request.query.strip()
                country_hint = "France"
                tavily_query = f"{query} {country_hint} site officiel"

                res = tavily_client.search(
                    query=tavily_query,
                    max_results=5,
                    include_answer=True,
                    include_raw_content=False
                )

                results = res.get("results", []) or []
                urls = [r.get("url") for r in results if r.get("url")]

                if not urls:
                    raise Exception("No Tavily results")

                website_url = None
                for u in urls:
                    if u and not any(x in u for x in [
                        "societe.com", "pappers.fr", "verif.com", "manageo.fr",
                        "annuaire", "wikipedia"
                    ]):
                        website_url = u
                        break

                if not website_url:
                    website_url = urls[0]

                if website_url and not website_url.startswith("http"):
                    website_url = "https://" + website_url

                tavily_answer = res.get("answer")
                tavily_urls = urls

                ai = llm_enrich_fr(
                    company_name=request.query,
                    website_url=website_url,
                    tavily_answer=tavily_answer,
                    tavily_urls=tavily_urls
                )

                description_fr = (ai.get("description_fr") or "").strip()

                # Récupération automatique du logo via Clearbit
                logo_url = None
                if website_url:
                    try:
                        from urllib.parse import urlparse
                        domain_parsed = urlparse(website_url).netloc or urlparse(website_url).path
                        domain_parsed = domain_parsed.replace("www.", "")
                        if domain_parsed:
                           logo_url = f"https://www.google.com/s2/favicons?domain={domain_parsed}&sz=128"
                    except Exception:
                        pass

                enriched_data = EnrichedCompanyData(
                    name=request.query.title(),
                    domain=request.domain,
                    website=website_url,
                    description=description_fr or (tavily_answer or "Résumé indisponible."),
                    country="France",
                    logo_url=logo_url
                )

                return CompanyEnrichmentResponse(
                    success=True,
                    company_data=enriched_data,
                    api_source="tavily_web_search"
                )

            except Exception as e:
                print(f"Tavily error: {str(e)}")

        # Fallback SIRENE
        try:
            sirene_url = "https://api.insee.fr/entreprises/sirene/V3/siret"
            headers = {'Accept': 'application/json'}
            params = {
                'q': f'denominationUniteLegale:"{request.query}"',
                'nombre': 1
            }
            response = requests.get(sirene_url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'etablissements' in data and len(data['etablissements']) > 0:
                    etablissement = data['etablissements'][0]
                    unite_legale = etablissement.get('uniteLegale', {})
                    enriched_data = EnrichedCompanyData(
                        name=unite_legale.get('denominationUniteLegale'),
                        industry=etablissement.get('libelleSecteurActiviteUniteLegale'),
                        country="France",
                        country_code="FR",
                        company_type="private" if unite_legale.get('categorieJuridiqueUniteLegale') else None,
                        year_founded=int(unite_legale.get('dateCreationUniteLegale', '0')[:4])
                        if unite_legale.get('dateCreationUniteLegale') else None
                    )
                    return CompanyEnrichmentResponse(
                        success=True,
                        company_data=enriched_data,
                        api_source="sirene_api"
                    )
        except Exception as e:
            print(f"SIRENE API error: {str(e)}")

        # Fallback basique
        try:
            query_clean = request.query.lower().strip()
            company_name = request.query.title()
            enriched_data = EnrichedCompanyData(
                name=company_name,
                domain=request.domain if request.domain else f"{query_clean.replace(' ', '').replace('-', '')}.com",
                description="Recherche en cours ou information non disponible.",
                industry="À préciser",
                company_type='private',
                employees_count=100
            )
            return CompanyEnrichmentResponse(
                success=True,
                company_data=enriched_data,
                api_source="enhanced_basic_enrichment"
            )
        except Exception as e:
            print(f"Enhanced basic enrichment error: {str(e)}")
            return CompanyEnrichmentResponse(
                success=False,
                error_message="Aucune donnée trouvée. Vérifiez le nom ou le domaine."
            )

    except Exception as e:
        return CompanyEnrichmentResponse(
            success=False,
            error_message=f"Erreur lors de l'enrichissement: {str(e)}"
        )


# --- Dealflow endpoints ---
@api_router.post("/dealflow", response_model=DealflowPartner)
async def create_dealflow_partner(partner: DealflowPartnerCreate):
    partner_dict = partner.dict()
    enrichment_settings = await get_enrichment_settings()
    if enrichment_settings.auto_enrich:
        enriched_data = await enrich_company_data(
            partner.nom,
            partner_dict.get("website_domain")
        )
        partner_dict["enriched_data"] = enriched_data

    partner_obj = DealflowPartner(**partner_dict)
    partner_data = partner_obj.dict()
    for key, value in partner_data.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            partner_data[key] = value.isoformat()

    await db.dealflow_partners.insert_one(partner_data)
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
    partners = await db.dealflow_partners.find().to_list(10000)
    partners_with_status = []
    for partner in partners:
        partner = normalize_doc(partner)          # ← normalize
        partner_with_status = add_inactivity_status(partner)
        partners_with_status.append(DealflowPartner(**partner_with_status))
    return partners_with_status


@api_router.get("/dealflow/{partner_id}", response_model=DealflowPartner)
async def get_dealflow_partner(partner_id: str):
    partner = await db.dealflow_partners.find_one({"id": partner_id})
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    partner = normalize_doc(partner)
    partner_with_status = add_inactivity_status(partner)
    return DealflowPartner(**partner_with_status)


@api_router.put("/dealflow/{partner_id}", response_model=DealflowPartner)
async def update_dealflow_partner(partner_id: str, partner_update: DealflowPartnerUpdate):
    original_partner = await db.dealflow_partners.find_one({"id": partner_id})
    if not original_partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    update_dict = {k: v for k, v in partner_update.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()

    for key, value in update_dict.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            update_dict[key] = value.isoformat()

    result = await db.dealflow_partners.update_one(
        {"id": partner_id},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")

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
    updated_partner = normalize_doc(updated_partner)
    updated_partner = add_inactivity_status(updated_partner)
    return DealflowPartner(**updated_partner)


@api_router.delete("/dealflow/{partner_id}")
async def delete_dealflow_partner(partner_id: str):
    partner = await db.dealflow_partners.find_one({"id": partner_id})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    result = await db.dealflow_partners.delete_one({"id": partner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")
    await log_activity(
        partner_id=partner_id,
        partner_type="dealflow",
        activity_type=ActivityType.UPDATED,
        description=f"Startup '{partner['nom']}' supprimée du dealflow",
        details={"action": "deleted"},
        user_name="System"
    )
    return {"message": "Partner deleted successfully"}


@api_router.post("/transition/{sourcing_id}")
async def transition_to_dealflow(sourcing_id: str, dealflow_data: Dict[str, Any] = Body(...)):
    sourcing_partner = await db.sourcing_partners.find_one({"id": sourcing_id})
    if sourcing_partner is None:
        raise HTTPException(status_code=404, detail="Sourcing partner not found")

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
        "date_prochaine_action": sourcing_partner.get("date_prochaine_action"),
        **dealflow_data
    }

    dealflow_partner = DealflowPartner(**dealflow_partner_data)
    dealflow_data_for_db = dealflow_partner.dict()
    for key, value in dealflow_data_for_db.items():
        if isinstance(value, date) and not isinstance(value, datetime):
            dealflow_data_for_db[key] = value.isoformat()

    await db.dealflow_partners.insert_one(dealflow_data_for_db)
    await db.sourcing_partners.update_one(
        {"id": sourcing_id},
        {"$set": {"statut": SourcingStatus.DEALFLOW, "updated_at": datetime.utcnow()}}
    )
    await log_activity(
        partner_id=sourcing_id,
        partner_type="sourcing",
        activity_type=ActivityType.TRANSITIONED,
        description=f"Startup '{sourcing_partner['nom_entreprise']}' transférée vers dealflow",
        details={"new_dealflow_id": dealflow_partner.id, "new_status": "dealflow"},
        user_name="System"
    )
    await log_activity(
        partner_id=dealflow_partner.id,
        partner_type="dealflow",
        activity_type=ActivityType.CREATED,
        description=f"Startup '{dealflow_partner.nom}' créée en dealflow (transition depuis sourcing)",
        details={"source_sourcing_id": sourcing_id, "inherited": True},
        user_name="System"
    )
    return dealflow_partner


@api_router.get("/statistics", response_model=DashboardStats)
async def get_dashboard_statistics():
    sourcing_partners = await db.sourcing_partners.find().to_list(10000)
    dealflow_partners = await db.dealflow_partners.find().to_list(10000)

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

    monthly_stats = {}
    for partner in dealflow_partners:
        pre_qual_date = partner.get("date_pre_qualification")
        if pre_qual_date:
            if isinstance(pre_qual_date, str):
                pre_qual_date = datetime.fromisoformat(pre_qual_date.replace('Z', '+00:00')).date()
            month_key = f"{pre_qual_date.year}-{pre_qual_date.month:02d}"
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {"pre_qualifications": 0, "go_studies": 0}
            monthly_stats[month_key]["pre_qualifications"] += 1

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

    domain_dist = {}
    typologie_dist = {}
    technology_dist = {}
    metiers_dist = {}
    sourcing_status_dist = {}
    dealflow_status_dist = {}

    for partner in sourcing_partners:
        domain_dist[partner.get("domaine_activite", "Unknown")] = domain_dist.get(partner.get("domaine_activite", "Unknown"), 0) + 1
        typologie_dist[partner.get("typologie", "Unknown")] = typologie_dist.get(partner.get("typologie", "Unknown"), 0) + 1
        technology_dist[partner.get("technologie", "Unknown")] = technology_dist.get(partner.get("technologie", "Unknown"), 0) + 1
        sourcing_status_dist[partner.get("statut", "Unknown")] = sourcing_status_dist.get(partner.get("statut", "Unknown"), 0) + 1

    for partner in dealflow_partners:
        domain_dist[partner.get("domaine", "Unknown")] = domain_dist.get(partner.get("domaine", "Unknown"), 0) + 1
        typologie_dist[partner.get("typologie", "Unknown")] = typologie_dist.get(partner.get("typologie", "Unknown"), 0) + 1
        metiers_dist[partner.get("metiers_concernes", "Unknown")] = metiers_dist.get(partner.get("metiers_concernes", "Unknown"), 0) + 1
        dealflow_status_dist[partner.get("statut", "Unknown")] = dealflow_status_dist.get(partner.get("statut", "Unknown"), 0) + 1

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


@api_router.post("/enrich/{partner_id}")
async def enrich_partner_data(partner_id: str, partner_type: str = "sourcing"):
    collection = db.sourcing_partners if partner_type == "sourcing" else db.dealflow_partners
    partner = await collection.find_one({"id": partner_id})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    company_name = partner.get("nom_entreprise" if partner_type == "sourcing" else "nom")
    enriched_data = await enrich_company_data(company_name)

    await collection.update_one(
        {"id": partner_id},
        {"$set": {"enriched_data": enriched_data, "updated_at": datetime.utcnow()}}
    )

    await log_activity(
        partner_id=partner_id,
        partner_type=partner_type,
        activity_type=ActivityType.ENRICHED,
        description=f"Données enrichies automatiquement pour '{company_name}'",
        details={"sources": ["linkedin", "website"], "fields_updated": list(enriched_data.keys())},
        user_name="System"
    )
    return {"message": "Partner enriched successfully", "enriched_data": enriched_data}


@api_router.get("/activity/{partner_id}", response_model=List[ActivityLogResponse])
async def get_partner_activity_timeline(partner_id: str, partner_type: str = "sourcing"):
    activities = await db.activity_logs.find({
        "partner_id": partner_id,
        "partner_type": partner_type
    }).sort("created_at", -1).to_list(100)
    return [ActivityLogResponse(**activity) for activity in activities]


@api_router.post("/activity/{partner_id}")
async def add_manual_activity(partner_id: str, partner_type: str,
                             description: str, user_name: str = "User"):
    collection = db.sourcing_partners if partner_type == "sourcing" else db.dealflow_partners
    partner = await collection.find_one({"id": partner_id})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
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
    threshold_date = datetime.utcnow() - timedelta(days=threshold_days)
    inactive_sourcing = await db.sourcing_partners.find({
        "updated_at": {"$lt": threshold_date.isoformat()}
    }).to_list(100)
    inactive_dealflow = await db.dealflow_partners.find({
        "updated_at": {"$lt": threshold_date.isoformat()}
    }).to_list(100)
    inactive_sourcing_with_status = [add_inactivity_status(normalize_doc(p)) for p in inactive_sourcing]
    inactive_dealflow_with_status = [add_inactivity_status(normalize_doc(p)) for p in inactive_dealflow]
    return {
        "threshold_days": threshold_days,
        "inactive_sourcing": inactive_sourcing_with_status,
        "inactive_dealflow": inactive_dealflow_with_status,
        "total_inactive": len(inactive_sourcing) + len(inactive_dealflow)
    }


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
    import base64

    try:
        content_type_header = request.headers.get("content-type", "")
        if "application/json" in content_type_header:
            body = await request.json()
            if 'partner_id' in body: partner_id = body['partner_id']
            if 'partner_type' in body: partner_type = body['partner_type']
            if 'filename' in body: filename = body['filename']
            if 'document_type' in body: document_type = body['document_type']
            if 'content' in body: content = body['content']
            if 'description' in body: description = body['description']
            if 'uploaded_by' in body: uploaded_by = body['uploaded_by']
    except Exception as e:
        print(f"JSON parsing failed, using query parameters: {e}")

    try:
        decoded_content = base64.b64decode(content)
        file_size = len(decoded_content)
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
        existing_docs = await db.documents.find({
            "partner_id": partner_id,
            "original_filename": filename
        }).to_list(100)
        version = max([doc["version"] for doc in existing_docs], default=0) + 1
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
        await db.documents.insert_one(document.dict())
        return document
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error uploading document: {str(e)}")


@api_router.get("/documents/{partner_id}", response_model=List[Document])
async def get_partner_documents(partner_id: str):
    documents = await db.documents.find({"partner_id": partner_id}).to_list(100)
    return [Document(**doc) for doc in documents]


@api_router.get("/documents/download/{document_id}")
async def download_document(document_id: str):
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
            headers={"Content-Disposition": f'attachment; filename="{document["filename"]}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")


@api_router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    result = await db.documents.delete_one({"id": document_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}


@api_router.get("/documents/types", response_model=List[str])
async def get_document_types():
    try:
        return [doc_type.value for doc_type in DocumentType]
    except Exception as e:
        return ["Convention", "Présentation", "Compte-rendu", "Contrat", "Document technique", "Autre"]


@api_router.get("/analytics/monthly-evolution")
async def get_monthly_evolution(start_date: str = None, end_date: str = None):
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=365)
        end_dt = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

    sourcing_partners = await db.sourcing_partners.find().to_list(10000)
    dealflow_partners = await db.dealflow_partners.find().to_list(10000)

    monthly_data = {}

    for partner in sourcing_partners:
        created_date = partner.get("created_at")
        if isinstance(created_date, str):
            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        if start_dt <= created_date <= end_dt:
            month_key = f"{created_date.year}-{created_date.month:02d}"
            if month_key not in monthly_data:
                monthly_data[month_key] = {"sourcing_created": 0, "dealflow_created": 0, "sourcing_closed": 0, "dealflow_closed": 0, "transitions": 0}
            monthly_data[month_key]["sourcing_created"] += 1

    for partner in dealflow_partners:
        created_date = partner.get("created_at")
        if isinstance(created_date, str):
            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        if start_dt <= created_date <= end_dt:
            month_key = f"{created_date.year}-{created_date.month:02d}"
            if month_key not in monthly_data:
                monthly_data[month_key] = {"sourcing_created": 0, "dealflow_created": 0, "sourcing_closed": 0, "dealflow_closed": 0, "transitions": 0}
            monthly_data[month_key]["dealflow_created"] += 1
            if partner.get("sourcing_id"):
                monthly_data[month_key]["transitions"] += 1

        closure_date = partner.get("date_cloture")
        if closure_date:
            if isinstance(closure_date, str):
                closure_date = datetime.fromisoformat(closure_date.replace('Z', '+00:00'))
            if start_dt <= closure_date <= end_dt:
                month_key = f"{closure_date.year}-{closure_date.month:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = {"sourcing_created": 0, "dealflow_created": 0, "sourcing_closed": 0, "dealflow_closed": 0, "transitions": 0}
                monthly_data[month_key]["dealflow_closed"] += 1

    for partner in sourcing_partners:
        if partner.get("statut") == "Clos":
            updated_date = partner.get("updated_at")
            if isinstance(updated_date, str):
                updated_date = datetime.fromisoformat(updated_date.replace('Z', '+00:00'))
            if start_dt <= updated_date <= end_dt:
                month_key = f"{updated_date.year}-{updated_date.month:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = {"sourcing_created": 0, "dealflow_created": 0, "sourcing_closed": 0, "dealflow_closed": 0, "transitions": 0}
                monthly_data[month_key]["sourcing_closed"] += 1

    sorted_data = sorted(monthly_data.items())
    return {"period": {"start": start_dt.isoformat(), "end": end_dt.isoformat()}, "monthly_evolution": sorted_data}


@api_router.get("/analytics/distribution")
async def get_enhanced_distribution(filter_by: str = None, filter_value: str = None,
                                  start_date: str = None, end_date: str = None):
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

    sourcing_partners = await db.sourcing_partners.find().to_list(10000)
    dealflow_partners = await db.dealflow_partners.find().to_list(10000)

    if start_dt and end_dt:
        def filter_by_date(partners):
            result = []
            for p in partners:
                created_at = p.get("created_at")
                if created_at:
                    if isinstance(created_at, str):
                        try:
                            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            if start_dt <= created_date <= end_dt:
                                result.append(p)
                        except ValueError:
                            continue
                    elif isinstance(created_at, datetime):
                        if start_dt <= created_at <= end_dt:
                            result.append(p)
            return result
        sourcing_partners = filter_by_date(sourcing_partners)
        dealflow_partners = filter_by_date(dealflow_partners)

    if filter_by and filter_value:
        if filter_by == "domaine":
            sourcing_partners = [p for p in sourcing_partners if p.get("domaine_activite") == filter_value]
            dealflow_partners = [p for p in dealflow_partners if p.get("domaine") == filter_value]
        elif filter_by == "pilote":
            sourcing_partners = [p for p in sourcing_partners if p.get("pilote") == filter_value]
            dealflow_partners = [p for p in dealflow_partners if p.get("pilote") == filter_value]

    distributions = {
        "by_status": {}, "by_domain": {}, "by_typologie": {}, "by_pilote": {}, "by_source": {},
        "summary": {
            "total_sourcing": len(sourcing_partners),
            "total_dealflow": len(dealflow_partners),
            "total_partners": len(sourcing_partners) + len(dealflow_partners)
        }
    }

    for partner in sourcing_partners:
        status = f"Sourcing - {partner.get('statut', 'Unknown')}"
        distributions["by_status"][status] = distributions["by_status"].get(status, 0) + 1
        domain = partner.get("domaine_activite", "Unknown")
        distributions["by_domain"][domain] = distributions["by_domain"].get(domain, 0) + 1
        typo = partner.get("typologie", "Unknown")
        distributions["by_typologie"][typo] = distributions["by_typologie"].get(typo, 0) + 1
        pilote = partner.get("pilote", "Unknown")
        distributions["by_pilote"][pilote] = distributions["by_pilote"].get(pilote, 0) + 1
        source = partner.get("source", "Unknown")
        distributions["by_source"][source] = distributions["by_source"].get(source, 0) + 1

    for partner in dealflow_partners:
        status = f"Dealflow - {partner.get('statut', 'Unknown')}"
        distributions["by_status"][status] = distributions["by_status"].get(status, 0) + 1
        domain = partner.get("domaine", "Unknown")
        distributions["by_domain"][domain] = distributions["by_domain"].get(domain, 0) + 1
        typo = partner.get("typologie", "Unknown")
        distributions["by_typologie"][typo] = distributions["by_typologie"].get(typo, 0) + 1
        pilote = partner.get("pilote", "Unknown")
        distributions["by_pilote"][pilote] = distributions["by_pilote"].get(pilote, 0) + 1
        source = partner.get("source", "Unknown")
        distributions["by_source"][source] = distributions["by_source"].get(source, 0) + 1

    return distributions


@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    user_obj = User(**user.dict())
    user_data = user_obj.dict()
    user_data["created_at"] = user_obj.created_at.isoformat()
    user_data["updated_at"] = user_obj.updated_at.isoformat()
    await db.users.insert_one(user_data)
    return user_obj

@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(10000)
    return [User(**user) for user in users]

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserUpdate):
    update_dict = {k: v for k, v in user_update.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    result = await db.users.update_one({"id": user_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await db.users.find_one({"id": user_id})
    return User(**updated_user)

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@api_router.post("/comments", response_model=PrivateCommentResponse)
async def create_private_comment(comment: PrivateCommentCreate, user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    comment_obj = PrivateComment(**comment.dict(), user_id=current_user.id, user_name=current_user.full_name)
    comment_data = comment_obj.dict()
    comment_data["created_at"] = comment_obj.created_at.isoformat()
    comment_data["updated_at"] = comment_obj.updated_at.isoformat()
    await db.private_comments.insert_one(comment_data)
    return PrivateCommentResponse(**comment_obj.dict())

@api_router.get("/comments/{partner_id}", response_model=List[PrivateCommentResponse])
async def get_partner_comments(partner_id: str, partner_type: str = "sourcing", user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    query = {"partner_id": partner_id, "partner_type": partner_type}
    if current_user.role != UserRole.ADMIN:
        query["user_id"] = current_user.id
    comments = await db.private_comments.find(query).sort("created_at", -1).to_list(100)
    return [PrivateCommentResponse(**comment) for comment in comments]

@api_router.put("/comments/{comment_id}", response_model=PrivateCommentResponse)
async def update_private_comment(comment_id: str, comment_update: PrivateCommentUpdate, user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    existing_comment = await db.private_comments.find_one({"id": comment_id})
    if not existing_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not can_view_private_comment(existing_comment["user_id"], current_user.id, current_user.role):
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    update_dict = comment_update.dict()
    update_dict["updated_at"] = datetime.utcnow()
    await db.private_comments.update_one({"id": comment_id}, {"$set": update_dict})
    updated_comment = await db.private_comments.find_one({"id": comment_id})
    return PrivateCommentResponse(**updated_comment)

@api_router.delete("/comments/{comment_id}")
async def delete_private_comment(comment_id: str, user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    existing_comment = await db.private_comments.find_one({"id": comment_id})
    if not existing_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not can_view_private_comment(existing_comment["user_id"], current_user.id, current_user.role):
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    await db.private_comments.delete_one({"id": comment_id})
    return {"message": "Comment deleted successfully"}


@api_router.get("/my-startups", response_model=Dict[str, Any])
async def get_my_startups(user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    sourcing_partners = await db.sourcing_partners.find({"pilote": current_user.full_name}).to_list(10000)
    dealflow_partners = await db.dealflow_partners.find({"pilote": current_user.full_name}).to_list(10000)

    sourcing_with_status = [add_inactivity_status(normalize_doc(p)) for p in sourcing_partners]
    dealflow_with_status = [add_inactivity_status(normalize_doc(p)) for p in dealflow_partners]

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


# ============================================================
# BUG 4 CORRIGÉ — /partners-by-pilote
# La fonction retournait None (oubli du return)
# ============================================================
@api_router.get("/partners-by-pilote")
async def get_partners_by_pilote():
    sourcing_partners = await db.sourcing_partners.find().to_list(10000)
    dealflow_partners = await db.dealflow_partners.find().to_list(10000)

    pilotes = {}

    for partner in sourcing_partners:
        partner = normalize_doc(partner)
        pilote = partner.get("pilote", "Unknown")
        if pilote not in pilotes:
            pilotes[pilote] = {"sourcing_partners": [], "dealflow_partners": []}
        pilotes[pilote]["sourcing_partners"].append(partner)

    for partner in dealflow_partners:
        partner = normalize_doc(partner)
        pilote = partner.get("pilote", "Unknown")
        if pilote not in pilotes:
            pilotes[pilote] = {"sourcing_partners": [], "dealflow_partners": []}
        pilotes[pilote]["dealflow_partners"].append(partner)

    for pilote, data in pilotes.items():
        sourcing_count = len(data["sourcing_partners"])
        dealflow_count = len(data["dealflow_partners"])
        data["total_partners"] = sourcing_count + dealflow_count
        data["summary"] = {
            "total_sourcing": sourcing_count,
            "total_dealflow": dealflow_count,
            "total_partners": sourcing_count + dealflow_count
        }

    return pilotes   # ← BUG 4 CORRIGÉ : return ajouté


@api_router.get("/kanban-data")
async def get_kanban_data(user_id: str = "default_user"):
    current_user = await get_current_user(user_id)

    sourcing_query = {}
    dealflow_query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        sourcing_query["pilote"] = current_user.full_name
        dealflow_query["pilote"] = current_user.full_name

    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(10000)
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(10000)

    kanban_data = {
        "columns": {
            "sourcing_a_traiter": {"id": "sourcing_a_traiter", "title": "🔍 Sourcing", "subtitle": "À traiter", "partners": []},
            "sourcing_klaxoon": {"id": "sourcing_klaxoon", "title": "📋 Sourcing", "subtitle": "Klaxoon", "partners": []},
            "prequalification": {"id": "prequalification", "title": "✓ Préqualif", "subtitle": "Évaluation initiale", "partners": []},
            "presentation": {"id": "presentation", "title": "📊 Présentation", "subtitle": "Aux métiers", "partners": []},
            "go_metier": {"id": "go_metier", "title": "🎯 Go Métier", "subtitle": "Étude approuvée", "partners": []},
            "experimentation": {"id": "experimentation", "title": "🧪 Expérimentation", "subtitle": "Test en cours", "partners": []},
            "evaluation": {"id": "evaluation", "title": "📈 Évaluation", "subtitle": "Résultats", "partners": []},
            "generalisation": {"id": "generalisation", "title": "🚀 Généralisation", "subtitle": "Déploiement", "partners": []},
            "cloture": {"id": "cloture", "title": "✅ Clôture", "subtitle": "Terminé", "partners": []}
        },
        "columnOrder": [
            "sourcing_a_traiter", "sourcing_klaxoon", "prequalification",
            "presentation", "go_metier", "experimentation",
            "evaluation", "generalisation", "cloture"
        ]
    }

    for partner in sourcing_partners:
        partner = normalize_doc(partner)
        partner_id = partner["id"]
        partner_with_status = add_inactivity_status(partner)
        status = partner.get("statut", "A traiter")

        kanban_partner = {
            **partner_with_status,
            "partner_type": "sourcing",
            # ← BUG 5 CORRIGÉ : séparateur "|" au lieu de "_" pour éviter
            #   le conflit avec les UUIDs qui contiennent des tirets (pas "_")
            #   mais par sécurité on utilise un séparateur non ambigu
            "kanban_id": f"sourcing|{partner_id}"
        }

        if status == "A traiter":
            kanban_data["columns"]["sourcing_a_traiter"]["partners"].append(kanban_partner)
        elif status == "Klaxoon":
            kanban_data["columns"]["sourcing_klaxoon"]["partners"].append(kanban_partner)

    for partner in dealflow_partners:
        partner = normalize_doc(partner)
        partner_id = partner["id"]
        partner_with_status = add_inactivity_status(partner)
        status = partner.get("statut", "En cours avec l'équipe inno")

        kanban_partner = {
            **partner_with_status,
            "partner_type": "dealflow",
            "kanban_id": f"dealflow|{partner_id}"   # ← BUG 5 CORRIGÉ
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
            kanban_data["columns"]["evaluation"]["partners"].append(kanban_partner)

    total_partners = len(sourcing_partners) + len(dealflow_partners)
    kanban_data["summary"] = {
        "total_partners": total_partners,
        "total_sourcing": len(sourcing_partners),
        "total_dealflow": len(dealflow_partners),
        "by_column": {col_id: len(col_data["partners"]) for col_id, col_data in kanban_data["columns"].items()}
    }

    return clean_nans(kanban_data)


# ============================================================
# BUG 5 CORRIGÉ — /kanban-move
# Séparateur "|" pour parser partner_type et partner_id
# + recherche par id string OU ObjectId
# ============================================================
@api_router.post("/kanban-move")
async def move_kanban_partner(
    partner_id: str,
    partner_type: str,
    source_column: str,
    destination_column: str,
    user_id: str = "default_user"
):
    current_user = await get_current_user(user_id)

    column_to_status = {
        "sourcing_a_traiter": {"type": "sourcing", "status": "A traiter"},
        "sourcing_klaxoon": {"type": "sourcing", "status": "Klaxoon"},
        "prequalification": {"type": "dealflow", "status": "En cours avec l'équipe inno"},
        "presentation": {"type": "dealflow", "status": "En cours avec les métiers"},
        "go_metier": {"type": "dealflow", "status": "Go métier étude"},
        "experimentation": {"type": "dealflow", "status": "Go experimentation"},
        "evaluation": {"type": "dealflow", "status": "En cours avec les métiers"},
        "generalisation": {"type": "dealflow", "status": "Go généralisation"},
        "cloture": {"type": "dealflow", "status": "Clos"}
    }

    if destination_column not in column_to_status:
        raise HTTPException(status_code=400, detail="Invalid destination column")

    new_status_info = column_to_status[destination_column]
    new_status = new_status_info["status"]
    target_type = new_status_info["type"]

    collection = db.sourcing_partners if partner_type == "sourcing" else db.dealflow_partners

    # Recherche robuste : id string d'abord, puis ObjectId si possible
    partner = await collection.find_one({"id": partner_id})
    if not partner:
        try:
            partner = await collection.find_one({"_id": ObjectId(partner_id)})
        except (InvalidId, TypeError):
            pass

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    if not can_edit_partner(current_user.role, partner.get("pilote"), current_user.full_name):
        raise HTTPException(status_code=403, detail="Not authorized to move this partner")

    partner = normalize_doc(partner)

    # Transition sourcing → dealflow
    if partner_type == "sourcing" and target_type == "dealflow":
        dealflow_data = {
            "nom": partner["nom_entreprise"],
            "statut": new_status,
            "domaine": partner["domaine_activite"],
            "typologie": partner["typologie"],
            "objet": partner["objet"],
            "source": partner["source"],
            "pilote": partner["pilote"],
            "metiers_concernes": "À définir",
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
        dealflow_data_for_db = dealflow_partner.dict()
        for key, value in dealflow_data_for_db.items():
            if isinstance(value, date) and not isinstance(value, datetime):
                dealflow_data_for_db[key] = value.isoformat()

        await db.dealflow_partners.insert_one(dealflow_data_for_db)
        await db.sourcing_partners.update_one(
            {"id": partner_id},
            {"$set": {"statut": "Dealflow", "updated_at": datetime.utcnow()}}
        )

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

    # Changement de statut dans le même type
    elif partner_type == target_type:
        await collection.update_one(
            {"id": partner_id},
            {"$set": {"statut": new_status, "updated_at": datetime.utcnow()}}
        )

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


@api_router.get("/synthetic-report")
async def get_synthetic_report(user_id: str = "default_user"):
    current_user = await get_current_user(user_id)

    sourcing_query = {}
    dealflow_query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        sourcing_query["pilote"] = current_user.full_name
        dealflow_query["pilote"] = current_user.full_name

    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(10000)
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(10000)

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

    status_data = {}
    for partner in sourcing_partners:
        status = f"Sourcing - {partner.get('statut', 'Unknown')}"
        status_data[status] = status_data.get(status, 0) + 1
    for partner in dealflow_partners:
        status = f"Dealflow - {partner.get('statut', 'Unknown')}"
        status_data[status] = status_data.get(status, 0) + 1
    report["cross_tables"]["by_status"] = status_data

    pilote_data = {}
    for partner in sourcing_partners:
        pilote = partner.get("pilote", "Unknown")
        if pilote not in pilote_data:
            pilote_data[pilote] = {"sourcing": 0, "dealflow": 0, "total": 0}
        pilote_data[pilote]["sourcing"] += 1
        pilote_data[pilote]["total"] += 1
    for partner in dealflow_partners:
        pilote = partner.get("pilote", "Unknown")
        if pilote not in pilote_data:
            pilote_data[pilote] = {"sourcing": 0, "dealflow": 0, "total": 0}
        pilote_data[pilote]["dealflow"] += 1
        pilote_data[pilote]["total"] += 1
    report["cross_tables"]["by_pilote"] = pilote_data

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

    collaboration_data = {}
    for partner in sourcing_partners + dealflow_partners:
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

    for partner in sourcing_partners:
        actions = partner.get("actions_commentaires", "") or ""
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
            "actions_commentaires": actions[:100] + "..." if len(actions) > 100 else actions
        })

    for partner in dealflow_partners:
        actions = partner.get("actions_commentaires", "") or ""
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
            "actions_commentaires": actions[:100] + "..." if len(actions) > 100 else actions
        })

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


@api_router.get("/quick-views/mes-startups")
async def get_my_startups_quick_view(user_id: str = "default_user"):
    current_user = await get_current_user(user_id)
    sourcing_partners = await db.sourcing_partners.find({"pilote": current_user.full_name}).to_list(10000)
    dealflow_partners = await db.dealflow_partners.find({"pilote": current_user.full_name}).to_list(10000)

    sourcing_clean = [add_inactivity_status(normalize_doc(p)) for p in sourcing_partners]
    dealflow_clean = [add_inactivity_status(normalize_doc(p)) for p in dealflow_partners]

    return {
        "view_name": "Mes Startups",
        "description": f"Startups pilotées par {current_user.full_name}",
        "sourcing": sourcing_clean,
        "dealflow": dealflow_clean,
        "summary": {"total": len(sourcing_clean) + len(dealflow_clean), "sourcing_count": len(sourcing_clean), "dealflow_count": len(dealflow_clean)}
    }


@api_router.get("/quick-views/a-relancer")
async def get_startups_to_follow_up(threshold_days: int = 90, user_id: str = "default_user"):
    current_user = await get_current_user(user_id)

    sourcing_query = {}
    dealflow_query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        sourcing_query["pilote"] = current_user.full_name
        dealflow_query["pilote"] = current_user.full_name

    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(10000)
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(10000)

    today = datetime.utcnow()
    sourcing_to_follow = []
    dealflow_to_follow = []

    for partner in sourcing_partners:
        partner = normalize_doc(partner)
        partner_with_status = add_inactivity_status(partner)
        needs_followup = False
        followup_reasons = []
        if partner_with_status.get("is_inactive"):
            needs_followup = True
            followup_reasons.append(f"Inactif depuis {partner_with_status.get('days_since_update')} jours")
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
        partner = normalize_doc(partner)
        partner_with_status = add_inactivity_status(partner)
        needs_followup = False
        followup_reasons = []
        if partner_with_status.get("is_inactive"):
            needs_followup = True
            followup_reasons.append(f"Inactif depuis {partner_with_status.get('days_since_update')} jours")
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
        "summary": {"total": len(sourcing_to_follow) + len(dealflow_to_follow), "sourcing_count": len(sourcing_to_follow), "dealflow_count": len(dealflow_to_follow), "threshold_days": threshold_days}
    }


@api_router.get("/quick-views/avec-documents")
async def get_startups_with_documents(user_id: str = "default_user"):
    current_user = await get_current_user(user_id)

    sourcing_query = {}
    dealflow_query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        sourcing_query["pilote"] = current_user.full_name
        dealflow_query["pilote"] = current_user.full_name

    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(10000)
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(10000)

    sourcing_with_docs = []
    dealflow_with_docs = []

    for partner in sourcing_partners:
        partner = normalize_doc(partner)
        partner_with_status = add_inactivity_status(partner)
        has_docs = False
        doc_types = []
        if partner.get("enriched_data") and len(partner["enriched_data"]) > 0:
            has_docs = True
            doc_types.append("Données enrichies")
        if partner.get("custom_fields") and len(partner["custom_fields"]) > 0:
            has_docs = True
            doc_types.append("Champs personnalisés")
        if has_docs:
            partner_with_status["document_types"] = doc_types
            sourcing_with_docs.append(partner_with_status)

    for partner in dealflow_partners:
        partner = normalize_doc(partner)
        partner_with_status = add_inactivity_status(partner)
        has_docs = False
        doc_types = []
        if partner.get("enriched_data") and len(partner["enriched_data"]) > 0:
            has_docs = True
            doc_types.append("Données enrichies")
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
        "summary": {"total": len(sourcing_with_docs) + len(dealflow_with_docs), "sourcing_count": len(sourcing_with_docs), "dealflow_count": len(dealflow_with_docs)}
    }


@api_router.get("/quick-views/en-experimentation")
async def get_startups_in_experimentation(user_id: str = "default_user"):
    current_user = await get_current_user(user_id)

    dealflow_query = {}
    if current_user.role == UserRole.CONTRIBUTEUR:
        dealflow_query["pilote"] = current_user.full_name

    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(10000)
    experimentation_statuses = ["Go experimentation", "Go généralisation", "En cours avec les métiers"]

    dealflow_in_exp = []
    for partner in dealflow_partners:
        partner = normalize_doc(partner)
        partner_with_status = add_inactivity_status(partner)
        status = partner.get("statut", "")
        if any(exp_status.lower() in status.lower() for exp_status in experimentation_statuses):
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
        "sourcing": [],
        "dealflow": dealflow_in_exp,
        "summary": {"total": len(dealflow_in_exp), "sourcing_count": 0, "dealflow_count": len(dealflow_in_exp)}
    }


@api_router.get("/global-search")
async def global_search(query: str, user_id: str = "default_user"):
    query = (query or "").strip()
    if len(query) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

    try:
        current_user = await get_current_user(user_id)
    except Exception:
        current_user = None

    query_lower = query.lower()
    sourcing_query: Dict[str, Any] = {}
    dealflow_query: Dict[str, Any] = {}

    try:
        if current_user and getattr(current_user, "role", None) == UserRole.CONTRIBUTEUR:
            sourcing_query["pilote"] = current_user.full_name
            dealflow_query["pilote"] = current_user.full_name
    except Exception:
        pass

    sourcing_partners = await db.sourcing_partners.find(sourcing_query).to_list(10000)
    dealflow_partners = await db.dealflow_partners.find(dealflow_query).to_list(10000)

    def matches_query(partner: Dict[str, Any], partner_type: str) -> bool:
        try:
            if partner_type == "sourcing":
                nom = (partner.get("nom_entreprise") or "").lower()
                domaine = (partner.get("domaine_activite") or "").lower()
            else:
                nom = (partner.get("nom") or "").lower()
                domaine = (partner.get("domaine") or "").lower()

            searchable_fields = [
                nom, domaine,
                (partner.get("pilote") or "").lower(),
                (partner.get("typologie") or "").lower(),
                (partner.get("source") or "").lower(),
                (partner.get("technologie") or "").lower(),
                (partner.get("pays_origine") or "").lower(),
            ]
            return any(query_lower in field for field in searchable_fields if field)
        except Exception:
            return False

    def safe_add_inactivity(partner: Dict[str, Any]) -> Dict[str, Any]:
        try:
            partner_copy = normalize_doc(dict(partner))
            return add_inactivity_status(partner_copy)
        except Exception:
            return normalize_doc(dict(partner))

    sourcing_matches = [safe_add_inactivity(p) for p in sourcing_partners if matches_query(p, "sourcing")]
    dealflow_matches = [safe_add_inactivity(p) for p in dealflow_partners if matches_query(p, "dealflow")]

    return clean_nans({
        "query": query,
        "sourcing": sourcing_matches,
        "dealflow": dealflow_matches,
        "summary": {
            "total": len(sourcing_matches) + len(dealflow_matches),
            "sourcing_count": len(sourcing_matches),
            "dealflow_count": len(dealflow_matches),
        },
    })

@api_router.get("/migrate-domains")
async def migrate_domains():
    """
    Migration unique : normalise les doublons de domaines et typologies
    dans les collections sourcing_partners et dealflow_partners.
    Peut être appelé plusieurs fois sans risque (idempotent).
    """
 
    results = {
        "sourcing_domaine": {},
        "dealflow_domaine": {},
        "sourcing_typologie": {},
        "dealflow_typologie": {},
        "total_corrections": 0
    }
 
    # ============================================================
    # 1. NORMALISATION DES DOMAINES
    # ============================================================
    domaine_corrections = {
        # Valeur incorrecte → Valeur correcte
        "Insurtech":    "InsurTech",
        "Fintech":      "FinTech",
        "Smarthome":    "SmartHome",
        "Cybersecurity":"CyberSecurity",
        "Martech":      "MarTech",
        "Regtech":      "RegTech",
    }
 
    # Sourcing — champ domaine_activite
    for incorrect, correct in domaine_corrections.items():
        result = await db.sourcing_partners.update_many(
            {"domaine_activite": incorrect},
            {"$set": {"domaine_activite": correct}}
        )
        if result.modified_count > 0:
            results["sourcing_domaine"][incorrect] = {
                "corrigé_en": correct,
                "nb_corrections": result.modified_count
            }
            results["total_corrections"] += result.modified_count
 
    # Dealflow — champ domaine
    for incorrect, correct in domaine_corrections.items():
        result = await db.dealflow_partners.update_many(
            {"domaine": incorrect},
            {"$set": {"domaine": correct}}
        )
        if result.modified_count > 0:
            results["dealflow_domaine"][incorrect] = {
                "corrigé_en": correct,
                "nb_corrections": result.modified_count
            }
            results["total_corrections"] += result.modified_count
 
    # ============================================================
    # 2. NORMALISATION DES TYPOLOGIES
    # ============================================================
    # Format : "valeur_incorrecte_en_base" → "valeur_correcte"
    # Les caractères mal encodés viennent d'un import CSV
    # où les accents n'étaient pas en UTF-8
    typologie_corrections = {
        # Casse / espaces
        "assurance":                "Assurance",
        "Assurance ":               "Assurance",
        "solution assurance":       "Solution Assurance",
        "Gestion sinistres":        "Gestion Sinistres",
        "Solution innovante":       "Solution Innovante",
        "Mutuelle ":                "Mutuelle",
        "Gestion innovation":       "Gestion Innovation",
        "Gestion des risques":      "Gestion des Risques",
        "Gestion risques":          "Gestion des Risques",
        "Solution RH ":             "Solution RH",
        "solution juridique":       "Solution Juridique",
        "Solution financire":       "Solution Financière",
        "Solution marketing":       "Solution Marketing",
        "Solution auto ":           "Solution Auto",
        "Communication mdicale":    "Communication Médicale",
        "Protection donnes":        "Protection Données",
        "Gestion immoblire":        "Gestion Immobilière",
 
        # Accents manquants (encodage cassé lors d'import CSV)
        "Prvention Climatique":     "Prévention Climatique",
        "Preuves Numriques":        "Preuves Numériques",
        "Preuves numriques":        "Preuves Numériques",
        "Avantages Employs ":       "Avantages Employés",
        "Prvention Sinistre":       "Prévention Sinistre",
        "Gestion Donnes":           "Gestion Données",
        "Sant Prventive":           "Santé Préventive",
        "Sant":                     "Santé",
        "Solution ducative":        "Solution Éducative",
        "Solution ducation":        "Solution Éducative",
        "Solution Financire":       "Solution Financière",
        "Exprience Client ":        "Expérience Client",
        "Transition cologique":     "Transition Écologique",
        "Gestion Rclamations":      "Gestion Réclamations",
        "Solution Mobilit":         "Solution Mobilité",
        "Communication Mdicale":    "Communication Médicale",
        "Protection Donnes":        "Protection Données",
        "Gestion Immobilire":       "Gestion Immobilière",
        "Assurance Numrique":       "Assurance Numérique",
        "Finance sant":             "Finance Santé",
        "Prise de note ":           "Prise de Note",
    }
 
    # Sourcing — champ typologie
    for incorrect, correct in typologie_corrections.items():
        result = await db.sourcing_partners.update_many(
            {"typologie": incorrect},
            {"$set": {"typologie": correct}}
        )
        if result.modified_count > 0:
            results["sourcing_typologie"][incorrect] = {
                "corrigé_en": correct,
                "nb_corrections": result.modified_count
            }
            results["total_corrections"] += result.modified_count
 
    # Dealflow — champ typologie
    for incorrect, correct in typologie_corrections.items():
        result = await db.dealflow_partners.update_many(
            {"typologie": incorrect},
            {"$set": {"typologie": correct}}
        )
        if result.modified_count > 0:
            results["dealflow_typologie"][incorrect] = {
                "corrigé_en": correct,
                "nb_corrections": result.modified_count
            }
            results["total_corrections"] += result.modified_count
 
    # ============================================================
    # 3. RÉSUMÉ
    # ============================================================
    results["message"] = (
        f"✅ Migration terminée : {results['total_corrections']} "
        f"corrections appliquées en base de données."
    )
    if results["total_corrections"] == 0:
        results["message"] = (
            "✅ Aucune correction nécessaire : "
            "les données sont déjà propres (migration déjà effectuée)."
        )
 
    return results

@api_router.get("/import-dealflow-history")
async def import_dealflow_history():
    import json, pathlib
    json_path = pathlib.Path(__file__).parent / "dealflow_import.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="Fichier dealflow_import.json introuvable")
    with open(json_path, encoding="utf-8") as f:
        docs = json.load(f)
    existing = set(
        d["nom"].strip().lower()
        for d in await db.dealflow_partners.find({}, {"nom": 1}).to_list(10000)
        if d.get("nom")
    )
    inserted, skipped = 0, 0
    for doc in docs:
        nom = doc.get("nom", "").strip()
        if not nom or nom.lower() in existing:
            skipped += 1
            continue
        await db.dealflow_partners.insert_one(doc)
        existing.add(nom.lower())
        inserted += 1
    return {"inserted": inserted, "skipped": skipped, "total": await db.dealflow_partners.count_documents({})}


@api_router.get("/fix-nat-dates")
async def fix_nat_dates():
    result = await db.dealflow_partners.update_many(
        {"date_reception_fichier": "NaT"},
        {"$set": {"date_reception_fichier": "2020-01-01"}}
    )
    return {"fixed": result.modified_count}


app.include_router(api_router)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
