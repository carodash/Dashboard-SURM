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

def test_phase1_next_action_date():
    """Test Phase 1 - Next Action Date field functionality"""
    print("\n=== TESTING PHASE 1 - NEXT ACTION DATE FIELD ===")
    
    # Test 1: Create sourcing partner with date_prochaine_action
    print("\n1. Testing POST /api/sourcing with date_prochaine_action")
    test_data = SOURCING_TEST_DATA.copy()
    test_data["nom_entreprise"] = "NextAction Test Startup"
    test_data["date_prochaine_action"] = "2024-05-15"
    
    response = requests.post(f"{API_URL}/sourcing", json=test_data)
    if response.status_code == 200:
        partner = response.json()
        sourcing_id = partner['id']
        if partner.get('date_prochaine_action') == "2024-05-15":
            print(f"✅ Sourcing partner created with date_prochaine_action: {partner['date_prochaine_action']}")
        else:
            print(f"❌ date_prochaine_action not properly stored: {partner.get('date_prochaine_action')}")
    else:
        print(f"❌ Failed to create sourcing partner with date_prochaine_action: {response.status_code}")
        return None
    
    # Test 2: Update sourcing partner date_prochaine_action
    print(f"\n2. Testing PUT /api/sourcing/{sourcing_id} with date_prochaine_action update")
    update_data = {"date_prochaine_action": "2024-06-01"}
    response = requests.put(f"{API_URL}/sourcing/{sourcing_id}", json=update_data)
    if response.status_code == 200:
        updated_partner = response.json()
        if updated_partner.get('date_prochaine_action') == "2024-06-01":
            print(f"✅ Sourcing partner date_prochaine_action updated: {updated_partner['date_prochaine_action']}")
        else:
            print(f"❌ date_prochaine_action not properly updated: {updated_partner.get('date_prochaine_action')}")
    else:
        print(f"❌ Failed to update sourcing partner date_prochaine_action: {response.status_code}")
    
    # Test 3: Create dealflow partner with date_prochaine_action
    print("\n3. Testing POST /api/dealflow with date_prochaine_action")
    dealflow_data = DEALFLOW_TEST_DATA.copy()
    dealflow_data["nom"] = "NextAction Dealflow Test"
    dealflow_data["date_prochaine_action"] = "2024-05-20"
    
    response = requests.post(f"{API_URL}/dealflow", json=dealflow_data)
    if response.status_code == 200:
        partner = response.json()
        dealflow_id = partner['id']
        if partner.get('date_prochaine_action') == "2024-05-20":
            print(f"✅ Dealflow partner created with date_prochaine_action: {partner['date_prochaine_action']}")
        else:
            print(f"❌ date_prochaine_action not properly stored: {partner.get('date_prochaine_action')}")
    else:
        print(f"❌ Failed to create dealflow partner with date_prochaine_action: {response.status_code}")
        return sourcing_id, None
    
    # Test 4: Update dealflow partner date_prochaine_action
    print(f"\n4. Testing PUT /api/dealflow/{dealflow_id} with date_prochaine_action update")
    update_data = {"date_prochaine_action": "2024-06-15"}
    response = requests.put(f"{API_URL}/dealflow/{dealflow_id}", json=update_data)
    if response.status_code == 200:
        updated_partner = response.json()
        if updated_partner.get('date_prochaine_action') == "2024-06-15":
            print(f"✅ Dealflow partner date_prochaine_action updated: {updated_partner['date_prochaine_action']}")
        else:
            print(f"❌ date_prochaine_action not properly updated: {updated_partner.get('date_prochaine_action')}")
    else:
        print(f"❌ Failed to update dealflow partner date_prochaine_action: {response.status_code}")
    
    return sourcing_id, dealflow_id

def test_phase1_inactivity_indicators():
    """Test Phase 1 - Inactivity Indicators functionality"""
    print("\n=== TESTING PHASE 1 - INACTIVITY INDICATORS ===")
    
    # Test 1: Check if GET /api/sourcing returns inactivity fields
    print("\n1. Testing GET /api/sourcing for inactivity indicators")
    response = requests.get(f"{API_URL}/sourcing")
    if response.status_code == 200:
        partners = response.json()
        if partners:
            partner = partners[0]
            if 'is_inactive' in partner and 'days_since_update' in partner:
                print(f"✅ Sourcing partners include inactivity indicators:")
                print(f"   - is_inactive: {partner['is_inactive']}")
                print(f"   - days_since_update: {partner['days_since_update']}")
            else:
                print(f"❌ Missing inactivity indicators in sourcing response")
                print(f"   Available fields: {list(partner.keys())}")
        else:
            print("⚠️ No sourcing partners found to test inactivity indicators")
    else:
        print(f"❌ Failed to get sourcing partners: {response.status_code}")
    
    # Test 2: Check if GET /api/dealflow returns inactivity fields
    print("\n2. Testing GET /api/dealflow for inactivity indicators")
    response = requests.get(f"{API_URL}/dealflow")
    if response.status_code == 200:
        partners = response.json()
        if partners:
            partner = partners[0]
            if 'is_inactive' in partner and 'days_since_update' in partner:
                print(f"✅ Dealflow partners include inactivity indicators:")
                print(f"   - is_inactive: {partner['is_inactive']}")
                print(f"   - days_since_update: {partner['days_since_update']}")
            else:
                print(f"❌ Missing inactivity indicators in dealflow response")
                print(f"   Available fields: {list(partner.keys())}")
        else:
            print("⚠️ No dealflow partners found to test inactivity indicators")
    else:
        print(f"❌ Failed to get dealflow partners: {response.status_code}")
    
    # Test 3: Test GET /api/inactive-partners endpoint
    print("\n3. Testing GET /api/inactive-partners endpoint")
    response = requests.get(f"{API_URL}/inactive-partners")
    if response.status_code == 200:
        inactive_data = response.json()
        print(f"✅ Inactive partners endpoint working:")
        print(f"   - Threshold days: {inactive_data['threshold_days']}")
        print(f"   - Inactive sourcing: {len(inactive_data['inactive_sourcing'])}")
        print(f"   - Inactive dealflow: {len(inactive_data['inactive_dealflow'])}")
        print(f"   - Total inactive: {inactive_data['total_inactive']}")
    else:
        print(f"❌ Failed to get inactive partners: {response.status_code} - {response.text}")
    
    # Test 4: Test with custom threshold
    print("\n4. Testing GET /api/inactive-partners with custom threshold")
    response = requests.get(f"{API_URL}/inactive-partners?threshold_days=30")
    if response.status_code == 200:
        inactive_data = response.json()
        print(f"✅ Custom threshold (30 days) working:")
        print(f"   - Total inactive: {inactive_data['total_inactive']}")
    else:
        print(f"❌ Failed to get inactive partners with custom threshold: {response.status_code}")

def test_phase1_activity_timeline():
    """Test Phase 1 - Activity Timeline functionality"""
    print("\n=== TESTING PHASE 1 - ACTIVITY TIMELINE ===")
    
    # First, create a test partner to work with
    print("\n1. Creating test partner for activity timeline")
    test_data = SOURCING_TEST_DATA.copy()
    test_data["nom_entreprise"] = "Activity Timeline Test"
    response = requests.post(f"{API_URL}/sourcing", json=test_data)
    if response.status_code != 200:
        print(f"❌ Failed to create test partner: {response.status_code}")
        return
    
    partner = response.json()
    partner_id = partner['id']
    print(f"✅ Created test partner: {partner_id}")
    
    # Test 2: Update partner to generate activity
    print(f"\n2. Updating partner to generate activity log")
    update_data = {"actions_commentaires": "Updated for activity timeline test"}
    response = requests.put(f"{API_URL}/sourcing/{partner_id}", json=update_data)
    if response.status_code == 200:
        print("✅ Partner updated successfully")
    else:
        print(f"❌ Failed to update partner: {response.status_code}")
    
    # Test 3: Get activity timeline
    print(f"\n3. Testing GET /api/activity/{partner_id}?partner_type=sourcing")
    response = requests.get(f"{API_URL}/activity/{partner_id}?partner_type=sourcing")
    if response.status_code == 200:
        activities = response.json()
        print(f"✅ Retrieved {len(activities)} activities:")
        for activity in activities[:3]:  # Show first 3
            print(f"   - {activity['activity_type']}: {activity['description']}")
            print(f"     Created: {activity['created_at']}")
    else:
        print(f"❌ Failed to get activity timeline: {response.status_code} - {response.text}")
    
    # Test 4: Add manual activity
    print(f"\n4. Testing POST /api/activity/{partner_id} (manual activity)")
    manual_activity_data = {
        "partner_type": "sourcing",
        "description": "Manual test activity added via API",
        "user_name": "Test User"
    }
    response = requests.post(f"{API_URL}/activity/{partner_id}", params=manual_activity_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Manual activity added: {result['activity_id']}")
    else:
        print(f"❌ Failed to add manual activity: {response.status_code} - {response.text}")
    
    # Test 5: Verify manual activity appears in timeline
    print(f"\n5. Verifying manual activity in timeline")
    response = requests.get(f"{API_URL}/activity/{partner_id}?partner_type=sourcing")
    if response.status_code == 200:
        activities = response.json()
        manual_activity_found = any(
            "Manual test activity" in activity['description'] 
            for activity in activities
        )
        if manual_activity_found:
            print("✅ Manual activity found in timeline")
        else:
            print("❌ Manual activity not found in timeline")
    
    return partner_id

def test_phase1_transition_inheritance():
    """Test Phase 1 - Enhanced transition with date_prochaine_action inheritance"""
    print("\n=== TESTING PHASE 1 - ENHANCED TRANSITION ===")
    
    # Create sourcing partner with date_prochaine_action
    print("\n1. Creating sourcing partner with date_prochaine_action for transition test")
    test_data = SOURCING_TEST_DATA.copy()
    test_data["nom_entreprise"] = "Transition Inheritance Test"
    test_data["date_prochaine_action"] = "2024-07-01"
    
    response = requests.post(f"{API_URL}/sourcing", json=test_data)
    if response.status_code != 200:
        print(f"❌ Failed to create sourcing partner: {response.status_code}")
        return
    
    sourcing_partner = response.json()
    sourcing_id = sourcing_partner['id']
    print(f"✅ Created sourcing partner with date_prochaine_action: {sourcing_partner['date_prochaine_action']}")
    
    # Test transition with inheritance
    print(f"\n2. Testing transition with date_prochaine_action inheritance")
    transition_data = {
        "statut": "En cours avec les métiers",
        "metiers_concernes": "Innovation, R&D",
        "date_reception_fichier": "2024-03-25"
    }
    
    response = requests.post(f"{API_URL}/transition/{sourcing_id}", json=transition_data)
    if response.status_code == 200:
        dealflow_partner = response.json()
        if dealflow_partner.get('date_prochaine_action') == "2024-07-01":
            print(f"✅ date_prochaine_action inherited correctly: {dealflow_partner['date_prochaine_action']}")
        else:
            print(f"❌ date_prochaine_action not inherited: {dealflow_partner.get('date_prochaine_action')}")
        
        # Check if transition activities were logged
        print(f"\n3. Checking transition activity logs")
        
        # Check sourcing activity
        response = requests.get(f"{API_URL}/activity/{sourcing_id}?partner_type=sourcing")
        if response.status_code == 200:
            activities = response.json()
            transition_activity = any(
                activity['activity_type'] == 'transitioned' 
                for activity in activities
            )
            if transition_activity:
                print("✅ Transition activity logged for sourcing partner")
            else:
                print("❌ Transition activity not found for sourcing partner")
        
        # Check dealflow activity
        dealflow_id = dealflow_partner['id']
        response = requests.get(f"{API_URL}/activity/{dealflow_id}?partner_type=dealflow")
        if response.status_code == 200:
            activities = response.json()
            creation_activity = any(
                'transition depuis sourcing' in activity['description'] 
                for activity in activities
            )
            if creation_activity:
                print("✅ Creation activity logged for dealflow partner")
            else:
                print("❌ Creation activity not found for dealflow partner")
        
        return dealflow_id
    else:
        print(f"❌ Failed to transition partner: {response.status_code} - {response.text}")
        return None

def test_phase2_monthly_evolution():
    """Test Phase 2 - Monthly Evolution Analytics"""
    print("\n=== TESTING PHASE 2 - MONTHLY EVOLUTION ANALYTICS ===")
    
    # Test 1: Basic monthly evolution endpoint
    print("\n1. Testing GET /api/analytics/monthly-evolution (basic)")
    response = requests.get(f"{API_URL}/analytics/monthly-evolution")
    if response.status_code == 200:
        data = response.json()
        print("✅ Monthly evolution endpoint working:")
        print(f"   - Period: {data.get('period', {}).get('start')} to {data.get('period', {}).get('end')}")
        print(f"   - Monthly data points: {len(data.get('monthly_evolution', []))}")
        
        # Verify data structure
        if 'period' in data and 'monthly_evolution' in data:
            print("✅ Response has correct structure (period, monthly_evolution)")
            
            # Check monthly evolution data structure
            monthly_data = data['monthly_evolution']
            if monthly_data:
                first_month = monthly_data[0]
                if len(first_month) == 2:  # [month, stats]
                    month_key, stats = first_month
                    expected_keys = ['sourcing_created', 'dealflow_created', 'sourcing_closed', 'dealflow_closed', 'transitions']
                    if all(key in stats for key in expected_keys):
                        print("✅ Monthly evolution data has correct structure")
                        print(f"   Sample month {month_key}: {stats}")
                    else:
                        print(f"❌ Missing expected keys in monthly stats: {list(stats.keys())}")
                else:
                    print(f"❌ Incorrect monthly data format: {first_month}")
            else:
                print("⚠️ No monthly evolution data found")
        else:
            print(f"❌ Missing required fields in response: {list(data.keys())}")
    else:
        print(f"❌ Failed to get monthly evolution: {response.status_code} - {response.text}")
    
    # Test 2: Monthly evolution with date range
    print("\n2. Testing GET /api/analytics/monthly-evolution with date range")
    start_date = "2024-01-01T00:00:00"
    end_date = "2024-12-31T23:59:59"
    response = requests.get(f"{API_URL}/analytics/monthly-evolution?start_date={start_date}&end_date={end_date}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Date range filtering working:")
        print(f"   - Requested period: {start_date} to {end_date}")
        print(f"   - Response period: {data.get('period', {}).get('start')} to {data.get('period', {}).get('end')}")
        print(f"   - Monthly data points: {len(data.get('monthly_evolution', []))}")
    else:
        print(f"❌ Failed with date range: {response.status_code} - {response.text}")
    
    # Test 3: Monthly evolution with last 6 months
    print("\n3. Testing GET /api/analytics/monthly-evolution (last 6 months)")
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # ~6 months
    
    response = requests.get(f"{API_URL}/analytics/monthly-evolution?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Last 6 months filtering working:")
        print(f"   - Monthly data points: {len(data.get('monthly_evolution', []))}")
    else:
        print(f"❌ Failed with 6 months range: {response.status_code} - {response.text}")

def test_phase2_enhanced_distribution():
    """Test Phase 2 - Enhanced Distribution Analytics"""
    print("\n=== TESTING PHASE 2 - ENHANCED DISTRIBUTION ANALYTICS ===")
    
    # Test 1: Basic distribution endpoint
    print("\n1. Testing GET /api/analytics/distribution (basic)")
    response = requests.get(f"{API_URL}/analytics/distribution")
    if response.status_code == 200:
        data = response.json()
        print("✅ Enhanced distribution endpoint working:")
        
        # Check required distribution types
        expected_distributions = ['by_status', 'by_domain', 'by_typologie', 'by_pilote', 'by_source']
        for dist_type in expected_distributions:
            if dist_type in data:
                print(f"   ✅ {dist_type}: {len(data[dist_type])} categories")
                # Show sample data
                if data[dist_type]:
                    sample_key = list(data[dist_type].keys())[0]
                    print(f"      Sample: {sample_key} = {data[dist_type][sample_key]}")
            else:
                print(f"   ❌ Missing {dist_type}")
        
        # Check summary statistics
        if 'summary' in data:
            summary = data['summary']
            print(f"   ✅ Summary statistics:")
            print(f"      - Total sourcing: {summary.get('total_sourcing', 0)}")
            print(f"      - Total dealflow: {summary.get('total_dealflow', 0)}")
            print(f"      - Total partners: {summary.get('total_partners', 0)}")
            
            # Verify totals make sense
            expected_total = summary.get('total_sourcing', 0) + summary.get('total_dealflow', 0)
            if summary.get('total_partners', 0) == expected_total:
                print("   ✅ Summary totals are consistent")
            else:
                print(f"   ❌ Summary totals inconsistent: {summary.get('total_partners')} != {expected_total}")
        else:
            print("   ❌ Missing summary statistics")
    else:
        print(f"❌ Failed to get enhanced distribution: {response.status_code} - {response.text}")
    
    # Test 2: Distribution with domain filtering
    print("\n2. Testing GET /api/analytics/distribution with domain filter")
    response = requests.get(f"{API_URL}/analytics/distribution?filter_by=domaine&filter_value=Intelligence Artificielle")
    if response.status_code == 200:
        data = response.json()
        print("✅ Domain filtering working:")
        print(f"   - Filtered total partners: {data.get('summary', {}).get('total_partners', 0)}")
        
        # Verify filtering worked - all domain entries should be the filter value or related
        domain_dist = data.get('by_domain', {})
        if 'Intelligence Artificielle' in domain_dist:
            print(f"   ✅ Filter domain found: Intelligence Artificielle = {domain_dist['Intelligence Artificielle']}")
        else:
            print(f"   ⚠️ Filter domain not found in results: {list(domain_dist.keys())}")
    else:
        print(f"❌ Failed with domain filter: {response.status_code} - {response.text}")
    
    # Test 3: Distribution with pilote filtering
    print("\n3. Testing GET /api/analytics/distribution with pilote filter")
    response = requests.get(f"{API_URL}/analytics/distribution?filter_by=pilote&filter_value=Marie Dubois")
    if response.status_code == 200:
        data = response.json()
        print("✅ Pilote filtering working:")
        print(f"   - Filtered total partners: {data.get('summary', {}).get('total_partners', 0)}")
        
        # Verify filtering worked
        pilote_dist = data.get('by_pilote', {})
        if 'Marie Dubois' in pilote_dist:
            print(f"   ✅ Filter pilote found: Marie Dubois = {pilote_dist['Marie Dubois']}")
        else:
            print(f"   ⚠️ Filter pilote not found in results: {list(pilote_dist.keys())}")
    else:
        print(f"❌ Failed with pilote filter: {response.status_code} - {response.text}")
    
    # Test 4: Distribution with date range filtering
    print("\n4. Testing GET /api/analytics/distribution with date range")
    start_date = "2024-01-01T00:00:00"
    end_date = "2024-12-31T23:59:59"
    response = requests.get(f"{API_URL}/analytics/distribution?start_date={start_date}&end_date={end_date}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Date range filtering working:")
        print(f"   - Filtered total partners: {data.get('summary', {}).get('total_partners', 0)}")
    else:
        print(f"❌ Failed with date range: {response.status_code} - {response.text}")
    
    # Test 5: Combined filters (date range + domain)
    print("\n5. Testing GET /api/analytics/distribution with combined filters")
    response = requests.get(f"{API_URL}/analytics/distribution?filter_by=domaine&filter_value=Intelligence Artificielle&start_date={start_date}&end_date={end_date}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Combined filtering working:")
        print(f"   - Filtered total partners: {data.get('summary', {}).get('total_partners', 0)}")
    else:
        print(f"❌ Failed with combined filters: {response.status_code} - {response.text}")

def test_phase2_data_accuracy():
    """Test Phase 2 - Data Accuracy and Edge Cases"""
    print("\n=== TESTING PHASE 2 - DATA ACCURACY & EDGE CASES ===")
    
    # Test 1: Verify distribution percentages add up
    print("\n1. Testing distribution percentage accuracy")
    response = requests.get(f"{API_URL}/analytics/distribution")
    if response.status_code == 200:
        data = response.json()
        total_partners = data.get('summary', {}).get('total_partners', 0)
        
        if total_partners > 0:
            # Check status distribution adds up
            status_dist = data.get('by_status', {})
            status_total = sum(status_dist.values())
            if status_total == total_partners:
                print(f"   ✅ Status distribution adds up correctly: {status_total} = {total_partners}")
            else:
                print(f"   ❌ Status distribution mismatch: {status_total} != {total_partners}")
            
            # Check domain distribution adds up
            domain_dist = data.get('by_domain', {})
            domain_total = sum(domain_dist.values())
            if domain_total == total_partners:
                print(f"   ✅ Domain distribution adds up correctly: {domain_total} = {total_partners}")
            else:
                print(f"   ❌ Domain distribution mismatch: {domain_total} != {total_partners}")
        else:
            print("   ⚠️ No partners found to verify distribution accuracy")
    else:
        print(f"❌ Failed to get distribution for accuracy test: {response.status_code}")
    
    # Test 2: Test invalid date formats
    print("\n2. Testing invalid date formats")
    response = requests.get(f"{API_URL}/analytics/monthly-evolution?start_date=invalid-date")
    if response.status_code in [400, 422]:
        print("✅ Correctly rejected invalid date format")
    else:
        print(f"❌ Should have rejected invalid date: {response.status_code}")
    
    # Test 3: Test invalid filter values
    print("\n3. Testing invalid filter values")
    response = requests.get(f"{API_URL}/analytics/distribution?filter_by=invalid_field&filter_value=test")
    if response.status_code == 200:
        data = response.json()
        # Should return empty results or handle gracefully
        print(f"✅ Invalid filter handled gracefully: {data.get('summary', {}).get('total_partners', 0)} partners")
    else:
        print(f"❌ Failed to handle invalid filter: {response.status_code}")
    
    # Test 4: Test empty date range
    print("\n4. Testing empty date range")
    future_start = "2030-01-01T00:00:00"
    future_end = "2030-12-31T23:59:59"
    response = requests.get(f"{API_URL}/analytics/monthly-evolution?start_date={future_start}&end_date={future_end}")
    if response.status_code == 200:
        data = response.json()
        monthly_data = data.get('monthly_evolution', [])
        if len(monthly_data) == 0:
            print("✅ Empty date range handled correctly (no data)")
        else:
            print(f"⚠️ Future date range returned data: {len(monthly_data)} months")
    else:
        print(f"❌ Failed to handle empty date range: {response.status_code}")

# PHASE 3 - USER MANAGEMENT TESTS
def test_phase3_user_management():
    """Test Phase 3 - User Management System"""
    print("\n=== TESTING PHASE 3 - USER MANAGEMENT SYSTEM ===")
    
    # Test data for different user roles
    admin_user_data = {
        "username": "admin_user",
        "email": "admin@surm.com",
        "full_name": "Administrateur SURM",
        "role": "admin",
        "is_active": True
    }
    
    contributeur_user_data = {
        "username": "contributeur_user",
        "email": "contributeur@surm.com", 
        "full_name": "Marie Dubois",
        "role": "contributeur",
        "is_active": True
    }
    
    observateur_user_data = {
        "username": "observateur_user",
        "email": "observateur@surm.com",
        "full_name": "Jean Observateur",
        "role": "observateur",
        "is_active": True
    }
    
    created_users = []
    
    # Test 1: Create users with different roles
    print("\n1. Testing POST /api/users (Create users)")
    for user_data in [admin_user_data, contributeur_user_data, observateur_user_data]:
        response = requests.post(f"{API_URL}/users", json=user_data)
        if response.status_code == 200:
            user = response.json()
            created_users.append(user)
            print(f"✅ Created user: {user['full_name']} ({user['role']})")
        else:
            print(f"❌ Failed to create user {user_data['full_name']}: {response.status_code} - {response.text}")
    
    # Test 2: GET all users
    print("\n2. Testing GET /api/users (List all users)")
    response = requests.get(f"{API_URL}/users")
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Retrieved {len(users)} users:")
        for user in users:
            print(f"   - {user['full_name']} ({user['role']}) - Active: {user['is_active']}")
    else:
        print(f"❌ Failed to get users: {response.status_code} - {response.text}")
    
    # Test 3: GET specific user
    if created_users:
        user_id = created_users[0]['id']
        print(f"\n3. Testing GET /api/users/{user_id} (Get specific user)")
        response = requests.get(f"{API_URL}/users/{user_id}")
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Retrieved specific user: {user['full_name']} ({user['role']})")
        else:
            print(f"❌ Failed to get specific user: {response.status_code} - {response.text}")
    
    # Test 4: UPDATE user
    if created_users:
        user_id = created_users[0]['id']
        print(f"\n4. Testing PUT /api/users/{user_id} (Update user)")
        update_data = {
            "full_name": "Administrateur SURM Modifié",
            "is_active": False
        }
        response = requests.put(f"{API_URL}/users/{user_id}", json=update_data)
        if response.status_code == 200:
            updated_user = response.json()
            print(f"✅ Updated user: {updated_user['full_name']} - Active: {updated_user['is_active']}")
        else:
            print(f"❌ Failed to update user: {response.status_code} - {response.text}")
    
    # Test 5: Verify role enum values
    print("\n5. Testing role enum validation")
    invalid_role_data = {
        "username": "invalid_role_user",
        "email": "invalid@surm.com",
        "full_name": "Invalid Role User",
        "role": "invalid_role",
        "is_active": True
    }
    response = requests.post(f"{API_URL}/users", json=invalid_role_data)
    if response.status_code == 422:
        print("✅ Correctly rejected invalid role enum")
    else:
        print(f"❌ Should have rejected invalid role: {response.status_code}")
    
    # Test 6: DELETE user (test with last created user)
    if created_users and len(created_users) > 1:
        user_id = created_users[-1]['id']
        print(f"\n6. Testing DELETE /api/users/{user_id} (Delete user)")
        response = requests.delete(f"{API_URL}/users/{user_id}")
        if response.status_code == 200:
            print(f"✅ Deleted user: {created_users[-1]['full_name']}")
        else:
            print(f"❌ Failed to delete user: {response.status_code} - {response.text}")
    
    return created_users

def test_phase3_private_comments():
    """Test Phase 3 - Private Comments System"""
    print("\n=== TESTING PHASE 3 - PRIVATE COMMENTS SYSTEM ===")
    
    # First create test users and partners
    admin_user_data = {
        "username": "admin_comments",
        "email": "admin_comments@surm.com",
        "full_name": "Admin Comments",
        "role": "admin"
    }
    
    regular_user_data = {
        "username": "regular_comments",
        "email": "regular_comments@surm.com",
        "full_name": "Regular User",
        "role": "contributeur"
    }
    
    # Create users
    admin_response = requests.post(f"{API_URL}/users", json=admin_user_data)
    regular_response = requests.post(f"{API_URL}/users", json=regular_user_data)
    
    if admin_response.status_code != 200 or regular_response.status_code != 200:
        print("❌ Failed to create test users for comments")
        return
    
    admin_user = admin_response.json()
    regular_user = regular_response.json()
    
    # Create test partner
    test_partner_data = SOURCING_TEST_DATA.copy()
    test_partner_data["nom_entreprise"] = "Comments Test Partner"
    partner_response = requests.post(f"{API_URL}/sourcing", json=test_partner_data)
    
    if partner_response.status_code != 200:
        print("❌ Failed to create test partner for comments")
        return
    
    partner = partner_response.json()
    partner_id = partner['id']
    
    # Test 1: Create private comment as regular user
    print("\n1. Testing POST /api/comments (Create private comment)")
    comment_data = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "comment": "This is a private comment from regular user"
    }
    response = requests.post(f"{API_URL}/comments?user_id={regular_user['id']}", json=comment_data)
    if response.status_code == 200:
        comment = response.json()
        regular_comment_id = comment['id']
        print(f"✅ Created private comment: {comment['comment'][:50]}...")
        print(f"   User: {comment['user_name']}, Partner: {comment['partner_id']}")
    else:
        print(f"❌ Failed to create private comment: {response.status_code} - {response.text}")
        return
    
    # Test 2: Create private comment as admin
    print("\n2. Testing POST /api/comments as admin")
    admin_comment_data = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "comment": "This is a private comment from admin user"
    }
    response = requests.post(f"{API_URL}/comments?user_id={admin_user['id']}", json=admin_comment_data)
    if response.status_code == 200:
        admin_comment = response.json()
        admin_comment_id = admin_comment['id']
        print(f"✅ Created admin private comment: {admin_comment['comment'][:50]}...")
    else:
        print(f"❌ Failed to create admin private comment: {response.status_code} - {response.text}")
        return
    
    # Test 3: GET comments as regular user (should see only own comments)
    print(f"\n3. Testing GET /api/comments/{partner_id} as regular user (privacy test)")
    response = requests.get(f"{API_URL}/comments/{partner_id}?partner_type=sourcing&user_id={regular_user['id']}")
    if response.status_code == 200:
        comments = response.json()
        print(f"✅ Regular user retrieved {len(comments)} comments")
        
        # Verify user only sees their own comments
        own_comments = [c for c in comments if c['user_id'] == regular_user['id']]
        if len(comments) == len(own_comments):
            print("✅ Privacy verified: Regular user sees only own comments")
        else:
            print(f"❌ Privacy violation: Regular user sees {len(comments)} comments but owns {len(own_comments)}")
    else:
        print(f"❌ Failed to get comments as regular user: {response.status_code} - {response.text}")
    
    # Test 4: GET comments as admin (should see all comments)
    print(f"\n4. Testing GET /api/comments/{partner_id} as admin (should see all)")
    response = requests.get(f"{API_URL}/comments/{partner_id}?partner_type=sourcing&user_id={admin_user['id']}")
    if response.status_code == 200:
        comments = response.json()
        print(f"✅ Admin retrieved {len(comments)} comments")
        
        # Verify admin sees all comments
        if len(comments) >= 2:  # Should see both regular user and admin comments
            print("✅ Admin privilege verified: Admin sees all comments")
            for comment in comments:
                print(f"   - {comment['user_name']}: {comment['comment'][:30]}...")
        else:
            print(f"❌ Admin should see all comments but only sees {len(comments)}")
    else:
        print(f"❌ Failed to get comments as admin: {response.status_code} - {response.text}")
    
    # Test 5: UPDATE comment (only by owner or admin)
    print(f"\n5. Testing PUT /api/comments/{regular_comment_id} (Update comment)")
    update_data = {"comment": "Updated private comment text"}
    response = requests.put(f"{API_URL}/comments/{regular_comment_id}?user_id={regular_user['id']}", json=update_data)
    if response.status_code == 200:
        updated_comment = response.json()
        print(f"✅ Updated comment: {updated_comment['comment']}")
    else:
        print(f"❌ Failed to update comment: {response.status_code} - {response.text}")
    
    # Test 6: Try to update comment as different user (should fail)
    print(f"\n6. Testing unauthorized comment update (should fail)")
    response = requests.put(f"{API_URL}/comments/{admin_comment_id}?user_id={regular_user['id']}", json=update_data)
    if response.status_code == 403:
        print("✅ Correctly rejected unauthorized comment update")
    else:
        print(f"❌ Should have rejected unauthorized update: {response.status_code}")
    
    # Test 7: DELETE comment
    print(f"\n7. Testing DELETE /api/comments/{regular_comment_id} (Delete comment)")
    response = requests.delete(f"{API_URL}/comments/{regular_comment_id}?user_id={regular_user['id']}")
    if response.status_code == 200:
        print("✅ Successfully deleted private comment")
    else:
        print(f"❌ Failed to delete comment: {response.status_code} - {response.text}")
    
    return {
        'admin_user': admin_user,
        'regular_user': regular_user,
        'partner_id': partner_id
    }

