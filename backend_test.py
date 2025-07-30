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
    move_data = {
        "partner_id": dealflow_id,
        "partner_type": "dealflow",
        "source_column": "prequalification",
        "destination_column": "presentation"
    }
    
    response = requests.post(f"{API_URL}/kanban-move", json=move_data)
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
        transition_move_data = {
            "partner_id": transition_id,
            "partner_type": "sourcing",
            "source_column": "sourcing_a_traiter",
            "destination_column": "prequalification"
        }
        
        response = requests.post(f"{API_URL}/kanban-move", json=transition_move_data)
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
    invalid_move_data = {
        "partner_id": sourcing_id,
        "partner_type": "sourcing",
        "source_column": "sourcing_a_traiter",
        "destination_column": "invalid_column"
    }
    
    response = requests.post(f"{API_URL}/kanban-move", json=invalid_move_data)
    if response.status_code == 400:
        print("✅ Correctly rejected invalid destination column")
    else:
        print(f"❌ Should have rejected invalid column: {response.status_code}")
    
    # Test invalid partner ID
    invalid_partner_move = {
        "partner_id": "invalid-id",
        "partner_type": "sourcing",
        "source_column": "sourcing_a_traiter",
        "destination_column": "sourcing_klaxoon"
    }
    
    response = requests.post(f"{API_URL}/kanban-move", json=invalid_partner_move)
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
    print("🚀 Starting SURM Backend API Tests - Including Phase 1, Phase 2 & Phase 3 Features")
    print("=" * 60)
    
    try:
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
        
        # Test error handling
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 SURM Backend API Testing Complete - All Phases (1, 2, 3 & 4) Included!")
        print("Check the results above for any failures.")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()