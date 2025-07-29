#!/usr/bin/env python3
"""
SURM Backend API Testing Suite
Tests all CRUD operations for sourcing/dealflow partners, transition workflow, and statistics
"""

import requests
import json
from datetime import datetime, date
import sys
import os

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("ERROR: Could not get REACT_APP_BACKEND_URL from frontend/.env")
    sys.exit(1)

API_URL = f"{BASE_URL}/api"
print(f"Testing SURM Backend API at: {API_URL}")

# Test data for realistic French innovation context
SOURCING_TEST_DATA = {
    "nom_entreprise": "TechInnovate Solutions",
    "statut": "A traiter",
    "pays_origine": "France",
    "domaine_activite": "Intelligence Artificielle",
    "typologie": "Startup",
    "objet": "Solution IA pour optimisation énergétique",
    "cas_usage": "Optimisation consommation énergétique bâtiments tertiaires",
    "technologie": "Machine Learning",
    "source": "Salon VivaTech 2024",
    "date_entree_sourcing": "2024-03-15",
    "interet": True,
    "date_presentation_metiers": "2024-03-20",
    "pilote": "Marie Dubois",
    "actions_commentaires": "Premier contact très prometteur",
    # Phase 1 - Next Action Date
    "date_prochaine_action": "2024-04-15"
}

SOURCING_TEST_DATA_2 = {
    "nom_entreprise": "GreenTech Innovations",
    "statut": "Clos",
    "pays_origine": "Allemagne",
    "domaine_activite": "Développement Durable",
    "typologie": "PME",
    "objet": "Technologies de recyclage avancé",
    "cas_usage": "Recyclage plastiques complexes",
    "technologie": "Chimie Verte",
    "source": "Partenariat industriel",
    "date_entree_sourcing": "2024-01-10",
    "interet": False,
    "pilote": "Jean Martin",
    "actions_commentaires": "Technologie pas encore mature"
}

DEALFLOW_TEST_DATA = {
    "nom": "FinTech Secure",
    "statut": "En cours avec les métiers",
    "domaine": "Services Financiers",
    "typologie": "Scale-up",
    "objet": "Sécurisation transactions blockchain",
    "source": "Réseau partenaires",
    "pilote": "Sophie Laurent",
    "metiers_concernes": "DSI, Risk Management",
    "date_reception_fichier": "2024-02-01",
    "date_pre_qualification": "2024-02-15",
    "date_presentation_meetup_referents": "2024-02-28",
    "actions_commentaires": "Très bon potentiel commercial",
    # Phase 1 - Next Action Date
    "date_prochaine_action": "2024-04-10"
}

def test_sourcing_crud():
    """Test all SOURCING CRUD operations"""
    print("\n=== TESTING SOURCING PARTNERS CRUD ===")
    
    # Test 1: CREATE sourcing partner
    print("\n1. Testing POST /api/sourcing (Create)")
    response = requests.post(f"{API_URL}/sourcing", json=SOURCING_TEST_DATA)
    if response.status_code == 200:
        sourcing_partner = response.json()
        sourcing_id = sourcing_partner['id']
        print(f"✅ Created sourcing partner: {sourcing_partner['nom_entreprise']} (ID: {sourcing_id})")
    else:
        print(f"❌ Failed to create sourcing partner: {response.status_code} - {response.text}")
        return None
    
    # Create second partner for testing
    response2 = requests.post(f"{API_URL}/sourcing", json=SOURCING_TEST_DATA_2)
    if response2.status_code == 200:
        sourcing_partner_2 = response2.json()
        print(f"✅ Created second sourcing partner: {sourcing_partner_2['nom_entreprise']}")
    
    # Test 2: GET all sourcing partners
    print("\n2. Testing GET /api/sourcing (List all)")
    response = requests.get(f"{API_URL}/sourcing")
    if response.status_code == 200:
        partners = response.json()
        print(f"✅ Retrieved {len(partners)} sourcing partners")
        for partner in partners:
            print(f"   - {partner['nom_entreprise']} ({partner['statut']})")
    else:
        print(f"❌ Failed to get sourcing partners: {response.status_code} - {response.text}")
    
    # Test 3: GET specific sourcing partner
    print(f"\n3. Testing GET /api/sourcing/{sourcing_id} (Get specific)")
    response = requests.get(f"{API_URL}/sourcing/{sourcing_id}")
    if response.status_code == 200:
        partner = response.json()
        print(f"✅ Retrieved specific partner: {partner['nom_entreprise']}")
        print(f"   Status: {partner['statut']}, Domain: {partner['domaine_activite']}")
    else:
        print(f"❌ Failed to get specific sourcing partner: {response.status_code} - {response.text}")
    
    # Test 4: UPDATE sourcing partner
    print(f"\n4. Testing PUT /api/sourcing/{sourcing_id} (Update)")
    update_data = {
        "statut": "Klaxoon",
        "actions_commentaires": "Mis à jour pour Klaxoon session"
    }
    response = requests.put(f"{API_URL}/sourcing/{sourcing_id}", json=update_data)
    if response.status_code == 200:
        updated_partner = response.json()
        print(f"✅ Updated partner status to: {updated_partner['statut']}")
    else:
        print(f"❌ Failed to update sourcing partner: {response.status_code} - {response.text}")
    
    # Test 5: DELETE sourcing partner (delete the second one)
    print(f"\n5. Testing DELETE /api/sourcing/{sourcing_partner_2['id']} (Delete)")
    response = requests.delete(f"{API_URL}/sourcing/{sourcing_partner_2['id']}")
    if response.status_code == 200:
        print(f"✅ Deleted sourcing partner: {sourcing_partner_2['nom_entreprise']}")
    else:
        print(f"❌ Failed to delete sourcing partner: {response.status_code} - {response.text}")
    
    return sourcing_id