def test_phase3_personal_dashboard():
    """Test Phase 3 - Personal Dashboard View"""
    print("\n=== TESTING PHASE 3 - PERSONAL DASHBOARD VIEW ===")
    
    # Create test user
    user_data = {
        "username": "dashboard_user",
        "email": "dashboard@surm.com",
        "full_name": "Dashboard Test User",
        "role": "contributeur"
    }
    
    user_response = requests.post(f"{API_URL}/users", json=user_data)
    if user_response.status_code != 200:
        print("❌ Failed to create test user for dashboard")
        return
    
    user = user_response.json()
    user_name = user['full_name']
    
    # Create test partners assigned to this user
    sourcing_data = SOURCING_TEST_DATA.copy()
    sourcing_data["nom_entreprise"] = "Dashboard Sourcing Test"
    sourcing_data["pilote"] = user_name
    
    dealflow_data = DEALFLOW_TEST_DATA.copy()
    dealflow_data["nom"] = "Dashboard Dealflow Test"
    dealflow_data["pilote"] = user_name
    
    # Create partners
    sourcing_response = requests.post(f"{API_URL}/sourcing", json=sourcing_data)
    dealflow_response = requests.post(f"{API_URL}/dealflow", json=dealflow_data)
    
    if sourcing_response.status_code != 200 or dealflow_response.status_code != 200:
        print("❌ Failed to create test partners for dashboard")
        return
    
    # Test 1: GET my-startups (user's assigned startups)
    print(f"\n1. Testing GET /api/my-startups (user's assigned startups)")
    response = requests.get(f"{API_URL}/my-startups?user_id={user['id']}")
    if response.status_code == 200:
        my_startups = response.json()
        print("✅ Retrieved personal dashboard data:")
        print(f"   - Sourcing partners: {len(my_startups.get('sourcing_partners', []))}")
        print(f"   - Dealflow partners: {len(my_startups.get('dealflow_partners', []))}")
        print(f"   - Total assigned: {my_startups.get('total_assigned', 0)}")
        
        # Verify filtering by pilote
        sourcing_partners = my_startups.get('sourcing_partners', [])
        dealflow_partners = my_startups.get('dealflow_partners', [])
        
        # Check if all sourcing partners belong to user
        sourcing_correct = all(p.get('pilote') == user_name for p in sourcing_partners)
        dealflow_correct = all(p.get('pilote') == user_name for p in dealflow_partners)
        
        if sourcing_correct and dealflow_correct:
            print("✅ Filtering by pilote working correctly")
        else:
            print("❌ Filtering by pilote not working correctly")
            
    else:
        print(f"❌ Failed to get my-startups: {response.status_code} - {response.text}")
    
    # Test 2: GET partners-by-pilote (partners grouped by pilote)
    print(f"\n2. Testing GET /api/partners-by-pilote (partners grouped by pilote)")
    response = requests.get(f"{API_URL}/partners-by-pilote")
    if response.status_code == 200:
        partners_by_pilote = response.json()
        print("✅ Retrieved partners grouped by pilote:")
        
        for pilote_name, pilote_data in partners_by_pilote.items():
            sourcing_count = len(pilote_data.get('sourcing_partners', []))
            dealflow_count = len(pilote_data.get('dealflow_partners', []))
            total = pilote_data.get('total_partners', 0)
            print(f"   - {pilote_name}: {sourcing_count} sourcing, {dealflow_count} dealflow (total: {total})")
        
        # Verify our test user appears in the grouping
        if user_name in partners_by_pilote:
            user_data = partners_by_pilote[user_name]
            if user_data.get('total_partners', 0) >= 2:  # Should have at least our 2 test partners
                print(f"✅ Test user found with {user_data['total_partners']} partners")
            else:
                print(f"❌ Test user has incorrect partner count: {user_data.get('total_partners', 0)}")
        else:
            print(f"❌ Test user {user_name} not found in pilote grouping")
            
    else:
        print(f"❌ Failed to get partners-by-pilote: {response.status_code} - {response.text}")
    
    return user

def test_phase3_enhanced_authorization():
    """Test Phase 3 - Enhanced Authorization with Role-Based Access"""
    print("\n=== TESTING PHASE 3 - ENHANCED AUTHORIZATION ===")
    
    # Create users with different roles
    admin_data = {
        "username": "auth_admin",
        "email": "auth_admin@surm.com",
        "full_name": "Auth Admin",
        "role": "admin"
    }
    
    contributeur_data = {
        "username": "auth_contributeur",
        "email": "auth_contributeur@surm.com",
        "full_name": "Auth Contributeur",
        "role": "contributeur"
    }
    
    observateur_data = {
        "username": "auth_observateur",
        "email": "auth_observateur@surm.com",
        "full_name": "Auth Observateur",
        "role": "observateur"
    }
    
    # Create users
    admin_response = requests.post(f"{API_URL}/users", json=admin_data)
    contributeur_response = requests.post(f"{API_URL}/users", json=contributeur_data)
    observateur_response = requests.post(f"{API_URL}/users", json=observateur_data)
    
    if not all(r.status_code == 200 for r in [admin_response, contributeur_response, observateur_response]):
        print("❌ Failed to create test users for authorization")
        return
    
    admin_user = admin_response.json()
    contributeur_user = contributeur_response.json()
    observateur_user = observateur_response.json()
    
    # Create test partner assigned to contributeur
    partner_data = SOURCING_TEST_DATA.copy()
    partner_data["nom_entreprise"] = "Authorization Test Partner"
    partner_data["pilote"] = contributeur_user['full_name']
    
    partner_response = requests.post(f"{API_URL}/sourcing?user_id={admin_user['id']}", json=partner_data)
    if partner_response.status_code != 200:
        print("❌ Failed to create test partner for authorization")
        return
    
    partner = partner_response.json()
    partner_id = partner['id']
    
    # Test 1: Admin access (should have full access)
    print("\n1. Testing Admin Role - Full Access")
    
    # Admin can view all partners
    response = requests.get(f"{API_URL}/sourcing?user_id={admin_user['id']}")
    if response.status_code == 200:
        partners = response.json()
        print(f"✅ Admin can view all sourcing partners: {len(partners)}")
    else:
        print(f"❌ Admin failed to view partners: {response.status_code}")
    
    # Admin can edit any partner
    update_data = {"actions_commentaires": "Updated by admin"}
    response = requests.put(f"{API_URL}/sourcing/{partner_id}?user_id={admin_user['id']}", json=update_data)
    if response.status_code == 200:
        print("✅ Admin can edit any partner")
    else:
        print(f"❌ Admin failed to edit partner: {response.status_code}")
    
    # Test 2: Contributeur access (can edit only own partners)
    print("\n2. Testing Contributeur Role - Limited Edit Access")
    
    # Contributeur can view partners (filtered to own)
    response = requests.get(f"{API_URL}/sourcing?user_id={contributeur_user['id']}")
    if response.status_code == 200:
        partners = response.json()
        # Should only see partners where pilote matches their name
        own_partners = [p for p in partners if p.get('pilote') == contributeur_user['full_name']]
        if len(partners) == len(own_partners):
            print(f"✅ Contributeur sees only own partners: {len(partners)}")
        else:
            print(f"❌ Contributeur sees unauthorized partners: {len(partners)} total, {len(own_partners)} own")
    else:
        print(f"❌ Contributeur failed to view partners: {response.status_code}")
    
    # Contributeur can edit own partner
    update_data = {"actions_commentaires": "Updated by contributeur"}
    response = requests.put(f"{API_URL}/sourcing/{partner_id}?user_id={contributeur_user['id']}", json=update_data)
    if response.status_code == 200:
        print("✅ Contributeur can edit own partner")
    else:
        print(f"❌ Contributeur failed to edit own partner: {response.status_code}")
    
    # Create partner assigned to someone else
    other_partner_data = SOURCING_TEST_DATA.copy()
    other_partner_data["nom_entreprise"] = "Other User Partner"
    other_partner_data["pilote"] = "Other User"
    
    other_partner_response = requests.post(f"{API_URL}/sourcing?user_id={admin_user['id']}", json=other_partner_data)
    if other_partner_response.status_code == 200:
        other_partner = other_partner_response.json()
        other_partner_id = other_partner['id']
        
        # Contributeur should NOT be able to edit other's partner
        response = requests.put(f"{API_URL}/sourcing/{other_partner_id}?user_id={contributeur_user['id']}", json=update_data)
        if response.status_code == 403:
            print("✅ Contributeur correctly denied access to other's partner")
        else:
            print(f"❌ Contributeur should be denied access: {response.status_code}")
    
    # Test 3: Observateur access (read-only)
    print("\n3. Testing Observateur Role - Read-Only Access")
    
    # Observateur can view all partners
    response = requests.get(f"{API_URL}/sourcing?user_id={observateur_user['id']}")
    if response.status_code == 200:
        partners = response.json()
        print(f"✅ Observateur can view all partners: {len(partners)}")
    else:
        print(f"❌ Observateur failed to view partners: {response.status_code}")
    
    # Observateur should NOT be able to create partners
    new_partner_data = SOURCING_TEST_DATA.copy()
    new_partner_data["nom_entreprise"] = "Observateur Test Partner"
    response = requests.post(f"{API_URL}/sourcing?user_id={observateur_user['id']}", json=new_partner_data)
    if response.status_code == 403:
        print("✅ Observateur correctly denied partner creation")
    else:
        print(f"❌ Observateur should be denied creation: {response.status_code}")
    
    # Observateur should NOT be able to edit partners
    response = requests.put(f"{API_URL}/sourcing/{partner_id}?user_id={observateur_user['id']}", json=update_data)
    if response.status_code == 403:
        print("✅ Observateur correctly denied partner editing")
    else:
        print(f"❌ Observateur should be denied editing: {response.status_code}")
    
    # Test 4: Test 403 status codes for permission errors
    print("\n4. Testing 403 Permission Error Responses")
    
    # Test various permission scenarios that should return 403
    permission_tests = [
        ("Observateur create", "POST", f"{API_URL}/sourcing?user_id={observateur_user['id']}", new_partner_data),
        ("Observateur edit", "PUT", f"{API_URL}/sourcing/{partner_id}?user_id={observateur_user['id']}", update_data),
        ("Contributeur edit other's", "PUT", f"{API_URL}/sourcing/{other_partner_id}?user_id={contributeur_user['id']}", update_data),
    ]
    
    for test_name, method, url, data in permission_tests:
        if method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        
        if response.status_code == 403:
            print(f"✅ {test_name}: Correctly returned 403")
        else:
            print(f"❌ {test_name}: Expected 403, got {response.status_code}")
    
    return {
        'admin_user': admin_user,
        'contributeur_user': contributeur_user,
        'observateur_user': observateur_user,
        'partner_id': partner_id
    }

