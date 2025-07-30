#!/usr/bin/env python3
"""
Phase 4 Kanban Backend Testing Only
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
    "date_prochaine_action": "2024-04-15"
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
    "date_prochaine_action": "2024-04-10"
}

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
    
    # Test 5: Test invalid moves and error handling
    print(f"\n5. Testing invalid moves and error handling")
    
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

def main():
    """Run Phase 4 tests only"""
    print("🚀 Starting SURM Backend API Phase 4 Tests - Kanban Pipeline")
    print("=" * 60)
    
    try:
        # Test Phase 4 - Kanban Data Endpoint
        test_phase4_kanban_data()
        
        # Test Phase 4 - Kanban Move Endpoint
        test_phase4_kanban_move()
        
        # Test Phase 4 - Data Structure Validation
        test_phase4_data_structure_validation()
        
        print("\n" + "=" * 60)
        print("🎉 SURM Backend API Phase 4 Testing Complete!")
        print("Check the results above for any failures.")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()