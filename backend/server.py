from fastapi import FastAPI, APIRouter, HTTPException, Body
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date
from enum import Enum


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

# Models for Sourcing
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

# Models for Dealflow
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

# SOURCING ENDPOINTS
@api_router.post("/sourcing", response_model=SourcingPartner)
async def create_sourcing_partner(partner: SourcingPartnerCreate):
    partner_dict = partner.dict()
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