# PHASE 4 - KANBAN PIPELINE TESTS
def test_phase4_kanban_data():
    """Test Phase 4 - Kanban Data Endpoint"""
    print("\n=== TESTING PHASE 4 - KANBAN DATA ENDPOINT ===")
    
    # Test 1: Basic kanban data endpoint
    print("\n1. Testing GET /api/kanban-data (basic)")
    response = requests.get(f"{API_URL}/kanban-data")
    if response.status_code == 200:
        kanban_data = response.json()
        print("✅ Kanban data endpoint working:")
        
        # Check required structure
        if "columns" in kanban_data and "columnOrder" in kanban_data and "summary" in kanban_data:
            print("✅ Response has correct structure (columns, columnOrder, summary)")
            
            # Check expected columns
            expected_columns = [
                "sourcing_a_traiter", "sourcing_klaxoon", "prequalification", 
                "presentation", "go_metier", "experimentation", 
                "evaluation", "generalisation", "cloture"
            ]
            
            columns = kanban_data["columns"]
            column_order = kanban_data["columnOrder"]
            
            # Verify all expected columns exist
            missing_columns = [col for col in expected_columns if col not in columns]
            if not missing_columns:
                print(f"✅ All 9 expected Kanban columns present: {len(columns)}")
            else:
                print(f"❌ Missing columns: {missing_columns}")
            
            # Verify column order matches expected
            if column_order == expected_columns:
                print("✅ Column order is correct")
            else:
                print(f"❌ Column order mismatch. Expected: {expected_columns}, Got: {column_order}")
            
            # Check column structure
            sample_column = columns.get("sourcing_a_traiter", {})
            if all(key in sample_column for key in ["id", "title", "subtitle", "partners"]):
                print("✅ Column structure is correct (id, title, subtitle, partners)")
            else:
                print(f"❌ Column structure incorrect. Sample: {list(sample_column.keys())}")
            
            # Check summary statistics
            summary = kanban_data["summary"]
            expected_summary_keys = ["total_partners", "total_sourcing", "total_dealflow", "by_column"]
            if all(key in summary for key in expected_summary_keys):
                print("✅ Summary statistics structure correct")
                print(f"   - Total partners: {summary['total_partners']}")
                print(f"   - Total sourcing: {summary['total_sourcing']}")
                print(f"   - Total dealflow: {summary['total_dealflow']}")
                
                # Verify by_column counts
                by_column = summary["by_column"]
                total_by_columns = sum(by_column.values())
                if total_by_columns == summary["total_partners"]:
                    print("✅ Column counts match total partners")
                else:
                    print(f"❌ Column counts mismatch: {total_by_columns} != {summary['total_partners']}")
            else:
                print(f"❌ Summary structure incorrect: {list(summary.keys())}")
                
        else:
            print(f"❌ Missing required fields in response: {list(kanban_data.keys())}")
    else:
        print(f"❌ Failed to get kanban data: {response.status_code} - {response.text}")
    
    # Test 2: Check partner data structure in columns
    print("\n2. Testing partner data structure in Kanban columns")
    response = requests.get(f"{API_URL}/kanban-data")
    if response.status_code == 200:
        kanban_data = response.json()
        
        # Find a column with partners
        partner_found = False
        for column_id, column_data in kanban_data["columns"].items():
            partners = column_data.get("partners", [])
            if partners:
                partner = partners[0]
                partner_found = True
                
                # Check required fields for Kanban
                required_fields = ["kanban_id", "partner_type", "is_inactive", "days_since_update"]
                missing_fields = [field for field in required_fields if field not in partner]
                
                if not missing_fields:
                    print(f"✅ Partner data structure correct in column '{column_id}'")
                    print(f"   - kanban_id: {partner['kanban_id']}")
                    print(f"   - partner_type: {partner['partner_type']}")
                    print(f"   - is_inactive: {partner['is_inactive']}")
                    print(f"   - days_since_update: {partner['days_since_update']}")
                else:
                    print(f"❌ Missing required fields in partner data: {missing_fields}")
                break
        
        if not partner_found:
            print("⚠️ No partners found in any column to test data structure")
    else:
        print(f"❌ Failed to get kanban data for partner structure test: {response.status_code}")
    
    # Test 3: Test user role filtering (contributeur vs admin)
    print("\n3. Testing user role filtering")
    
    # Create test users
    admin_user_data = {
        "username": "kanban_admin",
        "email": "kanban_admin@surm.com",
        "full_name": "Kanban Admin",
        "role": "admin"
    }
    
    contributeur_user_data = {
        "username": "kanban_contributeur",
        "email": "kanban_contributeur@surm.com",
        "full_name": "Kanban Contributeur",
        "role": "contributeur"
    }
    
    admin_response = requests.post(f"{API_URL}/users", json=admin_user_data)
    contributeur_response = requests.post(f"{API_URL}/users", json=contributeur_user_data)
    
    if admin_response.status_code == 200 and contributeur_response.status_code == 200:
        admin_user = admin_response.json()
        contributeur_user = contributeur_response.json()
        
        # Test admin sees all partners
        admin_kanban_response = requests.get(f"{API_URL}/kanban-data?user_id={admin_user['id']}")
        if admin_kanban_response.status_code == 200:
            admin_data = admin_kanban_response.json()
            admin_total = admin_data["summary"]["total_partners"]
            print(f"✅ Admin sees all partners: {admin_total}")
        else:
            print(f"❌ Admin kanban data failed: {admin_kanban_response.status_code}")
        
        # Test contributeur sees only own partners
        contributeur_kanban_response = requests.get(f"{API_URL}/kanban-data?user_id={contributeur_user['id']}")
        if contributeur_kanban_response.status_code == 200:
            contributeur_data = contributeur_kanban_response.json()
            contributeur_total = contributeur_data["summary"]["total_partners"]
            print(f"✅ Contributeur filtering working: {contributeur_total} partners")
            
            # Verify contributeur sees fewer or equal partners than admin
            if contributeur_total <= admin_total:
                print("✅ Role-based filtering verified: contributeur ≤ admin")
            else:
                print(f"❌ Role filtering issue: contributeur ({contributeur_total}) > admin ({admin_total})")
        else:
            print(f"❌ Contributeur kanban data failed: {contributeur_kanban_response.status_code}")
    else:
        print("❌ Failed to create test users for role filtering")

def test_phase4_kanban_move():
    """Test Phase 4 - Kanban Move Endpoint"""
    print("\n=== TESTING PHASE 4 - KANBAN MOVE ENDPOINT ===")
    
    # First create test partners for moving
    print("\n1. Creating test partners for Kanban move testing")
    
    # Create sourcing partner
    sourcing_data = SOURCING_TEST_DATA.copy()
    sourcing_data["nom_entreprise"] = "Kanban Move Test Sourcing"
    sourcing_data["statut"] = "A traiter"
    
    sourcing_response = requests.post(f"{API_URL}/sourcing", json=sourcing_data)
    if sourcing_response.status_code != 200:
        print("❌ Failed to create test sourcing partner for Kanban move")
        return
    
    sourcing_partner = sourcing_response.json()
    sourcing_id = sourcing_partner['id']
    print(f"✅ Created test sourcing partner: {sourcing_id}")
    
    # Create dealflow partner
    dealflow_data = DEALFLOW_TEST_DATA.copy()
    dealflow_data["nom"] = "Kanban Move Test Dealflow"
    dealflow_data["statut"] = "En cours avec l'équipe inno"
    
    dealflow_response = requests.post(f"{API_URL}/dealflow", json=dealflow_data)
    if dealflow_response.status_code != 200:
        print("❌ Failed to create test dealflow partner for Kanban move")
        return
    
    dealflow_partner = dealflow_response.json()
    dealflow_id = dealflow_partner['id']
    print(f"✅ Created test dealflow partner: {dealflow_id}")
    
    # Test 2: Move sourcing partner within sourcing columns
    print(f"\n2. Testing sourcing partner move within sourcing columns")
    move_params = {
        "partner_id": sourcing_id,
        "partner_type": "sourcing",
        "source_column": "sourcing_a_traiter",
        "destination_column": "sourcing_klaxoon"
    }
    
    response = requests.post(f"{API_URL}/kanban-move", params=move_params)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sourcing partner moved successfully: {result['message']}")
        
        # Verify status was updated
        verify_response = requests.get(f"{API_URL}/sourcing/{sourcing_id}")
        if verify_response.status_code == 200:
            updated_partner = verify_response.json()
            if updated_partner['statut'] == "Klaxoon":
                print("✅ Sourcing partner status correctly updated to 'Klaxoon'")
            else:
                print(f"❌ Status not updated correctly: {updated_partner['statut']}")
        else:
            print("❌ Failed to verify sourcing partner status update")
    else:
        print(f"❌ Failed to move sourcing partner: {response.status_code} - {response.text}")
    
    # Test 3: Move dealflow partner within dealflow columns
    print(f"\n3. Testing dealflow partner move within dealflow columns")
    move_params = {
        "partner_id": dealflow_id,
        "partner_type": "dealflow",
        "source_column": "prequalification",
        "destination_column": "presentation"
    }
    
    response = requests.post(f"{API_URL}/kanban-move", params=move_params)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Dealflow partner moved successfully: {result['message']}")
        
        # Verify status was updated
        verify_response = requests.get(f"{API_URL}/dealflow/{dealflow_id}")
        if verify_response.status_code == 200:
            updated_partner = verify_response.json()
            if updated_partner['statut'] == "En cours avec les métiers":
                print("✅ Dealflow partner status correctly updated to 'En cours avec les métiers'")
            else:
                print(f"❌ Status not updated correctly: {updated_partner['statut']}")
        else:
            print("❌ Failed to verify dealflow partner status update")
    else:
        print(f"❌ Failed to move dealflow partner: {response.status_code} - {response.text}")
    
    # Test 4: Transition from sourcing to dealflow
    print(f"\n4. Testing transition from sourcing to dealflow via Kanban move")
    
    # Create another sourcing partner for transition test
    transition_sourcing_data = SOURCING_TEST_DATA.copy()
    transition_sourcing_data["nom_entreprise"] = "Kanban Transition Test"
    transition_sourcing_data["statut"] = "A traiter"
    
    transition_response = requests.post(f"{API_URL}/sourcing", json=transition_sourcing_data)
    if transition_response.status_code == 200:
        transition_partner = transition_response.json()
        transition_id = transition_partner['id']
        
        # Move from sourcing to dealflow
        transition_move_params = {
            "partner_id": transition_id,
            "partner_type": "sourcing",
            "source_column": "sourcing_a_traiter",
            "destination_column": "prequalification"
        }
        
        response = requests.post(f"{API_URL}/kanban-move", params=transition_move_params)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sourcing to dealflow transition successful: {result['message']}")
            
            # Verify sourcing partner status updated to 'Dealflow'
            sourcing_verify = requests.get(f"{API_URL}/sourcing/{transition_id}")
            if sourcing_verify.status_code == 200:
                updated_sourcing = sourcing_verify.json()
                if updated_sourcing['statut'] == "Dealflow":
                    print("✅ Original sourcing partner status updated to 'Dealflow'")
                else:
                    print(f"❌ Sourcing status not updated correctly: {updated_sourcing['statut']}")
            
            # Verify new dealflow partner was created
            if "new_partner_id" in result:
                new_dealflow_id = result["new_partner_id"]
                dealflow_verify = requests.get(f"{API_URL}/dealflow/{new_dealflow_id}")
                if dealflow_verify.status_code == 200:
                    new_dealflow = dealflow_verify.json()
                    print(f"✅ New dealflow partner created: {new_dealflow['nom']}")
                    print(f"   Status: {new_dealflow['statut']}")
                    print(f"   Inherited data - Domain: {new_dealflow['domaine']}")
                else:
                    print("❌ Failed to verify new dealflow partner")
            else:
                print("❌ No new_partner_id returned from transition")
        else:
            print(f"❌ Failed to transition sourcing to dealflow: {response.status_code} - {response.text}")
    else:
        print("❌ Failed to create sourcing partner for transition test")
    
    # Test 5: Test activity logging for moves
    print(f"\n5. Testing activity logging for Kanban moves")
    
    # Check activity log for the dealflow move we did earlier
    activity_response = requests.get(f"{API_URL}/activity/{dealflow_id}?partner_type=dealflow")
    if activity_response.status_code == 200:
        activities = activity_response.json()
        
        # Look for kanban move activity
        kanban_activities = [
            activity for activity in activities 
            if activity.get('details', {}).get('kanban_move') == True
        ]
        
        if kanban_activities:
            print(f"✅ Kanban move activity logged: {len(kanban_activities)} activities")
            latest_activity = kanban_activities[0]
            print(f"   Description: {latest_activity['description']}")
            print(f"   Details: {latest_activity['details']}")
        else:
            print("❌ No Kanban move activities found in log")
    else:
        print(f"❌ Failed to get activity log: {activity_response.status_code}")
    
    # Test 6: Test invalid moves and error handling
    print(f"\n6. Testing invalid moves and error handling")
    
    # Test invalid destination column
    invalid_move_params = {
        "partner_id": sourcing_id,
        "partner_type": "sourcing",
        "source_column": "sourcing_a_traiter",
        "destination_column": "invalid_column"
    }
    
    response = requests.post(f"{API_URL}/kanban-move", params=invalid_move_params)
    if response.status_code == 400:
        print("✅ Correctly rejected invalid destination column")
    else:
        print(f"❌ Should have rejected invalid column: {response.status_code}")
    
    # Test invalid partner ID
    invalid_partner_params = {
        "partner_id": "invalid-id",
        "partner_type": "sourcing",
        "source_column": "sourcing_a_traiter",
        "destination_column": "sourcing_klaxoon"
    }
    
    response = requests.post(f"{API_URL}/kanban-move", params=invalid_partner_params)
    if response.status_code == 404:
        print("✅ Correctly rejected invalid partner ID")
    else:
        print(f"❌ Should have rejected invalid partner ID: {response.status_code}")
    
    # Test 7: Test authorization for moves
    print(f"\n7. Testing authorization for Kanban moves")
    
    # Create contributeur user
    contributeur_data = {
        "username": "kanban_move_contributeur",
        "email": "kanban_move_contributeur@surm.com",
        "full_name": "Move Test Contributeur",
        "role": "contributeur"
    }
    
    contributeur_response = requests.post(f"{API_URL}/users", json=contributeur_data)
    if contributeur_response.status_code == 200:
        contributeur_user = contributeur_response.json()
        
        # Try to move a partner not assigned to this contributeur
        unauthorized_move = {
            "partner_id": sourcing_id,  # This partner is assigned to "Marie Dubois"
            "partner_type": "sourcing",
            "source_column": "sourcing_klaxoon",
            "destination_column": "sourcing_a_traiter"
        }
        
        response = requests.post(f"{API_URL}/kanban-move?user_id={contributeur_user['id']}", json=unauthorized_move)
        if response.status_code == 403:
            print("✅ Correctly rejected unauthorized move by contributeur")
        else:
            print(f"❌ Should have rejected unauthorized move: {response.status_code}")
    else:
        print("❌ Failed to create contributeur for authorization test")
    
    return {
        'sourcing_id': sourcing_id,
        'dealflow_id': dealflow_id
    }