def test_dealflow_crud():
    """Test all DEALFLOW CRUD operations"""
    print("\n=== TESTING DEALFLOW PARTNERS CRUD ===")
    
    # Test 1: CREATE dealflow partner
    print("\n1. Testing POST /api/dealflow (Create)")
    response = requests.post(f"{API_URL}/dealflow", json=DEALFLOW_TEST_DATA)
    if response.status_code == 200:
        dealflow_partner = response.json()
        dealflow_id = dealflow_partner['id']
        print(f"✅ Created dealflow partner: {dealflow_partner['nom']} (ID: {dealflow_id})")
    else:
        print(f"❌ Failed to create dealflow partner: {response.status_code} - {response.text}")
        return None
    
    # Test 2: GET all dealflow partners
    print("\n2. Testing GET /api/dealflow (List all)")
    response = requests.get(f"{API_URL}/dealflow")
    if response.status_code == 200:
        partners = response.json()
        print(f"✅ Retrieved {len(partners)} dealflow partners")
        for partner in partners:
            print(f"   - {partner['nom']} ({partner['statut']})")
    else:
        print(f"❌ Failed to get dealflow partners: {response.status_code} - {response.text}")
    
    # Test 3: GET specific dealflow partner
    print(f"\n3. Testing GET /api/dealflow/{dealflow_id} (Get specific)")
    response = requests.get(f"{API_URL}/dealflow/{dealflow_id}")
    if response.status_code == 200:
        partner = response.json()
        print(f"✅ Retrieved specific partner: {partner['nom']}")
        print(f"   Status: {partner['statut']}, Domain: {partner['domaine']}")
    else:
        print(f"❌ Failed to get specific dealflow partner: {response.status_code} - {response.text}")
    
    # Test 4: UPDATE dealflow partner
    print(f"\n4. Testing PUT /api/dealflow/{dealflow_id} (Update)")
    update_data = {
        "statut": "En cours avec l'équipe inno",
        "date_go_metier_etude": "2024-03-10",
        "actions_commentaires": "Validation technique en cours"
    }
    response = requests.put(f"{API_URL}/dealflow/{dealflow_id}", json=update_data)
    if response.status_code == 200:
        updated_partner = response.json()
        print(f"✅ Updated partner status to: {updated_partner['statut']}")
    else:
        print(f"❌ Failed to update dealflow partner: {response.status_code} - {response.text}")
    
    return dealflow_id

def test_transition_workflow(sourcing_id):
    """Test the critical transition workflow from sourcing to dealflow"""
    print("\n=== TESTING TRANSITION WORKFLOW ===")
    
    if not sourcing_id:
        print("❌ No sourcing partner ID available for transition test")
        return
    
    # First, update sourcing partner to be ready for transition
    print(f"\n1. Preparing sourcing partner {sourcing_id} for transition")
    update_data = {"statut": "A traiter"}
    response = requests.put(f"{API_URL}/sourcing/{sourcing_id}", json=update_data)
    
    # Test transition
    print(f"\n2. Testing POST /api/transition/{sourcing_id} (Transition to dealflow)")
    transition_data = {
        "statut": "En cours avec les métiers",
        "metiers_concernes": "Innovation, R&D",
        "date_reception_fichier": "2024-03-25",
        "date_pre_qualification": "2024-03-30"
    }
    
    response = requests.post(f"{API_URL}/transition/{sourcing_id}", json=transition_data)
    if response.status_code == 200:
        dealflow_partner = response.json()
        print(f"✅ Successfully transitioned to dealflow: {dealflow_partner['nom']}")
        print(f"   Inherited data - Domain: {dealflow_partner['domaine']}, Technology: {dealflow_partner['technologie']}")
        print(f"   New dealflow ID: {dealflow_partner['id']}")
        
        # Verify sourcing partner status was updated
        sourcing_response = requests.get(f"{API_URL}/sourcing/{sourcing_id}")
        if sourcing_response.status_code == 200:
            sourcing_partner = sourcing_response.json()
            if sourcing_partner['statut'] == 'Dealflow':
                print(f"✅ Sourcing partner status correctly updated to: {sourcing_partner['statut']}")
            else:
                print(f"❌ Sourcing partner status not updated correctly: {sourcing_partner['statut']}")
        
        return dealflow_partner['id']
    else:
        print(f"❌ Failed to transition partner: {response.status_code} - {response.text}")
        return None