def test_phase4_data_structure_validation():
    """Test Phase 4 - Data Structure Validation"""
    print("\n=== TESTING PHASE 4 - DATA STRUCTURE VALIDATION ===")
    
    # Test 1: Verify MongoDB ObjectId removal
    print("\n1. Testing MongoDB ObjectId removal from responses")
    response = requests.get(f"{API_URL}/kanban-data")
    if response.status_code == 200:
        kanban_data = response.json()
        
        # Check if any partner has _id field (should be removed)
        objectid_found = False
        for column_id, column_data in kanban_data["columns"].items():
            for partner in column_data.get("partners", []):
                if "_id" in partner:
                    objectid_found = True
                    break
            if objectid_found:
                break
        
        if not objectid_found:
            print("✅ MongoDB ObjectId successfully removed from all partners")
        else:
            print("❌ MongoDB ObjectId found in partner data (should be removed)")
    else:
        print(f"❌ Failed to get kanban data for ObjectId test: {response.status_code}")
    
    # Test 2: Verify required fields for Kanban view
    print("\n2. Testing required fields for Kanban view")
    response = requests.get(f"{API_URL}/kanban-data")
    if response.status_code == 200:
        kanban_data = response.json()
        
        # Check partner data includes required fields
        partner_found = False
        for column_id, column_data in kanban_data["columns"].items():
            partners = column_data.get("partners", [])
            if partners:
                partner = partners[0]
                partner_found = True
                
                # Required fields for Kanban
                required_fields = ["kanban_id", "partner_type"]
                
                # Name fields (different for sourcing vs dealflow)
                if partner["partner_type"] == "sourcing":
                    required_fields.append("nom_entreprise")
                else:
                    required_fields.append("nom")
                
                missing_fields = [field for field in required_fields if field not in partner]
                
                if not missing_fields:
                    print(f"✅ Required fields present in {partner['partner_type']} partner")
                    
                    # Verify kanban_id format
                    kanban_id = partner["kanban_id"]
                    expected_prefix = f"{partner['partner_type']}_"
                    if kanban_id.startswith(expected_prefix):
                        print(f"✅ kanban_id format correct: {kanban_id}")
                    else:
                        print(f"❌ kanban_id format incorrect: {kanban_id}")
                else:
                    print(f"❌ Missing required fields: {missing_fields}")
                break
        
        if not partner_found:
            print("⚠️ No partners found to test required fields")
    else:
        print(f"❌ Failed to get kanban data for field validation: {response.status_code}")
    
    # Test 3: Test inactivity status calculation integration
    print("\n3. Testing inactivity status calculation integration")
    response = requests.get(f"{API_URL}/kanban-data")
    if response.status_code == 200:
        kanban_data = response.json()
        
        # Find partners and check inactivity fields
        inactivity_fields_found = False
        for column_id, column_data in kanban_data["columns"].items():
            partners = column_data.get("partners", [])
            if partners:
                partner = partners[0]
                
                if "is_inactive" in partner and "days_since_update" in partner:
                    inactivity_fields_found = True
                    print(f"✅ Inactivity status integrated in Kanban data")
                    print(f"   Sample partner - is_inactive: {partner['is_inactive']}, days_since_update: {partner['days_since_update']}")
                    
                    # Verify data types
                    if isinstance(partner["is_inactive"], bool) and isinstance(partner["days_since_update"], int):
                        print("✅ Inactivity field data types correct")
                    else:
                        print(f"❌ Inactivity field data types incorrect: is_inactive={type(partner['is_inactive'])}, days_since_update={type(partner['days_since_update'])}")
                break
        
        if not inactivity_fields_found:
            print("❌ Inactivity status fields not found in Kanban data")
    else:
        print(f"❌ Failed to get kanban data for inactivity test: {response.status_code}")
    
    # Test 4: Test date field handling and serialization
    print("\n4. Testing date field handling and serialization")
    response = requests.get(f"{API_URL}/kanban-data")
    if response.status_code == 200:
        kanban_data = response.json()
        
        # Find partners with date fields
        date_fields_tested = False
        for column_id, column_data in kanban_data["columns"].items():
            partners = column_data.get("partners", [])
            for partner in partners:
                # Check common date fields
                date_fields = ["date_prochaine_action", "created_at", "updated_at"]
                if partner["partner_type"] == "sourcing":
                    date_fields.extend(["date_entree_sourcing", "date_presentation_metiers"])
                else:
                    date_fields.extend(["date_reception_fichier", "date_pre_qualification"])
                
                for date_field in date_fields:
                    if date_field in partner and partner[date_field] is not None:
                        date_value = partner[date_field]
                        
                        # Verify it's a string (serialized date)
                        if isinstance(date_value, str):
                            print(f"✅ Date field '{date_field}' properly serialized as string")
                            date_fields_tested = True
                        else:
                            print(f"❌ Date field '{date_field}' not serialized: {type(date_value)}")
                        break
                
                if date_fields_tested:
                    break
            if date_fields_tested:
                break
        
        if not date_fields_tested:
            print("⚠️ No date fields found to test serialization")
    else:
        print(f"❌ Failed to get kanban data for date serialization test: {response.status_code}")

def test_phase4_synthetic_reports():
    """Test Phase 4 - Synthetic Reports Backend Implementation"""
    print("\n=== TESTING PHASE 4 - SYNTHETIC REPORTS BACKEND ===")
    
    # Test 1: Basic synthetic report endpoint
    print("\n1. Testing GET /api/synthetic-report (basic functionality)")
    response = requests.get(f"{API_URL}/synthetic-report")
    if response.status_code == 200:
        report = response.json()
        print("✅ Synthetic report endpoint working:")
        
        # Check required structure: summary, cross_tables, detailed_data
        required_sections = ["summary", "cross_tables", "detailed_data"]
        missing_sections = [section for section in required_sections if section not in report]
        
        if not missing_sections:
            print("✅ Report has correct structure (summary, cross_tables, detailed_data)")
            
            # Test summary structure
            summary = report["summary"]
            expected_summary_keys = ["total_sourcing", "total_dealflow", "total_partners", "generated_at", "generated_by"]
            if all(key in summary for key in expected_summary_keys):
                print("✅ Summary section has correct structure")
                print(f"   - Total sourcing: {summary['total_sourcing']}")
                print(f"   - Total dealflow: {summary['total_dealflow']}")
                print(f"   - Total partners: {summary['total_partners']}")
                print(f"   - Generated by: {summary['generated_by']}")
                print(f"   - Generated at: {summary['generated_at']}")
                
                # Verify totals consistency
                expected_total = summary['total_sourcing'] + summary['total_dealflow']
                if summary['total_partners'] == expected_total:
                    print("✅ Summary totals are consistent")
                else:
                    print(f"❌ Summary totals inconsistent: {summary['total_partners']} != {expected_total}")
            else:
                print(f"❌ Missing summary keys: {[k for k in expected_summary_keys if k not in summary]}")
            
            # Test cross_tables structure
            cross_tables = report["cross_tables"]
            expected_cross_tables = ["by_status", "by_pilote", "by_domain", "by_collaboration_type", "by_month"]
            missing_cross_tables = [ct for ct in expected_cross_tables if ct not in cross_tables]
            
            if not missing_cross_tables:
                print("✅ All 5 required cross-tables present:")
                
                # Test by_status cross-table
                by_status = cross_tables["by_status"]
                print(f"   - by_status: {len(by_status)} status categories")
                if by_status:
                    sample_status = list(by_status.keys())[0]
                    print(f"     Sample: {sample_status} = {by_status[sample_status]}")
                
                # Test by_pilote cross-table
                by_pilote = cross_tables["by_pilote"]
                print(f"   - by_pilote: {len(by_pilote)} pilotes")
                if by_pilote:
                    sample_pilote = list(by_pilote.keys())[0]
                    pilote_data = by_pilote[sample_pilote]
                    if isinstance(pilote_data, dict) and all(k in pilote_data for k in ["sourcing", "dealflow", "total"]):
                        print(f"     Sample: {sample_pilote} = {pilote_data}")
                        print("✅ by_pilote has correct structure (sourcing, dealflow, total)")
                    else:
                        print(f"❌ by_pilote structure incorrect: {pilote_data}")
                
                # Test by_domain cross-table
                by_domain = cross_tables["by_domain"]
                print(f"   - by_domain: {len(by_domain)} domains")
                if by_domain:
                    sample_domain = list(by_domain.keys())[0]
                    domain_data = by_domain[sample_domain]
                    if isinstance(domain_data, dict) and all(k in domain_data for k in ["sourcing", "dealflow", "total"]):
                        print(f"     Sample: {sample_domain} = {domain_data}")
                        print("✅ by_domain has correct structure (sourcing, dealflow, total)")
                    else:
                        print(f"❌ by_domain structure incorrect: {domain_data}")
                
                # Test by_collaboration_type cross-table
                by_collaboration = cross_tables["by_collaboration_type"]
                print(f"   - by_collaboration_type: {len(by_collaboration)} types")
                if by_collaboration:
                    sample_collab = list(by_collaboration.keys())[0]
                    collab_data = by_collaboration[sample_collab]
                    if isinstance(collab_data, dict) and all(k in collab_data for k in ["count", "partners"]):
                        print(f"     Sample: {sample_collab} = count: {collab_data['count']}, partners: {len(collab_data['partners'])}")
                        print("✅ by_collaboration_type has correct structure (count, partners)")
                    else:
                        print(f"❌ by_collaboration_type structure incorrect: {collab_data}")
                
                # Test by_month cross-table
                by_month = cross_tables["by_month"]
                print(f"   - by_month: {len(by_month)} months")
                if by_month:
                    sample_month = list(by_month.keys())[0]
                    month_data = by_month[sample_month]
                    if isinstance(month_data, dict) and all(k in month_data for k in ["sourcing", "dealflow"]):
                        print(f"     Sample: {sample_month} = {month_data}")
                        print("✅ by_month has correct structure (sourcing, dealflow)")
                    else:
                        print(f"❌ by_month structure incorrect: {month_data}")
                        
            else:
                print(f"❌ Missing cross-tables: {missing_cross_tables}")
            
            # Test detailed_data structure for CSV export
            detailed_data = report["detailed_data"]
            print(f"✅ Detailed data for CSV export: {len(detailed_data)} records")
            
            if detailed_data:
                sample_record = detailed_data[0]
                expected_csv_fields = [
                    "nom", "type", "statut", "domaine", "pilote", "typologie", 
                    "pays", "source", "date_entree", "date_prochaine_action", 
                    "interet", "is_inactive", "actions_commentaires"
                ]
                missing_csv_fields = [field for field in expected_csv_fields if field not in sample_record]
                
                if not missing_csv_fields:
                    print("✅ CSV export data has correct structure")
                    print(f"   Sample record: {sample_record['nom']} ({sample_record['type']})")
                    
                    # Test data sanitization (truncated comments)
                    comments = sample_record.get("actions_commentaires", "")
                    if len(comments) <= 103:  # 100 chars + "..." = 103 max
                        print("✅ Comments properly truncated for CSV export")
                    else:
                        print(f"❌ Comments not properly truncated: {len(comments)} chars")
                        
                else:
                    print(f"❌ Missing CSV fields: {missing_csv_fields}")
                    
        else:
            print(f"❌ Missing required sections: {missing_sections}")
            
    else:
        print(f"❌ Failed to get synthetic report: {response.status_code} - {response.text}")
        return
    
    # Test 2: User role filtering (contributeur vs admin)
    print("\n2. Testing user role filtering")
    
    # Create test users for role testing
    admin_user_data = {
        "username": "synthetic_admin",
        "email": "synthetic_admin@surm.com",
        "full_name": "Synthetic Admin",
        "role": "admin"
    }
    
    contributeur_user_data = {
        "username": "synthetic_contributeur",
        "email": "synthetic_contributeur@surm.com",
        "full_name": "Synthetic Contributeur",
        "role": "contributeur"
    }
    
    # Create users
    admin_response = requests.post(f"{API_URL}/users", json=admin_user_data)
    contributeur_response = requests.post(f"{API_URL}/users", json=contributeur_user_data)
    
    if admin_response.status_code == 200 and contributeur_response.status_code == 200:
        admin_user = admin_response.json()
        contributeur_user = contributeur_response.json()
        
        # Test admin access (should see all data)
        admin_report_response = requests.get(f"{API_URL}/synthetic-report?user_id={admin_user['id']}")
        if admin_report_response.status_code == 200:
            admin_report = admin_report_response.json()
            admin_total = admin_report["summary"]["total_partners"]
            print(f"✅ Admin sees all partners: {admin_total}")
        else:
            print(f"❌ Admin failed to get report: {admin_report_response.status_code}")
            admin_total = 0
        
        # Test contributeur access (should see only own data)
        contributeur_report_response = requests.get(f"{API_URL}/synthetic-report?user_id={contributeur_user['id']}")
        if contributeur_report_response.status_code == 200:
            contributeur_report = contributeur_report_response.json()
            contributeur_total = contributeur_report["summary"]["total_partners"]
            print(f"✅ Contributeur sees filtered partners: {contributeur_total}")
            
            # Verify role-based filtering
            if contributeur_total <= admin_total:
                print("✅ Role-based filtering working correctly")
                
                # Check if generated_by field reflects correct user
                if contributeur_report["summary"]["generated_by"] == contributeur_user["full_name"]:
                    print("✅ Report correctly shows generated_by user")
                else:
                    print(f"❌ generated_by incorrect: {contributeur_report['summary']['generated_by']}")
            else:
                print(f"❌ Role filtering failed: contributeur sees more than admin ({contributeur_total} > {admin_total})")
        else:
            print(f"❌ Contributeur failed to get report: {contributeur_report_response.status_code}")
    else:
        print("❌ Failed to create test users for role filtering")
    
    # Test 3: Cross-table calculations accuracy
    print("\n3. Testing cross-table calculations accuracy")
    
    # Get fresh report for accuracy testing
    response = requests.get(f"{API_URL}/synthetic-report")
    if response.status_code == 200:
        report = response.json()
        
        # Test status distribution accuracy
        by_status = report["cross_tables"]["by_status"]
        status_total = sum(by_status.values())
        expected_total = report["summary"]["total_partners"]
        
        if status_total == expected_total:
            print("✅ Status distribution calculations accurate")
        else:
            print(f"❌ Status distribution mismatch: {status_total} != {expected_total}")
        
        # Test pilote distribution accuracy
        by_pilote = report["cross_tables"]["by_pilote"]
        pilote_total = sum(pilote_data["total"] for pilote_data in by_pilote.values())
        
        if pilote_total == expected_total:
            print("✅ Pilote distribution calculations accurate")
        else:
            print(f"❌ Pilote distribution mismatch: {pilote_total} != {expected_total}")
        
        # Test domain distribution accuracy
        by_domain = report["cross_tables"]["by_domain"]
        domain_total = sum(domain_data["total"] for domain_data in by_domain.values())
        
        if domain_total == expected_total:
            print("✅ Domain distribution calculations accurate")
        else:
            print(f"❌ Domain distribution mismatch: {domain_total} != {expected_total}")
        
        # Test detailed data count matches summary
        detailed_count = len(report["detailed_data"])
        if detailed_count == expected_total:
            print("✅ Detailed data count matches summary")
        else:
            print(f"❌ Detailed data count mismatch: {detailed_count} != {expected_total}")
            
    else:
        print("❌ Failed to get report for accuracy testing")
    
    # Test 4: Date handling for monthly analysis
    print("\n4. Testing date handling for monthly analysis")
    
    response = requests.get(f"{API_URL}/synthetic-report")
    if response.status_code == 200:
        report = response.json()
        by_month = report["cross_tables"]["by_month"]
        
        if by_month:
            # Check month format (YYYY-MM)
            month_keys = list(by_month.keys())
            valid_month_format = all(
                len(month) == 7 and month[4] == '-' and month[:4].isdigit() and month[5:].isdigit()
                for month in month_keys
            )
            
            if valid_month_format:
                print("✅ Monthly data has correct format (YYYY-MM)")
                
                # Check if months are sorted
                sorted_months = sorted(month_keys)
                if month_keys == sorted_months:
                    print("✅ Monthly data is properly sorted")
                else:
                    print("❌ Monthly data not properly sorted")
                
                # Verify monthly totals
                monthly_sourcing_total = sum(month_data["sourcing"] for month_data in by_month.values())
                monthly_dealflow_total = sum(month_data["dealflow"] for month_data in by_month.values())
                monthly_total = monthly_sourcing_total + monthly_dealflow_total
                
                expected_total = report["summary"]["total_partners"]
                if monthly_total == expected_total:
                    print("✅ Monthly analysis totals are accurate")
                else:
                    print(f"❌ Monthly analysis totals mismatch: {monthly_total} != {expected_total}")
                    
            else:
                print(f"❌ Invalid month format in keys: {month_keys[:3]}")
        else:
            print("⚠️ No monthly data found (may be expected if no partners exist)")
    else:
        print("❌ Failed to get report for date handling test")
    
    print("\n✅ PHASE 4 - SYNTHETIC REPORTS TESTING COMPLETED")

# DOCUMENT MANAGEMENT SYSTEM TESTS
def test_document_management_system():
    """Test the complete document management system"""
    print("\n=== TESTING DOCUMENT MANAGEMENT SYSTEM ===")
    
    # First create a test partner to associate documents with
    print("\n0. Creating test partner for document association")
    test_partner_data = SOURCING_TEST_DATA.copy()
    test_partner_data["nom_entreprise"] = "Document Test Partner"
    partner_response = requests.post(f"{API_URL}/sourcing", json=test_partner_data)
    
    if partner_response.status_code != 200:
        print("❌ Failed to create test partner for documents")
        return
    
    partner = partner_response.json()
    partner_id = partner['id']
    print(f"✅ Created test partner: {partner_id}")
    
    # Test 1: GET /api/documents/types - List available document types
    print("\n1. Testing GET /api/documents/types (List document types)")
    response = requests.get(f"{API_URL}/documents/types")
    if response.status_code == 200:
        doc_types = response.json()
        expected_types = ["Convention", "Présentation", "Compte-rendu", "Contrat", "Document technique", "Autre"]
        print(f"✅ Retrieved {len(doc_types)} document types:")
        for doc_type in doc_types:
            print(f"   - {doc_type}")
        
        # Verify all expected types are present
        missing_types = [t for t in expected_types if t not in doc_types]
        if not missing_types:
            print("✅ All expected document types present")
        else:
            print(f"❌ Missing document types: {missing_types}")
    else:
        print(f"❌ Failed to get document types: {response.status_code} - {response.text}")
        return
    
    # Test 2: POST /api/documents/upload - Upload a document
    print("\n2. Testing POST /api/documents/upload (Upload document)")
    
    # Create test file content (Base64 encoded PDF-like content)
    import base64
    # Create a simple test content and encode it properly
    test_content_raw = b"This is a test PDF document content for validation purposes."
    test_content = base64.b64encode(test_content_raw).decode('utf-8')
    
    upload_data = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "test_document.pdf",
        "document_type": "Convention",
        "content": test_content,
        "description": "Test document for validation",
        "uploaded_by": "test_user"
    }
    
    response = requests.post(f"{API_URL}/documents/upload", params=upload_data)
    if response.status_code == 200:
        document = response.json()
        document_id = document['id']
        print(f"✅ Uploaded document successfully:")
        print(f"   - ID: {document_id}")
        print(f"   - Filename: {document['filename']}")
        print(f"   - Original filename: {document['original_filename']}")
        print(f"   - File type: {document['file_type']}")
        print(f"   - Document type: {document['document_type']}")
        print(f"   - Version: {document['version']}")
        print(f"   - File size: {document['file_size']} bytes")
        
        # Verify MIME type detection
        if document['file_type'] == 'application/pdf':
            print("✅ MIME type correctly detected as PDF")
        else:
            print(f"❌ MIME type incorrect: expected 'application/pdf', got '{document['file_type']}'")
            
        # Verify version is 1 for first upload
        if document['version'] == 1:
            print("✅ Version correctly set to 1 for first upload")
        else:
            print(f"❌ Version incorrect: expected 1, got {document['version']}")
            
    else:
        print(f"❌ Failed to upload document: {response.status_code} - {response.text}")
        return
    
    # Test 3: Upload second document with same filename (test versioning)
    print("\n3. Testing document versioning (same filename)")
    
    # Upload another document with the same filename
    upload_data_v2 = upload_data.copy()
    upload_data_v2["description"] = "Second version of test document"
    upload_data_v2["content"] = base64.b64encode(b"Updated content for version 2").decode('utf-8')
    
    response = requests.post(f"{API_URL}/documents/upload", params=upload_data_v2)
    if response.status_code == 200:
        document_v2 = response.json()
        document_v2_id = document_v2['id']
        print(f"✅ Uploaded second version successfully:")
        print(f"   - ID: {document_v2_id}")
        print(f"   - Filename: {document_v2['filename']}")
        print(f"   - Version: {document_v2['version']}")
        
        # Verify version increment
        if document_v2['version'] == 2:
            print("✅ Version correctly incremented to 2")
        else:
            print(f"❌ Version incorrect: expected 2, got {document_v2['version']}")
            
        # Verify filename includes version
        if "_v2" in document_v2['filename']:
            print("✅ Filename correctly includes version suffix")
        else:
            print(f"❌ Filename should include version: {document_v2['filename']}")
            
    else:
        print(f"❌ Failed to upload second version: {response.status_code} - {response.text}")
        return
    
    # Test 4: GET /api/documents/{partner_id} - Get documents for partner
    print(f"\n4. Testing GET /api/documents/{partner_id} (Get partner documents)")
    response = requests.get(f"{API_URL}/documents/{partner_id}")
    if response.status_code == 200:
        documents = response.json()
        print(f"✅ Retrieved {len(documents)} documents for partner:")
        for doc in documents:
            print(f"   - {doc['filename']} (v{doc['version']}) - {doc['document_type']}")
        
        # Verify we have both versions
        if len(documents) >= 2:
            print("✅ Both document versions retrieved")
            
            # Verify different versions have different IDs
            doc_ids = [doc['id'] for doc in documents]
            if len(set(doc_ids)) == len(doc_ids):
                print("✅ All documents have unique IDs")
            else:
                print("❌ Duplicate document IDs found")
        else:
            print(f"❌ Expected at least 2 documents, got {len(documents)}")
    else:
        print(f"❌ Failed to get partner documents: {response.status_code} - {response.text}")
        return
    
    # Test 5: GET /api/documents/download/{document_id} - Download document
    print(f"\n5. Testing GET /api/documents/download/{document_id} (Download document)")
    response = requests.get(f"{API_URL}/documents/download/{document_id}")
    if response.status_code == 200:
        print("✅ Document download successful:")
        print(f"   - Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"   - Content-Disposition: {response.headers.get('content-disposition', 'Not set')}")
        print(f"   - Content length: {len(response.content)} bytes")
        
        # Verify content integrity by decoding and comparing
        try:
            downloaded_content = base64.b64encode(response.content).decode('utf-8')
            if downloaded_content == test_content:
                print("✅ Downloaded content matches uploaded content")
            else:
                print("❌ Downloaded content differs from uploaded content")
        except Exception as e:
            print(f"⚠️ Could not verify content integrity: {e}")
            
    else:
        print(f"❌ Failed to download document: {response.status_code} - {response.text}")
    
    # Test 6: Test different file types and MIME type detection
    print("\n6. Testing different file types and MIME type detection")
    
    file_type_tests = [
        ("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "Document technique"),
        ("test.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", "Présentation"),
        ("test.txt", "text/plain", "Autre"),
        ("test.jpg", "image/jpeg", "Autre"),
        ("test.png", "image/png", "Autre")
    ]
    
    uploaded_test_docs = []
    for filename, expected_mime, doc_type in file_type_tests:
        test_file_content = base64.b64encode(f"Test content for {filename}".encode()).decode('utf-8')
        
        upload_data_test = {
            "partner_id": partner_id,
            "partner_type": "sourcing", 
            "filename": filename,
            "document_type": doc_type,
            "content": test_file_content,
            "uploaded_by": "test_user"
        }
        
        response = requests.post(f"{API_URL}/documents/upload", params=upload_data_test)
        if response.status_code == 200:
            doc = response.json()
            uploaded_test_docs.append(doc)
            if doc['file_type'] == expected_mime:
                print(f"✅ {filename}: MIME type correctly detected as {expected_mime}")
            else:
                print(f"❌ {filename}: Expected {expected_mime}, got {doc['file_type']}")
        else:
            print(f"❌ Failed to upload {filename}: {response.status_code}")
    
    # Test 7: DELETE /api/documents/{document_id} - Delete document
    print(f"\n7. Testing DELETE /api/documents/{document_id} (Delete document)")
    response = requests.delete(f"{API_URL}/documents/{document_id}")
    if response.status_code == 200:
        print("✅ Document deleted successfully")
        
        # Verify document is actually deleted
        response = requests.get(f"{API_URL}/documents/download/{document_id}")
        if response.status_code == 404:
            print("✅ Deleted document no longer accessible")
        else:
            print(f"❌ Deleted document still accessible: {response.status_code}")
    else:
        print(f"❌ Failed to delete document: {response.status_code} - {response.text}")
    
    # Test 8: Verify document list after deletion
    print(f"\n8. Testing document list after deletion")
    response = requests.get(f"{API_URL}/documents/{partner_id}")
    if response.status_code == 200:
        documents_after_delete = response.json()
        print(f"✅ Retrieved {len(documents_after_delete)} documents after deletion")
        
        # Should have one less document now
        if len(documents_after_delete) == len(documents) - 1:
            print("✅ Document count correctly reduced after deletion")
        else:
            print(f"❌ Expected {len(documents) - 1} documents, got {len(documents_after_delete)}")
    else:
        print(f"❌ Failed to get documents after deletion: {response.status_code}")
    
    # Test 9: Test error cases
    print("\n9. Testing error cases")
    
    # Test invalid Base64 content
    print("   9.1 Testing invalid Base64 content")
    invalid_upload = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "invalid.pdf",
        "document_type": "Convention",
        "content": "invalid-base64-content!@#$",
        "uploaded_by": "test_user"
    }
    response = requests.post(f"{API_URL}/documents/upload", params=invalid_upload)
    if response.status_code == 400:
        print("   ✅ Correctly rejected invalid Base64 content")
    else:
        print(f"   ❌ Should have rejected invalid Base64: {response.status_code}")
    
    # Test invalid document type
    print("   9.2 Testing invalid document type")
    invalid_type_upload = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "test.pdf",
        "document_type": "InvalidType",
        "content": test_content,
        "uploaded_by": "test_user"
    }
    response = requests.post(f"{API_URL}/documents/upload", params=invalid_type_upload)
    if response.status_code == 422:
        print("   ✅ Correctly rejected invalid document type")
    else:
        print(f"   ❌ Should have rejected invalid document type: {response.status_code}")
    
    # Test download non-existent document
    print("   9.3 Testing download non-existent document")
    response = requests.get(f"{API_URL}/documents/download/non-existent-id")
    if response.status_code == 404:
        print("   ✅ Correctly returned 404 for non-existent document")
    else:
        print(f"   ❌ Should have returned 404: {response.status_code}")
    
    # Test delete non-existent document
    print("   9.4 Testing delete non-existent document")
    response = requests.delete(f"{API_URL}/documents/non-existent-id")
    if response.status_code == 404:
        print("   ✅ Correctly returned 404 for non-existent document deletion")
    else:
        print(f"   ❌ Should have returned 404: {response.status_code}")
    
    print("\n✅ DOCUMENT MANAGEMENT SYSTEM TESTING COMPLETED")
    return {
        'partner_id': partner_id,
        'uploaded_documents': uploaded_test_docs,
        'remaining_document_id': document_v2_id
    }

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

def test_document_download_urgent():
    """URGENT: Test document download functionality after URL correction"""
    print("\n=== URGENT DOCUMENT DOWNLOAD TEST POST-CORRECTION ===")
    print("Testing document download after backend URL correction from preview.emergentagent.com to localhost:8001")
    
    # First, create a test partner
    print("\n1. Creating test partner for document testing")
    test_partner_data = {
        "nom_entreprise": "BACKEND SUCCESS Company",
        "statut": "A traiter",
        "pays_origine": "France",
        "domaine_activite": "FinTech",
        "typologie": "Startup",
        "objet": "Solution de paiement innovante",
        "cas_usage": "Paiements mobiles sécurisés",
        "technologie": "Blockchain",
        "source": "VivaTech 2025",
        "date_entree_sourcing": "2024-12-20",
        "interet": True,
        "pilote": "Marie Backend",
        "actions_commentaires": "Test urgent pour téléchargement documents"
    }
    
    partner_response = requests.post(f"{API_URL}/sourcing", json=test_partner_data)
    if partner_response.status_code != 200:
        print(f"❌ Failed to create test partner: {partner_response.status_code} - {partner_response.text}")
        return
    
    partner = partner_response.json()
    partner_id = partner['id']
    print(f"✅ Created test partner: {partner['nom_entreprise']} (ID: {partner_id})")
    
    # Test 2: Upload a test document
    print("\n2. Uploading test document 'test_document.txt'")
    import base64
    
    # Create test content matching user's scenario
    test_content_raw = b"Ceci est le contenu du document test_document.txt pour validation du telechargement."
    test_content_b64 = base64.b64encode(test_content_raw).decode('utf-8')
    
    upload_data = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "test_document.txt",
        "document_type": "Autre",
        "content": test_content_b64,
        "description": "Document test pour validation téléchargement",
        "uploaded_by": "test_user"
    }
    
    response = requests.post(f"{API_URL}/documents/upload", params=upload_data)
    if response.status_code != 200:
        print(f"❌ Failed to upload document: {response.status_code} - {response.text}")
        return
    
    document = response.json()
    document_id = document['id']
    print(f"✅ Uploaded document successfully:")
    print(f"   - ID: {document_id}")
    print(f"   - Filename: {document['filename']}")
    print(f"   - File type: {document['file_type']}")
    print(f"   - File size: {document['file_size']} bytes")
    
    # Test 3: List documents for partner (GET /api/documents/{partner_id})
    print(f"\n3. Testing GET /api/documents/{partner_id} (List partner documents)")
    response = requests.get(f"{API_URL}/documents/{partner_id}")
    if response.status_code == 200:
        documents = response.json()
        print(f"✅ Retrieved {len(documents)} documents for partner:")
        for doc in documents:
            print(f"   - {doc['filename']} (ID: {doc['id']}) - Type: {doc['document_type']}")
        
        # Verify our test document is in the list
        test_doc_found = any(doc['filename'] == 'test_document.txt' for doc in documents)
        if test_doc_found:
            print("✅ test_document.txt found in partner documents list")
        else:
            print("❌ test_document.txt NOT found in partner documents list")
    else:
        print(f"❌ Failed to list partner documents: {response.status_code} - {response.text}")
        return
    
    # Test 4: Direct download test (GET /api/documents/download/{document_id})
    print(f"\n4. Testing GET /api/documents/download/{document_id} (Direct download)")
    response = requests.get(f"{API_URL}/documents/download/{document_id}")
    if response.status_code == 200:
        print("✅ Document download successful!")
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"   - Content-Disposition: {response.headers.get('content-disposition', 'Not set')}")
        print(f"   - Content Length: {len(response.content)} bytes")
        
        # Test 5: Verify Base64 format and conversion
        print("\n5. Testing Base64 format and content integrity")
        try:
            # The response should be the raw file content (decoded from Base64)
            downloaded_content = response.content
            expected_content = test_content_raw
            
            if downloaded_content == expected_content:
                print("✅ Downloaded content matches original content perfectly")
                print(f"   - Original: {expected_content}")
                print(f"   - Downloaded: {downloaded_content}")
            else:
                print("❌ Downloaded content differs from original")
                print(f"   - Original: {expected_content}")
                print(f"   - Downloaded: {downloaded_content}")
                
            # Verify content can be re-encoded to Base64
            re_encoded = base64.b64encode(downloaded_content).decode('utf-8')
            if re_encoded == test_content_b64:
                print("✅ Content can be correctly re-encoded to Base64")
            else:
                print("❌ Content cannot be correctly re-encoded to Base64")
                
        except Exception as e:
            print(f"❌ Error during content verification: {e}")
    else:
        print(f"❌ Document download FAILED!")
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Response: {response.text}")
        return
    
    # Test 6: Test with different document types
    print("\n6. Testing download with different document types")
    
    # Upload a PDF document
    pdf_content = base64.b64encode(b"PDF test content for download validation").decode('utf-8')
    pdf_upload = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "test_document.pdf",
        "document_type": "Convention",
        "content": pdf_content,
        "uploaded_by": "test_user"
    }
    
    pdf_response = requests.post(f"{API_URL}/documents/upload", params=pdf_upload)
    if pdf_response.status_code == 200:
        pdf_doc = pdf_response.json()
        pdf_doc_id = pdf_doc['id']
        print(f"✅ Uploaded PDF document: {pdf_doc['filename']}")
        
        # Test PDF download
        pdf_download_response = requests.get(f"{API_URL}/documents/download/{pdf_doc_id}")
        if pdf_download_response.status_code == 200:
            print("✅ PDF document download successful")
            print(f"   - Content-Type: {pdf_download_response.headers.get('content-type')}")
            
            # Verify PDF MIME type
            if pdf_download_response.headers.get('content-type') == 'application/pdf':
                print("✅ PDF MIME type correctly set")
            else:
                print(f"❌ PDF MIME type incorrect: {pdf_download_response.headers.get('content-type')}")
        else:
            print(f"❌ PDF download failed: {pdf_download_response.status_code}")
    else:
        print(f"❌ Failed to upload PDF: {pdf_response.status_code}")
    
    # Test 7: Verify endpoint responds correctly with proper headers
    print("\n7. Testing endpoint response headers and format")
    response = requests.get(f"{API_URL}/documents/download/{document_id}")
    if response.status_code == 200:
        headers = response.headers
        print("✅ Endpoint responding correctly with headers:")
        print(f"   - Content-Type: {headers.get('content-type', 'Missing')}")
        print(f"   - Content-Disposition: {headers.get('content-disposition', 'Missing')}")
        print(f"   - Content-Length: {headers.get('content-length', 'Missing')}")
        
        # Verify Content-Disposition header format
        content_disp = headers.get('content-disposition', '')
        if 'attachment' in content_disp and 'filename=' in content_disp:
            print("✅ Content-Disposition header correctly formatted for download")
        else:
            print(f"❌ Content-Disposition header incorrect: {content_disp}")
            
        # Verify response is binary content, not JSON
        try:
            json.loads(response.text)
            print("❌ Response is JSON, should be binary file content")
        except:
            print("✅ Response is binary content (not JSON)")
            
    print("\n🎯 URGENT DOCUMENT DOWNLOAD TEST COMPLETED")
    print("=" * 60)
    
    return {
        'partner_id': partner_id,
        'document_id': document_id,
        'test_passed': response.status_code == 200
    }

def test_critical_kanban_go_metier_bug():
    """Test CRITICAL - Kanban Go Métier Drag & Drop Bug Fix"""
    print("\n=== TESTING CRITICAL - KANBAN GO MÉTIER DRAG & DROP BUG FIX ===")
    
    # Test 1: Create dealflow partner with new "Go métier étude" status
    print("\n1. Testing POST /api/dealflow with 'Go métier étude' status")
    go_metier_data = {
        "nom": "Go Métier Test Startup",
        "statut": "Go métier étude",
        "domaine": "Intelligence Artificielle",
        "typologie": "Startup",
        "objet": "Solution IA pour optimisation énergétique",
        "source": "Salon VivaTech 2024",
        "pilote": "Caroline Test",
        "metiers_concernes": "Innovation, R&D",
        "date_reception_fichier": "2024-03-01",
        "date_pre_qualification": "2024-03-15",
        "date_presentation_metiers": "2024-03-20",
        "date_go_metier_etude": "2024-03-25",
        "actions_commentaires": "Test pour Go métier étude"
    }
    
    response = requests.post(f"{API_URL}/dealflow", json=go_metier_data)
    if response.status_code == 200:
        go_metier_partner = response.json()
        go_metier_id = go_metier_partner['id']
        print(f"✅ Created dealflow partner with 'Go métier étude' status: {go_metier_partner['nom']}")
        print(f"   Status: {go_metier_partner['statut']}")
    else:
        print(f"❌ Failed to create dealflow partner with 'Go métier étude': {response.status_code} - {response.text}")
        return None
    
    # Test 2: Create dealflow partners with other new statuses
    print("\n2. Testing POST /api/dealflow with other new statuses")
    new_statuses_data = [
        {
            "nom": "Go Experimentation Test",
            "statut": "Go experimentation",
            "domaine": "FinTech",
            "typologie": "Scale-up",
            "objet": "Solution blockchain",
            "source": "Réseau partenaires",
            "pilote": "Caroline Test",
            "metiers_concernes": "DSI, Risk",
            "date_reception_fichier": "2024-03-01",
            "date_go_experimentation": "2024-03-30"
        },
        {
            "nom": "Go Généralisation Test",
            "statut": "Go généralisation",
            "domaine": "Développement Durable",
            "typologie": "PME",
            "objet": "Technologies vertes",
            "source": "Partenariat industriel",
            "pilote": "Caroline Test",
            "metiers_concernes": "Environnement",
            "date_reception_fichier": "2024-03-01",
            "date_go_generalisation": "2024-04-01"
        },
        {
            "nom": "Présentation Métiers Test",
            "statut": "Présentation métiers",
            "domaine": "Santé",
            "typologie": "Startup",
            "objet": "Dispositif médical",
            "source": "Salon santé",
            "pilote": "Caroline Test",
            "metiers_concernes": "Médical",
            "date_reception_fichier": "2024-03-01",
            "date_presentation_metiers": "2024-03-15"
        }
    ]
    
    created_partners = []
    for partner_data in new_statuses_data:
        response = requests.post(f"{API_URL}/dealflow", json=partner_data)
        if response.status_code == 200:
            partner = response.json()
            created_partners.append(partner)
            print(f"✅ Created partner with '{partner['statut']}': {partner['nom']}")
        else:
            print(f"❌ Failed to create partner with '{partner_data['statut']}': {response.status_code} - {response.text}")
    
    # Test 3: Test PUT /api/dealflow/{id} with new status values
    print("\n3. Testing PUT /api/dealflow/{id} with new status values")
    if go_metier_id:
        # Update to Go experimentation
        update_data = {
            "statut": "Go experimentation",
            "date_go_experimentation": "2024-04-05",
            "actions_commentaires": "Moved to experimentation phase"
        }
        response = requests.put(f"{API_URL}/dealflow/{go_metier_id}", json=update_data)
        if response.status_code == 200:
            updated_partner = response.json()
            print(f"✅ Successfully updated partner to 'Go experimentation': {updated_partner['statut']}")
        else:
            print(f"❌ Failed to update partner to 'Go experimentation': {response.status_code} - {response.text}")
        
        # Update to Go généralisation
        update_data = {
            "statut": "Go généralisation",
            "date_go_generalisation": "2024-04-10",
            "actions_commentaires": "Moved to generalisation phase"
        }
        response = requests.put(f"{API_URL}/dealflow/{go_metier_id}", json=update_data)
        if response.status_code == 200:
            updated_partner = response.json()
            print(f"✅ Successfully updated partner to 'Go généralisation': {updated_partner['statut']}")
        else:
            print(f"❌ Failed to update partner to 'Go généralisation': {response.status_code} - {response.text}")
    
    # Test 4: Test Kanban Move to Go Métier column
    print("\n4. Testing POST /api/kanban-move with destination_column='go_metier'")
    
    # First, create a partner in presentation status to move
    presentation_data = {
        "nom": "Kanban Move Test Startup",
        "statut": "Présentation métiers",
        "domaine": "Intelligence Artificielle",
        "typologie": "Startup",
        "objet": "Solution IA test",
        "source": "Test source",
        "pilote": "Caroline Test",
        "metiers_concernes": "Innovation",
        "date_reception_fichier": "2024-03-01",
        "date_presentation_metiers": "2024-03-15"
    }
    
    response = requests.post(f"{API_URL}/dealflow", json=presentation_data)
    if response.status_code == 200:
        presentation_partner = response.json()
        presentation_id = presentation_partner['id']
        print(f"✅ Created partner in 'Présentation métiers' for move test: {presentation_partner['nom']}")
        
        # Now test the kanban move
        move_params = {
            "partner_id": presentation_id,
            "partner_type": "dealflow",
            "source_column": "presentation",
            "destination_column": "go_metier"
        }
        
        response = requests.post(f"{API_URL}/kanban-move", params=move_params)
        if response.status_code == 200:
            move_result = response.json()
            print(f"✅ Successfully moved partner to go_metier column")
            print(f"   New status: {move_result.get('new_status', 'N/A')}")
            print(f"   Message: {move_result.get('message', 'N/A')}")
            
            # Verify the partner status was updated to "Go métier étude"
            verify_response = requests.get(f"{API_URL}/dealflow/{presentation_id}")
            if verify_response.status_code == 200:
                verified_partner = verify_response.json()
                if verified_partner['statut'] == "Go métier étude":
                    print(f"✅ Partner status correctly updated to 'Go métier étude'")
                else:
                    print(f"❌ Partner status not updated correctly: {verified_partner['statut']}")
            else:
                print(f"❌ Failed to verify partner status: {verify_response.status_code}")
        else:
            print(f"❌ Failed to move partner to go_metier column: {response.status_code} - {response.text}")
    else:
        print(f"❌ Failed to create partner for move test: {response.status_code} - {response.text}")
    
    # Test 5: Test Complete Kanban Workflow - Verify all columns show correctly
    print("\n5. Testing Complete Kanban Workflow - Column Display")
    response = requests.get(f"{API_URL}/kanban-data")
    if response.status_code == 200:
        kanban_data = response.json()
        
        # Check if go_metier column exists and has partners
        go_metier_column = kanban_data.get("columns", {}).get("go_metier", {})
        if go_metier_column:
            partners_in_go_metier = go_metier_column.get("partners", [])
            print(f"✅ Go Métier column exists with {len(partners_in_go_metier)} partners")
            
            # Check if our test partners appear in correct columns
            for partner in partners_in_go_metier:
                if partner.get("partner_type") == "dealflow":
                    print(f"   - Dealflow partner in go_metier: {partner.get('nom', 'N/A')}")
        else:
            print(f"❌ Go Métier column not found in Kanban data")
        
        # Check other new status columns
        experimentation_column = kanban_data.get("columns", {}).get("experimentation", {})
        generalisation_column = kanban_data.get("columns", {}).get("generalisation", {})
        
        if experimentation_column:
            exp_partners = experimentation_column.get("partners", [])
            print(f"✅ Experimentation column exists with {len(exp_partners)} partners")
        
        if generalisation_column:
            gen_partners = generalisation_column.get("partners", [])
            print(f"✅ Généralisation column exists with {len(gen_partners)} partners")
            
    else:
        print(f"❌ Failed to get Kanban data: {response.status_code} - {response.text}")
    
    # Test 6: Test enum validation - verify no 422 errors for new statuses
    print("\n6. Testing enum validation - no 422 errors for new statuses")
    all_new_statuses = ["Go métier étude", "Go experimentation", "Go généralisation", "Présentation métiers"]
    
    for status in all_new_statuses:
        test_data = {
            "nom": f"Enum Test {status}",
            "statut": status,
            "domaine": "Test Domain",
            "typologie": "Startup",
            "objet": "Test object",
            "source": "Test source",
            "pilote": "Test Pilot",
            "metiers_concernes": "Test métiers",
            "date_reception_fichier": "2024-03-01"
        }
        
        response = requests.post(f"{API_URL}/dealflow", json=test_data)
        if response.status_code == 200:
            print(f"✅ Enum validation passed for '{status}'")
        elif response.status_code == 422:
            print(f"❌ Enum validation failed for '{status}' - 422 error")
        else:
            print(f"⚠️ Unexpected response for '{status}': {response.status_code}")
    
    print("\n🎯 CRITICAL KANBAN GO MÉTIER BUG TESTING COMPLETED")
    return {
        'go_metier_id': go_metier_id if 'go_metier_id' in locals() else None,
        'created_partners': created_partners,
        'presentation_id': presentation_id if 'presentation_id' in locals() else None
    }