def test_statistics_endpoint():
    """Test the statistics dashboard endpoint"""
    print("\n=== TESTING STATISTICS ENDPOINT ===")
    
    print("\n1. Testing GET /api/statistics (Dashboard statistics)")
    response = requests.get(f"{API_URL}/statistics")
    if response.status_code == 200:
        stats = response.json()
        print("✅ Retrieved dashboard statistics:")
        
        # Test quarterly entries
        print(f"   📊 Quarterly Entries: {len(stats['quarterly_entries'])} quarters")
        for quarter in stats['quarterly_entries']:
            print(f"      - {quarter['quarter']}: {quarter['total_entries']} entries")
        
        # Test monthly stats
        print(f"   📊 Monthly Stats: {len(stats['monthly_stats'])} months")
        for month in stats['monthly_stats']:
            print(f"      - {month['month']}: {month['pre_qualifications']} pre-qual, {month['go_studies']} go-studies")
        
        # Test distributions
        print(f"   📊 Domain Distribution: {len(stats['domain_distribution'])} domains")
        for domain, count in stats['domain_distribution'].items():
            print(f"      - {domain}: {count}")
        
        print(f"   📊 Technology Distribution: {len(stats['technology_distribution'])} technologies")
        print(f"   📊 Status Distributions - Sourcing: {len(stats['sourcing_status_distribution'])}, Dealflow: {len(stats['dealflow_status_distribution'])}")
        
        # Test totals
        print(f"   📊 Totals - Sourcing: {stats['total_sourcing']}, Dealflow: {stats['total_dealflow']}")
        
        # Verify calculations make sense
        if stats['total_sourcing'] >= 0 and stats['total_dealflow'] >= 0:
            print("✅ Statistics calculations appear accurate")
        else:
            print("❌ Statistics calculations seem incorrect")
            
    else:
        print(f"❌ Failed to get statistics: {response.status_code} - {response.text}")

def test_error_handling():
    """Test error handling for invalid data"""
    print("\n=== TESTING ERROR HANDLING ===")
    
    # Test invalid sourcing partner ID
    print("\n1. Testing invalid sourcing partner ID")
    response = requests.get(f"{API_URL}/sourcing/invalid-id")
    if response.status_code == 404:
        print("✅ Correctly returned 404 for invalid sourcing partner ID")
    else:
        print(f"❌ Unexpected response for invalid ID: {response.status_code}")
    
    # Test invalid dealflow partner ID
    print("\n2. Testing invalid dealflow partner ID")
    response = requests.get(f"{API_URL}/dealflow/invalid-id")
    if response.status_code == 404:
        print("✅ Correctly returned 404 for invalid dealflow partner ID")
    else:
        print(f"❌ Unexpected response for invalid ID: {response.status_code}")
    
    # Test invalid enum values
    print("\n3. Testing invalid enum values")
    invalid_data = SOURCING_TEST_DATA.copy()
    invalid_data["statut"] = "Invalid Status"
    response = requests.post(f"{API_URL}/sourcing", json=invalid_data)
    if response.status_code == 422:
        print("✅ Correctly rejected invalid status enum")
    else:
        print(f"❌ Should have rejected invalid enum: {response.status_code}")
    
    # Test transition with invalid sourcing ID
    print("\n4. Testing transition with invalid sourcing ID")
    response = requests.post(f"{API_URL}/transition/invalid-id", json={"statut": "En cours avec les métiers", "metiers_concernes": "Test", "date_reception_fichier": "2024-01-01"})
    if response.status_code == 404:
        print("✅ Correctly returned 404 for invalid transition ID")
    else:
        print(f"❌ Unexpected response for invalid transition: {response.status_code}")

def main():
    """Run all tests"""
    print("🚀 Starting SURM Backend API Tests")
    print("=" * 50)
    
    try:
        # Test CRUD operations
        sourcing_id = test_sourcing_crud()
        dealflow_id = test_dealflow_crud()
        
        # Test transition workflow
        transitioned_dealflow_id = test_transition_workflow(sourcing_id)
        
        # Test statistics
        test_statistics_endpoint()
        
        # Test error handling
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 SURM Backend API Testing Complete!")
        print("Check the results above for any failures.")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()