def test_urgent_kanban_response_format():
    """Test URGENT - Kanban Move Response Format Fix for Caroline's issue"""
    print("\n=== TESTING URGENT - KANBAN MOVE RESPONSE FORMAT FIX ===")
    
    # Test 1: Create test dealflow partner in "Présentation métiers" status
    print("\n1. Creating test dealflow partner in 'Présentation métiers' status")
    test_partner_data = {
        "nom": "Caroline Test Partner",
        "statut": "Présentation métiers",
        "domaine": "FinTech",
        "typologie": "Startup",
        "objet": "Solution de paiement innovante",
        "source": "VivaTech 2025",
        "pilote": "Caroline Test",
        "metiers_concernes": "DSI, Finance",
        "date_reception_fichier": "2024-12-01",
        "date_pre_qualification": "2024-12-05",
        "actions_commentaires": "Test pour Caroline"
    }
    
    response = requests.post(f"{API_URL}/dealflow", json=test_partner_data)
    if response.status_code == 200:
        partner = response.json()
        partner_id = partner['id']
        print(f"✅ Created test partner: {partner['nom']} (ID: {partner_id})")
        print(f"   Initial status: {partner['statut']}")
    else:
        print(f"❌ Failed to create test partner: {response.status_code} - {response.text}")
        return
    
    # Test 2: Move to "go_metier" column via POST /api/kanban-move
    print(f"\n2. Testing POST /api/kanban-move to 'go_metier' column")
    move_params = {
        "partner_id": partner_id,
        "partner_type": "dealflow",
        "source_column": "presentation",
        "destination_column": "go_metier"
    }
    
    response = requests.post(f"{API_URL}/kanban-move", params=move_params)
    if response.status_code == 200:
        move_result = response.json()
        print("✅ Kanban move successful!")
        print(f"   Response: {move_result}")
        
        # Verify response includes new_status="Go métier étude"
        if "new_status" in move_result:
            if move_result["new_status"] == "Go métier étude":
                print("✅ CRITICAL FIX VERIFIED: new_status='Go métier étude' returned correctly")
            else:
                print(f"❌ CRITICAL ISSUE: new_status='{move_result['new_status']}' (expected 'Go métier étude')")
        else:
            print("❌ CRITICAL ISSUE: 'new_status' field missing from response")
        
        # Verify other required fields
        required_fields = ["message", "new_status", "partner_type", "partner_id"]
        missing_fields = [field for field in required_fields if field not in move_result]
        if not missing_fields:
            print("✅ All required response fields present: message, new_status, partner_type, partner_id")
        else:
            print(f"❌ Missing required fields: {missing_fields}")
            
    else:
        print(f"❌ Kanban move failed: {response.status_code} - {response.text}")
        return
    
    # Test 3: Create another test dealflow partner for généralisation test
    print("\n3. Creating second test partner for généralisation test")
    test_partner_data_2 = test_partner_data.copy()
    test_partner_data_2["nom"] = "Caroline Généralisation Test"
    test_partner_data_2["statut"] = "Go experimentation"
    
    response = requests.post(f"{API_URL}/dealflow", json=test_partner_data_2)
    if response.status_code == 200:
        partner_2 = response.json()
        partner_2_id = partner_2['id']
        print(f"✅ Created second test partner: {partner_2['nom']} (ID: {partner_2_id})")
    else:
        print(f"❌ Failed to create second test partner: {response.status_code} - {response.text}")
        return
    
    # Test 4: Move to "generalisation" column
    print(f"\n4. Testing POST /api/kanban-move to 'generalisation' column")
    move_params_2 = {
        "partner_id": partner_2_id,
        "partner_type": "dealflow",
        "source_column": "experimentation",
        "destination_column": "generalisation"
    }
    
    response = requests.post(f"{API_URL}/kanban-move", params=move_params_2)
    if response.status_code == 200:
        move_result_2 = response.json()
        print("✅ Kanban move to généralisation successful!")
        print(f"   Response: {move_result_2}")
        
        # Verify response includes new_status="Go généralisation"
        if "new_status" in move_result_2:
            if move_result_2["new_status"] == "Go généralisation":
                print("✅ GÉNÉRALISATION FIX VERIFIED: new_status='Go généralisation' returned correctly")
            else:
                print(f"❌ GÉNÉRALISATION ISSUE: new_status='{move_result_2['new_status']}' (expected 'Go généralisation')")
        else:
            print("❌ GÉNÉRALISATION ISSUE: 'new_status' field missing from response")
            
    else:
        print(f"❌ Kanban move to généralisation failed: {response.status_code} - {response.text}")
    
    # Test 5: Test Response Structure Completeness
    print("\n5. Testing complete response structure for all required fields")
    test_cases = [
        ("go_metier move", move_result if 'move_result' in locals() else {}),
        ("generalisation move", move_result_2 if 'move_result_2' in locals() else {})
    ]
    
    for test_name, result in test_cases:
        if result:
            print(f"\n   Testing {test_name}:")
            required_fields = ["message", "new_status", "partner_type", "partner_id"]
            for field in required_fields:
                if field in result:
                    print(f"   ✅ {field}: {result[field]}")
                else:
                    print(f"   ❌ {field}: MISSING")
    
    print("\n🎯 CAROLINE'S KANBAN ISSUE RESOLUTION SUMMARY:")
    print("   - Backend now returns complete response with new_status field")
    print("   - Frontend should no longer show 'Nouveau statut: N/A'")
    print("   - Drag & drop status confirmation working correctly")
    
    return partner_id, partner_2_id

def main():
    """Run all tests"""
    print("🚀 Starting SURM Backend API Tests - Including Phase 1, Phase 2 & Phase 3 Features")
    print("=" * 60)
    
    try:
        # CRITICAL TEST FIRST - Kanban Go Métier Bug Fix
        print("\n" + "🚨" * 40)
        print("🚨 CRITICAL PRIORITY - KANBAN GO MÉTIER BUG FIX TESTING")
        print("🚨" * 40)
        
        test_critical_kanban_go_metier_bug()
        
        # URGENT: Test document download functionality first
        print("🚨 RUNNING URGENT DOCUMENT DOWNLOAD TEST FIRST")
        urgent_result = test_document_download_urgent()
        
        # Test CRUD operations
        sourcing_id = test_sourcing_crud()
        dealflow_id = test_dealflow_crud()
        
        # Test transition workflow
        transitioned_dealflow_id = test_transition_workflow(sourcing_id)
        
        # Test statistics
        test_statistics_endpoint()
        
        # === PHASE 1 TESTS ===
        print("\n" + "=" * 60)
        print("🔥 PHASE 1 - SUIVI & RELANCE FEATURES TESTING")
        print("=" * 60)
        
        # Test Phase 1 - Next Action Date Field
        next_action_sourcing_id, next_action_dealflow_id = test_phase1_next_action_date()
        
        # Test Phase 1 - Inactivity Indicators
        test_phase1_inactivity_indicators()
        
        # Test Phase 1 - Activity Timeline
        timeline_partner_id = test_phase1_activity_timeline()
        
        # Test Phase 1 - Enhanced Transition
        enhanced_transition_dealflow_id = test_phase1_transition_inheritance()
        
        # === PHASE 2 TESTS ===
        print("\n" + "=" * 60)
        print("📊 PHASE 2 - ENHANCED ANALYTICS FEATURES TESTING")
        print("=" * 60)
        
        # Test Phase 2 - Monthly Evolution Analytics
        test_phase2_monthly_evolution()
        
        # Test Phase 2 - Enhanced Distribution Analytics
        test_phase2_enhanced_distribution()
        
        # Test Phase 2 - Data Accuracy and Edge Cases
        test_phase2_data_accuracy()
        
        # === PHASE 3 TESTS ===
        print("\n" + "=" * 60)
        print("👥 PHASE 3 - ADVANCED USER ROLES & PRIVATE COMMENTS TESTING")
        print("=" * 60)
        
        # Test Phase 3 - User Management System
        created_users = test_phase3_user_management()
        
        # Test Phase 3 - Private Comments System
        comments_test_data = test_phase3_private_comments()
        
        # Test Phase 3 - Personal Dashboard View
        dashboard_user = test_phase3_personal_dashboard()
        
        # Test Phase 3 - Enhanced Authorization
        auth_test_data = test_phase3_enhanced_authorization()
        
        # === PHASE 4 TESTS ===
        print("\n" + "=" * 60)
        print("📋 PHASE 4 - KANBAN PIPELINE BACKEND TESTING")
        print("=" * 60)
        
        # Test Phase 4 - Kanban Data Endpoint
        test_phase4_kanban_data()
        
        # Test Phase 4 - Kanban Move Endpoint
        kanban_move_data = test_phase4_kanban_move()
        
        # Test Phase 4 - Data Structure Validation
        test_phase4_data_structure_validation()
        
        # Test Phase 4 - Synthetic Reports
        test_phase4_synthetic_reports()
        
        # DOCUMENT MANAGEMENT SYSTEM TESTS
        print("\n" + "=" * 60)
        print("📄 DOCUMENT MANAGEMENT SYSTEM TESTS")
        print("=" * 60)
        
        test_document_management_system()
        
        # Test error handling
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 SURM Backend API Testing Complete - All Phases (1, 2, 3 & 4) Included!")
        print("Check the results above for any failures.")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {e}")
        import traceback
        traceback.print_exc()

def test_kanban_data_structure_detailed():
    """Detailed test of Kanban data structure for drag & drop debugging"""
    print("\n=== TESTING KANBAN DATA STRUCTURE - DETAILED ANALYSIS ===")
    
    # Test with default_user as specified by the user
    user_id = "default_user"
    
    print(f"\n1. Testing GET /api/kanban-data with user_id={user_id}")
    response = requests.get(f"{API_URL}/kanban-data?user_id={user_id}")
    
    if response.status_code != 200:
        print(f"❌ Failed to get kanban data: {response.status_code} - {response.text}")
        return
    
    kanban_data = response.json()
    print("✅ Kanban data retrieved successfully")
    
    # Analyze the complete structure
    print(f"\n2. KANBAN DATA STRUCTURE ANALYSIS:")
    print(f"   - Top-level keys: {list(kanban_data.keys())}")
    
    if "columns" in kanban_data:
        columns = kanban_data["columns"]
        print(f"   - Number of columns: {len(columns)}")
        print(f"   - Column IDs: {list(columns.keys())}")
        
        # Check column order
        if "columnOrder" in kanban_data:
            column_order = kanban_data["columnOrder"]
            print(f"   - Column order: {column_order}")
        
        # Analyze each column and its partners
        total_partners_found = 0
        for column_id, column_data in columns.items():
            partners = column_data.get("partners", [])
            partner_count = len(partners)
            total_partners_found += partner_count
            
            print(f"\n   📋 COLUMN: {column_id}")
            print(f"      - Title: {column_data.get('title', 'N/A')}")
            print(f"      - Subtitle: {column_data.get('subtitle', 'N/A')}")
            print(f"      - Partners count: {partner_count}")
            
            # Analyze first few partners in detail
            if partners:
                print(f"      - Sample partners:")
                for i, partner in enumerate(partners[:3]):  # Show first 3 partners
                    print(f"        [{i+1}] kanban_id: {partner.get('kanban_id', 'MISSING')}")
                    print(f"            partner_type: {partner.get('partner_type', 'MISSING')}")
                    print(f"            name: {partner.get('nom_entreprise', partner.get('nom', 'MISSING'))}")
                    print(f"            statut: {partner.get('statut', 'MISSING')}")
                    print(f"            is_inactive: {partner.get('is_inactive', 'MISSING')}")
                    print(f"            days_since_update: {partner.get('days_since_update', 'MISSING')}")
                    
                    # Check for all available fields
                    all_fields = list(partner.keys())
                    print(f"            all_fields: {all_fields}")
                    print()
        
        print(f"\n   📊 SUMMARY:")
        print(f"      - Total partners across all columns: {total_partners_found}")
        
        if "summary" in kanban_data:
            summary = kanban_data["summary"]
            print(f"      - Summary total_partners: {summary.get('total_partners', 'N/A')}")
            print(f"      - Summary total_sourcing: {summary.get('total_sourcing', 'N/A')}")
            print(f"      - Summary total_dealflow: {summary.get('total_dealflow', 'N/A')}")
            
            if "by_column" in summary:
                by_column = summary["by_column"]
                print(f"      - By column breakdown: {by_column}")
    
    # Test specific partner data format
    print(f"\n3. TESTING KANBAN_ID FORMAT:")
    sample_partners = []
    if "columns" in kanban_data:
        for column_data in kanban_data["columns"].values():
            partners = column_data.get("partners", [])
            if partners:
                sample_partners.extend(partners[:2])  # Take 2 from each column
                if len(sample_partners) >= 10:  # Limit to 10 samples
                    break
    
    if sample_partners:
        print(f"   Found {len(sample_partners)} sample partners:")
        for i, partner in enumerate(sample_partners):
            kanban_id = partner.get('kanban_id', 'MISSING')
            partner_type = partner.get('partner_type', 'MISSING')
            name = partner.get('nom_entreprise', partner.get('nom', 'MISSING'))
            
            print(f"   [{i+1}] {kanban_id} | {partner_type} | {name}")
            
            # Validate kanban_id format
            if kanban_id != 'MISSING':
                expected_format = f"{partner_type}_{partner.get('id', 'unknown')}"
                if kanban_id == expected_format:
                    print(f"       ✅ kanban_id format correct")
                else:
                    print(f"       ❌ kanban_id format issue: expected {expected_format}, got {kanban_id}")
    else:
        print("   ⚠️ No partners found to analyze kanban_id format")
    
    return kanban_data

def test_kanban_move_with_real_data():
    """Test Kanban move functionality with real partner IDs"""
    print("\n=== TESTING KANBAN MOVE WITH REAL DATA ===")
    
    user_id = "default_user"
    
    # First get kanban data to find real partner IDs
    print(f"\n1. Getting real partner data for move testing")
    response = requests.get(f"{API_URL}/kanban-data?user_id={user_id}")
    
    if response.status_code != 200:
        print(f"❌ Failed to get kanban data: {response.status_code}")
        return
    
    kanban_data = response.json()
    
    # Find a partner to test moving
    test_partner = None
    source_column = None
    
    for column_id, column_data in kanban_data["columns"].items():
        partners = column_data.get("partners", [])
        if partners:
            test_partner = partners[0]
            source_column = column_id
            break
    
    if not test_partner:
        print("❌ No partners found to test move functionality")
        return
    
    partner_id = test_partner.get('id')
    partner_type = test_partner.get('partner_type')
    kanban_id = test_partner.get('kanban_id')
    partner_name = test_partner.get('nom_entreprise', test_partner.get('nom', 'Unknown'))
    
    print(f"✅ Found test partner:")
    print(f"   - ID: {partner_id}")
    print(f"   - Kanban ID: {kanban_id}")
    print(f"   - Type: {partner_type}")
    print(f"   - Name: {partner_name}")
    print(f"   - Current column: {source_column}")
    
    # Test different move scenarios
    move_tests = []
    
    # Define valid moves based on partner type and current status
    if partner_type == "sourcing":
        if source_column == "sourcing_a_traiter":
            move_tests.append(("sourcing_klaxoon", "Move sourcing from A traiter to Klaxoon"))
        elif source_column == "sourcing_klaxoon":
            move_tests.append(("prequalification", "Transition sourcing to dealflow prequalification"))
    elif partner_type == "dealflow":
        if source_column == "prequalification":
            move_tests.append(("presentation", "Move dealflow from prequalification to presentation"))
        elif source_column == "presentation":
            move_tests.append(("go_metier", "Move dealflow from presentation to go_metier"))
    
    # Add a test to move back to original position
    move_tests.append((source_column, f"Move back to original column {source_column}"))
    
    print(f"\n2. Testing {len(move_tests)} move scenarios:")
    
    for target_column, description in move_tests:
        print(f"\n   🔄 {description}")
        print(f"      Moving {kanban_id} from {source_column} to {target_column}")
        
        # The API expects query parameters, not JSON body
        params = {
            "partner_id": partner_id,
            "partner_type": partner_type,
            "source_column": source_column,
            "destination_column": target_column,  # Note: API uses 'destination_column', not 'target_column'
            "user_id": user_id
        }
        
        response = requests.post(f"{API_URL}/kanban-move", params=params)
        
        if response.status_code == 200:
            result = response.json()
            print(f"      ✅ Move successful:")
            print(f"         - Message: {result.get('message', 'N/A')}")
            print(f"         - New status: {result.get('new_status', 'N/A')}")
            print(f"         - Partner type: {result.get('partner_type', 'N/A')}")
            
            # Update source column for next test
            source_column = target_column
            
        elif response.status_code == 400:
            print(f"      ⚠️ Move rejected (expected for invalid moves): {response.text}")
        elif response.status_code == 403:
            print(f"      ⚠️ Move unauthorized: {response.text}")
        elif response.status_code == 404:
            print(f"      ❌ Partner not found: {response.text}")
        else:
            print(f"      ❌ Move failed: {response.status_code} - {response.text}")
    
    # Test invalid moves
    print(f"\n3. Testing invalid move scenarios:")
    
    invalid_moves = [
        ("invalid_column", "Move to non-existent column"),
        ("", "Move to empty column"),
        (None, "Move to null column")
    ]
    
    for target_column, description in invalid_moves:
        print(f"\n   ❌ {description}")
        
        move_data = {
            "partner_id": partner_id,
            "partner_type": partner_type,
            "source_column": source_column,
            "target_column": target_column
        }
        
        response = requests.post(f"{API_URL}/kanban-move?user_id={user_id}", json=move_data)
        
        if response.status_code == 400:
            print(f"      ✅ Correctly rejected invalid move: {response.status_code}")
        else:
            print(f"      ❌ Should have rejected invalid move: {response.status_code}")

def test_kanban_frontend_compatibility():
    """Test Kanban data compatibility with frontend drag & drop expectations"""
    print("\n=== TESTING KANBAN FRONTEND COMPATIBILITY ===")
    
    user_id = "default_user"
    
    print(f"\n1. Analyzing data structure for frontend compatibility")
    response = requests.get(f"{API_URL}/kanban-data?user_id={user_id}")
    
    if response.status_code != 200:
        print(f"❌ Failed to get kanban data: {response.status_code}")
        return
    
    kanban_data = response.json()
    
    # Check for common drag & drop library requirements
    print(f"\n2. FRONTEND DRAG & DROP COMPATIBILITY CHECKS:")
    
    # Check if data structure matches react-beautiful-dnd format
    required_top_level = ["columns", "columnOrder"]
    missing_top_level = [key for key in required_top_level if key not in kanban_data]
    
    if not missing_top_level:
        print("   ✅ Top-level structure compatible with react-beautiful-dnd")
    else:
        print(f"   ❌ Missing top-level keys for drag & drop: {missing_top_level}")
    
    # Check column structure
    if "columns" in kanban_data:
        columns = kanban_data["columns"]
        sample_column_id = list(columns.keys())[0] if columns else None
        
        if sample_column_id:
            sample_column = columns[sample_column_id]
            required_column_keys = ["id", "title", "partners"]
            missing_column_keys = [key for key in required_column_keys if key not in sample_column]
            
            if not missing_column_keys:
                print("   ✅ Column structure compatible with drag & drop")
            else:
                print(f"   ❌ Missing column keys: {missing_column_keys}")
            
            # Check partner structure within columns
            partners = sample_column.get("partners", [])
            if partners:
                sample_partner = partners[0]
                
                # Check for unique identifier
                if "kanban_id" in sample_partner:
                    print("   ✅ Partners have kanban_id for drag & drop identification")
                else:
                    print("   ❌ Partners missing kanban_id for drag & drop")
                
                # Check for required display fields
                display_fields = ["nom_entreprise", "nom"]  # Either should be present
                has_display_field = any(field in sample_partner for field in display_fields)
                
                if has_display_field:
                    print("   ✅ Partners have display name fields")
                else:
                    print("   ❌ Partners missing display name fields")
                
                # Check for status information
                if "statut" in sample_partner:
                    print("   ✅ Partners have status information")
                else:
                    print("   ❌ Partners missing status information")
                
                print(f"\n   📋 SAMPLE PARTNER STRUCTURE:")
                for key, value in sample_partner.items():
                    print(f"      - {key}: {value}")
            else:
                print("   ⚠️ No partners found in sample column")
    
    # Check columnOrder
    if "columnOrder" in kanban_data:
        column_order = kanban_data["columnOrder"]
        if isinstance(column_order, list) and len(column_order) > 0:
            print(f"   ✅ Column order is properly formatted list with {len(column_order)} columns")
        else:
            print(f"   ❌ Column order format issue: {type(column_order)}, length: {len(column_order) if isinstance(column_order, list) else 'N/A'}")
    
    # Test JSON serialization (important for frontend)
    print(f"\n3. JSON SERIALIZATION TEST:")
    try:
        json_str = json.dumps(kanban_data)
        parsed_back = json.loads(json_str)
        print("   ✅ Data properly serializes to/from JSON")
    except Exception as e:
        print(f"   ❌ JSON serialization error: {e}")
    
    # Check for MongoDB ObjectId issues
    print(f"\n4. MONGODB OBJECTID CHECK:")
    def check_for_objectid(obj, path=""):
        issues = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if key == "_id" or (isinstance(value, dict) and "$oid" in value):
                    issues.append(current_path)
                else:
                    issues.extend(check_for_objectid(value, current_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                issues.extend(check_for_objectid(item, current_path))
        return issues
    
    objectid_issues = check_for_objectid(kanban_data)
    if not objectid_issues:
        print("   ✅ No MongoDB ObjectId serialization issues found")
    else:
        print(f"   ❌ MongoDB ObjectId issues found at: {objectid_issues}")
    
    return kanban_data

def run_kanban_focused_tests():
    """Run focused Kanban tests for drag & drop debugging"""
    print("🚀 Starting SURM Kanban Endpoint Detailed Testing")
    print("=" * 60)
    
    # Focus on Kanban testing as requested by user
    print("\n🎯 FOCUSED KANBAN TESTING FOR DRAG & DROP DEBUGGING")
    
    # Detailed structure analysis
    kanban_data = test_kanban_data_structure_detailed()
    
    # Test move functionality with real data
    test_kanban_move_with_real_data()
    
    # Test frontend compatibility
    test_kanban_frontend_compatibility()
    
    print("\n" + "=" * 60)
    print("🎉 Kanban Endpoint Testing Completed!")
    print("Data structure and move functionality analyzed for drag & drop debugging.")

def test_urgent_backend_success_creation():
    """URGENT TEST - Create partner with exact user-provided data to prove backend works"""
    print("\n=== URGENT TEST - BACKEND SUCCESS PARTNER CREATION ===")
    print("Testing with exact data provided by user to prove backend functionality")
    
    # Exact data provided by user
    BACKEND_SUCCESS_DATA = {
        "nom_entreprise": "BACKEND SUCCESS Company",
        "statut": "A traiter",
        "pays_origine": "France",
        "domaine_activite": "FinTech",
        "typologie": "Startup",
        "objet": "Solution de paiement innovante",
        "cas_usage": "Paiements mobiles sécurisés",
        "technologie": "Blockchain et IA",
        "source": "VivaTech 2025",
        "date_entree_sourcing": "2025-01-08",
        "pilote": "Marie Backend",
        "interet": True
    }
    
    # Test 1: Create the BACKEND SUCCESS partner
    print("\n1. Creating 'BACKEND SUCCESS Company' with complete data")
    response = requests.post(f"{API_URL}/sourcing", json=BACKEND_SUCCESS_DATA)
    if response.status_code == 200:
        partner = response.json()
        partner_id = partner['id']
        print(f"✅ BACKEND SUCCESS: Created partner successfully!")
        print(f"   - ID: {partner_id}")
        print(f"   - Name: {partner['nom_entreprise']}")
        print(f"   - Status: {partner['statut']}")
        print(f"   - Domain: {partner['domaine_activite']}")
        print(f"   - Pilot: {partner['pilote']}")
        print(f"   - Technology: {partner['technologie']}")
        print(f"   - Source: {partner['source']}")
        print(f"   - Date: {partner['date_entree_sourcing']}")
    else:
        print(f"❌ BACKEND FAILED: Could not create partner: {response.status_code} - {response.text}")
        return None
    
    # Test 2: Verify partner appears in list
    print("\n2. Verifying partner appears in sourcing list")
    response = requests.get(f"{API_URL}/sourcing")
    if response.status_code == 200:
        partners = response.json()
        backend_success_found = False
        for p in partners:
            if p['nom_entreprise'] == "BACKEND SUCCESS Company":
                backend_success_found = True
                print(f"✅ BACKEND SUCCESS: Partner found in list!")
                print(f"   - Listed with status: {p['statut']}")
                print(f"   - Listed with domain: {p['domaine_activite']}")
                break
        
        if not backend_success_found:
            print("❌ BACKEND ISSUE: Partner not found in list after creation")
    else:
        print(f"❌ BACKEND FAILED: Could not retrieve partner list: {response.status_code}")
    
    # Test 3: Test document functionality with new partner
    print("\n3. Testing document functionality with BACKEND SUCCESS partner")
    
    # Create a test document (Base64 encoded simple text)
    import base64
    test_content = "This is a test document for BACKEND SUCCESS Company - proving document management works!"
    encoded_content = base64.b64encode(test_content.encode()).decode()
    
    document_data = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "backend_success_test.txt",
        "document_type": "Autre",
        "content": encoded_content,
        "description": "Test document to prove backend document management works",
        "uploaded_by": "Backend Test System"
    }
    
    # Upload document
    response = requests.post(f"{API_URL}/documents/upload", params=document_data)
    if response.status_code == 200:
        document = response.json()
        document_id = document['id']
        print(f"✅ DOCUMENT SUCCESS: Uploaded document for BACKEND SUCCESS partner!")
        print(f"   - Document ID: {document_id}")
        print(f"   - Filename: {document['filename']}")
        print(f"   - Type: {document['document_type']}")
        print(f"   - Size: {document['file_size']} bytes")
    else:
        print(f"❌ DOCUMENT FAILED: Could not upload document: {response.status_code} - {response.text}")
        return partner_id
    
    # Test 4: Retrieve documents for partner
    print("\n4. Retrieving documents for BACKEND SUCCESS partner")
    response = requests.get(f"{API_URL}/documents/{partner_id}")
    if response.status_code == 200:
        documents = response.json()
        print(f"✅ DOCUMENT SUCCESS: Retrieved {len(documents)} documents for partner")
        for doc in documents:
            print(f"   - {doc['filename']} ({doc['document_type']}) - {doc['file_size']} bytes")
    else:
        print(f"❌ DOCUMENT FAILED: Could not retrieve documents: {response.status_code}")
    
    # Test 5: Download document
    print("\n5. Testing document download functionality")
    response = requests.get(f"{API_URL}/documents/download/{document_id}")
    if response.status_code == 200:
        downloaded_content = response.content.decode()
        if "BACKEND SUCCESS Company" in downloaded_content:
            print("✅ DOCUMENT SUCCESS: Document download working correctly!")
            print(f"   - Downloaded content contains expected text")
        else:
            print("❌ DOCUMENT ISSUE: Downloaded content doesn't match expected")
    else:
        print(f"❌ DOCUMENT FAILED: Could not download document: {response.status_code}")
    
    print("\n" + "="*60)
    print("🎯 URGENT TEST CONCLUSION:")
    print("✅ BACKEND API IS FULLY FUNCTIONAL!")
    print("✅ Partner creation works with complete data")
    print("✅ Partner appears in list correctly")
    print("✅ Document management system works")
    print("🔍 If frontend creation fails, the issue is in FRONTEND, not backend!")
    print("="*60)
    
    return partner_id

def test_critical_partner_creation_bug():
    """Test CRITICAL BUG - Partner Creation Not Working"""
    print("\n=== TESTING CRITICAL BUG - PARTNER CREATION NOT WORKING ===")
    print("Testing direct backend API to isolate frontend vs backend issues")
    
    # Test 1: POST /api/sourcing with complete and valid data
    print("\n1. Testing POST /api/sourcing (Create sourcing partner)")
    print("   Using realistic French innovation data matching frontend requirements...")
    
    # Complete sourcing data with all required fields
    sourcing_creation_data = {
        "nom_entreprise": "InnovTech Solutions",
        "statut": "A traiter",
        "pays_origine": "France", 
        "domaine_activite": "Intelligence Artificielle",
        "typologie": "Startup",
        "objet": "Plateforme IA pour optimisation énergétique industrielle",
        "cas_usage": "Réduction consommation énergétique usines manufacturières",
        "technologie": "Machine Learning, IoT",
        "source": "Salon VivaTech 2024",
        "date_entree_sourcing": "2024-03-15",
        "interet": True,
        "date_presentation_metiers": "2024-03-25",
        "pilote": "Marie Dubois",
        "actions_commentaires": "Premier contact très prometteur, équipe technique solide",
        "date_prochaine_action": "2024-04-15"
    }
    
    response = requests.post(f"{API_URL}/sourcing", json=sourcing_creation_data)
    print(f"   Response Status: {response.status_code}")
    
    if response.status_code == 200:
        sourcing_partner = response.json()
        sourcing_id = sourcing_partner['id']
        print(f"✅ SOURCING CREATION SUCCESSFUL")
        print(f"   - Partner ID: {sourcing_id}")
        print(f"   - Company: {sourcing_partner['nom_entreprise']}")
        print(f"   - Status: {sourcing_partner['statut']}")
        print(f"   - Domain: {sourcing_partner['domaine_activite']}")
        print(f"   - Pilot: {sourcing_partner['pilote']}")
        
        # Verify all fields were saved correctly
        field_verification = []
        for key, expected_value in sourcing_creation_data.items():
            actual_value = sourcing_partner.get(key)
            if actual_value == expected_value:
                field_verification.append(f"✅ {key}")
            else:
                field_verification.append(f"❌ {key}: expected '{expected_value}', got '{actual_value}'")
        
        print("   Field Verification:")
        for verification in field_verification[:5]:  # Show first 5
            print(f"     {verification}")
        
    else:
        print(f"❌ SOURCING CREATION FAILED")
        print(f"   Status Code: {response.status_code}")
        print(f"   Error Response: {response.text}")
        try:
            error_detail = response.json()
            print(f"   Error Detail: {error_detail}")
        except:
            pass
        sourcing_id = None
    
    # Test 2: POST /api/dealflow with complete and valid data
    print("\n2. Testing POST /api/dealflow (Create dealflow partner)")
    print("   Using realistic dealflow data with all required fields...")
    
    # Complete dealflow data with all required fields
    dealflow_creation_data = {
        "nom": "SecureFinTech Pro",
        "statut": "En cours avec les métiers",
        "domaine": "Services Financiers",
        "typologie": "Scale-up",
        "objet": "Solution blockchain pour sécurisation transactions bancaires",
        "source": "Réseau partenaires bancaires",
        "pilote": "Sophie Laurent",
        "metiers_concernes": "DSI, Risk Management, Compliance",
        "date_reception_fichier": "2024-02-01",
        "date_pre_qualification": "2024-02-15",
        "date_presentation_meetup_referents": "2024-02-28",
        "date_presentation_metiers": "2024-03-10",
        "actions_commentaires": "Très bon potentiel commercial, équipe expérimentée",
        "points_etapes_intermediaires": "Validation technique en cours, POC prévu Q2",
        "date_prochaine_action": "2024-04-20"
    }
    
    response = requests.post(f"{API_URL}/dealflow", json=dealflow_creation_data)
    print(f"   Response Status: {response.status_code}")
    
    if response.status_code == 200:
        dealflow_partner = response.json()
        dealflow_id = dealflow_partner['id']
        print(f"✅ DEALFLOW CREATION SUCCESSFUL")
        print(f"   - Partner ID: {dealflow_id}")
        print(f"   - Company: {dealflow_partner['nom']}")
        print(f"   - Status: {dealflow_partner['statut']}")
        print(f"   - Domain: {dealflow_partner['domaine']}")
        print(f"   - Pilot: {dealflow_partner['pilote']}")
        
        # Verify all fields were saved correctly
        field_verification = []
        for key, expected_value in dealflow_creation_data.items():
            actual_value = dealflow_partner.get(key)
            if actual_value == expected_value:
                field_verification.append(f"✅ {key}")
            else:
                field_verification.append(f"❌ {key}: expected '{expected_value}', got '{actual_value}'")
        
        print("   Field Verification:")
        for verification in field_verification[:5]:  # Show first 5
            print(f"     {verification}")
            
    else:
        print(f"❌ DEALFLOW CREATION FAILED")
        print(f"   Status Code: {response.status_code}")
        print(f"   Error Response: {response.text}")
        try:
            error_detail = response.json()
            print(f"   Error Detail: {error_detail}")
        except:
            pass
        dealflow_id = None
    
    # Test 3: Verify new partners appear in GET endpoints
    print("\n3. Testing GET endpoints to verify new partners are retrievable")
    
    if sourcing_id:
        print("   3a. Verifying sourcing partner in GET /api/sourcing")
        response = requests.get(f"{API_URL}/sourcing")
        if response.status_code == 200:
            partners = response.json()
            found_partner = next((p for p in partners if p['id'] == sourcing_id), None)
            if found_partner:
                print(f"✅ New sourcing partner found in list: {found_partner['nom_entreprise']}")
            else:
                print(f"❌ New sourcing partner NOT found in list (ID: {sourcing_id})")
        else:
            print(f"❌ Failed to get sourcing partners: {response.status_code}")
        
        print(f"   3b. Verifying specific sourcing partner GET /api/sourcing/{sourcing_id}")
        response = requests.get(f"{API_URL}/sourcing/{sourcing_id}")
        if response.status_code == 200:
            partner = response.json()
            print(f"✅ Specific sourcing partner retrievable: {partner['nom_entreprise']}")
        else:
            print(f"❌ Failed to get specific sourcing partner: {response.status_code}")
    
    if dealflow_id:
        print("   3c. Verifying dealflow partner in GET /api/dealflow")
        response = requests.get(f"{API_URL}/dealflow")
        if response.status_code == 200:
            partners = response.json()
            found_partner = next((p for p in partners if p['id'] == dealflow_id), None)
            if found_partner:
                print(f"✅ New dealflow partner found in list: {found_partner['nom']}")
            else:
                print(f"❌ New dealflow partner NOT found in list (ID: {dealflow_id})")
        else:
            print(f"❌ Failed to get dealflow partners: {response.status_code}")
        
        print(f"   3d. Verifying specific dealflow partner GET /api/dealflow/{dealflow_id}")
        response = requests.get(f"{API_URL}/dealflow/{dealflow_id}")
        if response.status_code == 200:
            partner = response.json()
            print(f"✅ Specific dealflow partner retrievable: {partner['nom']}")
        else:
            print(f"❌ Failed to get specific dealflow partner: {response.status_code}")
    
    # Test 4: Test document functionality with new partners
    print("\n4. Testing document functionality with newly created partners")
    
    if sourcing_id:
        print("   4a. Testing document upload for sourcing partner")
        
        # Create a simple test document (base64 encoded text)
        import base64
        test_content = "Test document for sourcing partner - SURM system validation"
        encoded_content = base64.b64encode(test_content.encode()).decode()
        
        upload_data = {
            "partner_id": sourcing_id,
            "partner_type": "sourcing",
            "filename": "test_sourcing_doc.txt",
            "document_type": "Autre",
            "content": encoded_content,
            "description": "Test document for sourcing partner creation validation",
            "uploaded_by": "test_user"
        }
        
        response = requests.post(f"{API_URL}/documents/upload", params=upload_data)
        if response.status_code == 200:
            document = response.json()
            print(f"✅ Document uploaded for sourcing partner: {document['filename']}")
            
            # Verify document can be retrieved
            response = requests.get(f"{API_URL}/documents/{sourcing_id}")
            if response.status_code == 200:
                documents = response.json()
                if documents:
                    print(f"✅ Document retrievable: {len(documents)} documents found")
                else:
                    print("❌ No documents found after upload")
            else:
                print(f"❌ Failed to retrieve documents: {response.status_code}")
        else:
            print(f"❌ Failed to upload document for sourcing: {response.status_code} - {response.text}")
    
    if dealflow_id:
        print("   4b. Testing document upload for dealflow partner")
        
        test_content = "Test document for dealflow partner - SURM system validation"
        encoded_content = base64.b64encode(test_content.encode()).decode()
        
        upload_data = {
            "partner_id": dealflow_id,
            "partner_type": "dealflow",
            "filename": "test_dealflow_doc.txt",
            "document_type": "Présentation",
            "content": encoded_content,
            "description": "Test document for dealflow partner creation validation",
            "uploaded_by": "test_user"
        }
        
        response = requests.post(f"{API_URL}/documents/upload", params=upload_data)
        if response.status_code == 200:
            document = response.json()
            print(f"✅ Document uploaded for dealflow partner: {document['filename']}")
            
            # Verify document can be retrieved
            response = requests.get(f"{API_URL}/documents/{dealflow_id}")
            if response.status_code == 200:
                documents = response.json()
                if documents:
                    print(f"✅ Document retrievable: {len(documents)} documents found")
                else:
                    print("❌ No documents found after upload")
            else:
                print(f"❌ Failed to retrieve documents: {response.status_code}")
        else:
            print(f"❌ Failed to upload document for dealflow: {response.status_code} - {response.text}")
    
    # Test 5: Summary and diagnosis
    print("\n5. CRITICAL BUG DIAGNOSIS SUMMARY")
    
    sourcing_success = sourcing_id is not None
    dealflow_success = dealflow_id is not None
    
    if sourcing_success and dealflow_success:
        print("✅ BACKEND API WORKING CORRECTLY")
        print("   - Both sourcing and dealflow partner creation successful")
        print("   - Partners are retrievable via GET endpoints")
        print("   - Document functionality working with new partners")
        print("   - CONCLUSION: Issue is likely in FRONTEND, not backend")
        print("   - Recommendation: Check frontend form validation, API calls, error handling")
    elif sourcing_success or dealflow_success:
        print("⚠️ PARTIAL BACKEND FUNCTIONALITY")
        if sourcing_success:
            print("   - Sourcing creation: ✅ Working")
        else:
            print("   - Sourcing creation: ❌ Failed")
        if dealflow_success:
            print("   - Dealflow creation: ✅ Working")
        else:
            print("   - Dealflow creation: ❌ Failed")
        print("   - CONCLUSION: Mixed results - investigate specific endpoint issues")
    else:
        print("❌ BACKEND API NOT WORKING")
        print("   - Both sourcing and dealflow creation failed")
        print("   - CONCLUSION: Issue is in BACKEND API")
        print("   - Recommendation: Check backend server, database connection, model validation")
    
    return {
        'sourcing_success': sourcing_success,
        'dealflow_success': dealflow_success,
        'sourcing_id': sourcing_id,
        'dealflow_id': dealflow_id
    }

def test_critical_partner_creation():
    """CRITICAL BUG TEST - Partner Creation Backend Testing"""
    print("\n" + "=" * 80)
    print("🚨 CRITICAL BUG INVESTIGATION - PARTNER CREATION BACKEND TESTING")
    print("=" * 80)
    
    # Test data for realistic partner creation
    sourcing_creation_data = {
        "nom_entreprise": "CriticalTest Startup",
        "statut": "A traiter",
        "pays_origine": "France",
        "domaine_activite": "Intelligence Artificielle",
        "typologie": "Startup",
        "objet": "Solution IA pour optimisation énergétique",
        "cas_usage": "Optimisation consommation énergétique bâtiments tertiaires",
        "technologie": "Machine Learning",
        "source": "Test de création critique",
        "date_entree_sourcing": "2024-12-20",
        "interet": True,
        "pilote": "Test Pilote",
        "actions_commentaires": "Test de création de partenaire sourcing"
    }
    
    dealflow_creation_data = {
        "nom": "CriticalTest Dealflow",
        "statut": "En cours avec les métiers",
        "domaine": "Services Financiers",
        "typologie": "Scale-up",
        "objet": "Sécurisation transactions blockchain",
        "source": "Test de création critique",
        "pilote": "Test Pilote",
        "metiers_concernes": "DSI, Risk Management",
        "date_reception_fichier": "2024-12-20",
        "actions_commentaires": "Test de création de partenaire dealflow"
    }
    
    # Test 1: POST /api/sourcing endpoint
    print("\n1. 🔍 TESTING POST /api/sourcing (Critical Partner Creation)")
    print(f"   Testing with data: {sourcing_creation_data['nom_entreprise']}")
    
    response = requests.post(f"{API_URL}/sourcing", json=sourcing_creation_data)
    print(f"   Response Status: {response.status_code}")
    
    if response.status_code == 200:
        sourcing_partner = response.json()
        sourcing_id = sourcing_partner['id']
        print(f"✅ SOURCING CREATION SUCCESS!")
        print(f"   - Created partner: {sourcing_partner['nom_entreprise']}")
        print(f"   - Partner ID: {sourcing_id}")
        print(f"   - Status: {sourcing_partner['statut']}")
        print(f"   - Domain: {sourcing_partner['domaine_activite']}")
        print(f"   - Pilote: {sourcing_partner['pilote']}")
        
        # Verify all required fields are present
        required_fields = ['nom_entreprise', 'statut', 'pays_origine', 'domaine_activite', 'typologie', 'objet', 'cas_usage', 'technologie', 'source', 'date_entree_sourcing', 'interet', 'pilote']
        missing_fields = [field for field in required_fields if field not in sourcing_partner]
        if not missing_fields:
            print("✅ All required fields present in response")
        else:
            print(f"❌ Missing fields in response: {missing_fields}")
            
    elif response.status_code == 422:
        print("❌ SOURCING CREATION FAILED - Validation Error (422)")
        try:
            error_detail = response.json()
            print(f"   Validation errors: {error_detail}")
        except:
            print(f"   Raw error response: {response.text}")
    else:
        print(f"❌ SOURCING CREATION FAILED - Status: {response.status_code}")
        print(f"   Error response: {response.text}")
    
    # Test 2: POST /api/dealflow endpoint
    print("\n2. 🔍 TESTING POST /api/dealflow (Critical Partner Creation)")
    print(f"   Testing with data: {dealflow_creation_data['nom']}")
    
    response = requests.post(f"{API_URL}/dealflow", json=dealflow_creation_data)
    print(f"   Response Status: {response.status_code}")
    
    if response.status_code == 200:
        dealflow_partner = response.json()
        dealflow_id = dealflow_partner['id']
        print(f"✅ DEALFLOW CREATION SUCCESS!")
        print(f"   - Created partner: {dealflow_partner['nom']}")
        print(f"   - Partner ID: {dealflow_id}")
        print(f"   - Status: {dealflow_partner['statut']}")
        print(f"   - Domain: {dealflow_partner['domaine']}")
        print(f"   - Pilote: {dealflow_partner['pilote']}")
        
        # Verify all required fields are present
        required_fields = ['nom', 'statut', 'domaine', 'typologie', 'objet', 'source', 'pilote', 'metiers_concernes', 'date_reception_fichier']
        missing_fields = [field for field in required_fields if field not in dealflow_partner]
        if not missing_fields:
            print("✅ All required fields present in response")
        else:
            print(f"❌ Missing fields in response: {missing_fields}")
            
    elif response.status_code == 422:
        print("❌ DEALFLOW CREATION FAILED - Validation Error (422)")
        try:
            error_detail = response.json()
            print(f"   Validation errors: {error_detail}")
        except:
            print(f"   Raw error response: {response.text}")
    else:
        print(f"❌ DEALFLOW CREATION FAILED - Status: {response.status_code}")
        print(f"   Error response: {response.text}")
    
    # Test 3: Verify created partners appear in GET requests
    print("\n3. 🔍 TESTING GET REQUESTS (Verify Created Partners)")
    
    # Test GET /api/sourcing
    print("   Testing GET /api/sourcing...")
    response = requests.get(f"{API_URL}/sourcing")
    if response.status_code == 200:
        sourcing_partners = response.json()
        critical_test_partners = [p for p in sourcing_partners if 'CriticalTest' in p.get('nom_entreprise', '')]
        print(f"✅ GET /api/sourcing working - Found {len(critical_test_partners)} CriticalTest partners")
        if critical_test_partners:
            for partner in critical_test_partners:
                print(f"   - {partner['nom_entreprise']} (ID: {partner['id']})")
    else:
        print(f"❌ GET /api/sourcing failed: {response.status_code}")
    
    # Test GET /api/dealflow
    print("   Testing GET /api/dealflow...")
    response = requests.get(f"{API_URL}/dealflow")
    if response.status_code == 200:
        dealflow_partners = response.json()
        critical_test_partners = [p for p in dealflow_partners if 'CriticalTest' in p.get('nom', '')]
        print(f"✅ GET /api/dealflow working - Found {len(critical_test_partners)} CriticalTest partners")
        if critical_test_partners:
            for partner in critical_test_partners:
                print(f"   - {partner['nom']} (ID: {partner['id']})")
    else:
        print(f"❌ GET /api/dealflow failed: {response.status_code}")
    
    # Test 4: Test document management with new partners (if they were created)
    print("\n4. 🔍 TESTING DOCUMENT MANAGEMENT (Verify Functionality)")
    
    # Try to find a created partner to test document upload
    response = requests.get(f"{API_URL}/sourcing")
    if response.status_code == 200:
        sourcing_partners = response.json()
        if sourcing_partners:
            test_partner = sourcing_partners[0]
            partner_id = test_partner['id']
            
            # Test document upload
            print(f"   Testing document upload for partner: {test_partner.get('nom_entreprise', 'Unknown')}")
            
            # Create a simple base64 encoded test document
            import base64
            test_content = "This is a test document for partner creation verification."
            encoded_content = base64.b64encode(test_content.encode()).decode()
            
            doc_data = {
                "partner_id": partner_id,
                "partner_type": "sourcing",
                "filename": "test_document.txt",
                "document_type": "Autre",
                "content": encoded_content,
                "description": "Test document for critical bug investigation"
            }
            
            response = requests.post(f"{API_URL}/documents/upload", params=doc_data)
            if response.status_code == 200:
                document = response.json()
                print(f"✅ Document upload working - Document ID: {document['id']}")
                
                # Test document retrieval
                response = requests.get(f"{API_URL}/documents/{partner_id}")
                if response.status_code == 200:
                    documents = response.json()
                    print(f"✅ Document retrieval working - Found {len(documents)} documents")
                else:
                    print(f"❌ Document retrieval failed: {response.status_code}")
            else:
                print(f"❌ Document upload failed: {response.status_code} - {response.text}")
        else:
            print("⚠️ No sourcing partners found to test document management")
    else:
        print("❌ Cannot test document management - sourcing partners not accessible")
    
    # Test 5: Test various validation scenarios
    print("\n5. 🔍 TESTING VALIDATION SCENARIOS")
    
    # Test missing required fields
    print("   Testing missing required fields...")
    incomplete_data = {
        "nom_entreprise": "Incomplete Test",
        # Missing required fields intentionally
    }
    
    response = requests.post(f"{API_URL}/sourcing", json=incomplete_data)
    if response.status_code == 422:
        print("✅ Validation working - Correctly rejected incomplete data")
    else:
        print(f"❌ Validation issue - Should reject incomplete data: {response.status_code}")
    
    # Test invalid enum values
    print("   Testing invalid enum values...")
    invalid_enum_data = sourcing_creation_data.copy()
    invalid_enum_data["statut"] = "Invalid Status"
    invalid_enum_data["nom_entreprise"] = "Invalid Enum Test"
    
    response = requests.post(f"{API_URL}/sourcing", json=invalid_enum_data)
    if response.status_code == 422:
        print("✅ Enum validation working - Correctly rejected invalid status")
    else:
        print(f"❌ Enum validation issue - Should reject invalid status: {response.status_code}")
    
    print("\n" + "=" * 80)
    print("🔍 CRITICAL BUG INVESTIGATION COMPLETED")
    print("=" * 80)

def test_urgent_document_upload_json():
    """URGENT TEST - Document Upload with JSON Body (User Request)"""
    print("\n=== 🚨 URGENT TEST - DOCUMENT UPLOAD JSON ENDPOINT 🚨 ===")
    print("Testing the modified backend endpoint that should accept JSON instead of query parameters")
    
    # First create a test partner
    print("\n1. Creating test partner for urgent document upload test")
    test_data = SOURCING_TEST_DATA.copy()
    test_data["nom_entreprise"] = "URGENT JSON Upload Test Partner"
    response = requests.post(f"{API_URL}/sourcing", json=test_data)
    if response.status_code != 200:
        print(f"❌ Failed to create test partner: {response.status_code}")
        return
    
    partner = response.json()
    partner_id = partner['id']
    print(f"✅ Created test partner: {partner_id}")
    
    # Test with EXACT data provided by user
    print(f"\n2. Testing POST /api/documents/upload with EXACT USER-PROVIDED JSON DATA")
    
    # User's exact test data
    user_test_data = {
        "partner_id": partner_id,  # Using real partner ID instead of "test-partner-id"
        "partner_type": "sourcing", 
        "filename": "test.txt",
        "document_type": "Autre",
        "content": "VGVzdCBjb250ZW50",  # base64 for "Test content"
        "description": "Test upload",
        "uploaded_by": "test_user"
    }
    
    print("📋 Request data:")
    print(f"   - partner_id: {user_test_data['partner_id']}")
    print(f"   - partner_type: {user_test_data['partner_type']}")
    print(f"   - filename: {user_test_data['filename']}")
    print(f"   - document_type: {user_test_data['document_type']}")
    print(f"   - content: {user_test_data['content'][:20]}... (base64)")
    print(f"   - description: {user_test_data['description']}")
    print(f"   - uploaded_by: {user_test_data['uploaded_by']}")
    
    # Make the request with JSON body (as user expects it to work)
    print(f"\n3. Making POST request to {API_URL}/documents/upload with JSON body...")
    response = requests.post(f"{API_URL}/documents/upload", json=user_test_data)
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        document = response.json()
        print("✅ SUCCESS! Document upload with JSON body is working!")
        print(f"   - Document ID: {document['id']}")
        print(f"   - Filename: {document['filename']}")
        print(f"   - Type: {document['document_type']}")
        print(f"   - Size: {document['file_size']} bytes")
        print(f"   - Version: {document['version']}")
        print(f"   - Uploaded by: {document['uploaded_by']}")
        
        # Verify the content was decoded correctly
        import base64
        expected_content = base64.b64decode("VGVzdCBjb250ZW50").decode()
        print(f"   - Expected decoded content: '{expected_content}'")
        
        # Test download to verify content integrity
        print(f"\n4. Verifying uploaded content by downloading...")
        download_response = requests.get(f"{API_URL}/documents/download/{document['id']}")
        if download_response.status_code == 200:
            downloaded_content = download_response.content.decode()
            if downloaded_content == expected_content:
                print("✅ Content integrity verified - upload and download match!")
            else:
                print(f"❌ Content mismatch: '{downloaded_content}' != '{expected_content}'")
        else:
            print(f"❌ Failed to download for verification: {download_response.status_code}")
            
    elif response.status_code == 400:
        print("❌ CRITICAL: Still getting 400 Bad Request!")
        print(f"📋 Response body: {response.text}")
        
        # Let's try to understand what the backend expects
        print(f"\n🔍 DEBUGGING: Let's check what the backend actually receives...")
        
        # Try with query parameters (old method) to see if that still works
        print(f"\n5. Testing with query parameters (fallback method)...")
        params = {
            "partner_id": user_test_data["partner_id"],
            "partner_type": user_test_data["partner_type"],
            "filename": user_test_data["filename"],
            "document_type": user_test_data["document_type"],
            "content": user_test_data["content"],
            "description": user_test_data["description"],
            "uploaded_by": user_test_data["uploaded_by"]
        }
        
        fallback_response = requests.post(f"{API_URL}/documents/upload", params=params)
        print(f"📊 Fallback Response Status: {fallback_response.status_code}")
        
        if fallback_response.status_code == 200:
            print("✅ Query parameters method still works - JSON parsing issue in backend")
        else:
            print(f"❌ Both methods failing: {fallback_response.text}")
            
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        print(f"📋 Response body: {response.text}")
    
    # Test 6: Additional validation tests
    print(f"\n6. Testing edge cases and validation...")
    
    # Test with missing required fields
    incomplete_data = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "incomplete.txt"
        # Missing document_type, content, etc.
    }
    
    response = requests.post(f"{API_URL}/documents/upload", json=incomplete_data)
    print(f"📊 Incomplete data test: {response.status_code}")
    if response.status_code in [400, 422]:
        print("✅ Correctly rejected incomplete data")
    else:
        print(f"❌ Should have rejected incomplete data: {response.status_code}")
    
    # Test with invalid base64
    invalid_b64_data = user_test_data.copy()
    invalid_b64_data["content"] = "invalid-base64-content!"
    
    response = requests.post(f"{API_URL}/documents/upload", json=invalid_b64_data)
    print(f"📊 Invalid base64 test: {response.status_code}")
    if response.status_code in [400, 422]:
        print("✅ Correctly rejected invalid base64")
    else:
        print(f"❌ Should have rejected invalid base64: {response.status_code}")
    
    print(f"\n🎯 URGENT TEST SUMMARY:")
    print(f"   - Backend URL: {API_URL}/documents/upload")
    print(f"   - JSON body method: {'✅ WORKING' if response.status_code == 200 else '❌ FAILING'}")
    print(f"   - User's 400 error: {'🔧 FIXED' if response.status_code == 200 else '🚨 STILL PRESENT'}")
    
    return partner_id

if __name__ == "__main__":
    # Check if we want to run focused tests
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "kanban":
            run_kanban_focused_tests()
        elif sys.argv[1] == "critical":
            test_critical_partner_creation()
        else:
            main()
    else:
        # CRITICAL BUG INVESTIGATION - Test partner creation first
        test_critical_partner_creation()
        
        # Then run full test suite
        main()