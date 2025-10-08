#!/usr/bin/env python3
"""
Caroline's Critical Functionality Tests
Tests the two critical issues Caroline reported:
1. Partner Creation Functionality
2. New Company Enrichment Endpoint
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
print(f"Testing Caroline's Critical Issues at: {API_URL}")

def test_caroline_partner_creation_issue():
    """Test Caroline's critical partner creation issue"""
    print("\n=== TESTING CAROLINE'S PARTNER CREATION ISSUE ===")
    print("User Caroline reports: Clicking 'Créer' button does nothing in partner creation forms")
    
    # Test 1: POST /api/sourcing with Caroline's exact scenario
    print("\n1. Testing POST /api/sourcing with realistic Caroline data")
    caroline_sourcing_data = {
        "nom_entreprise": "Caroline Test Company",
        "statut": "A traiter",
        "pays_origine": "France",
        "domaine_activite": "FinTech",
        "typologie": "Startup",
        "objet": "Solution de paiement innovante",
        "cas_usage": "Paiements mobiles sécurisés",
        "technologie": "Blockchain",
        "source": "VivaTech 2025",
        "date_entree_sourcing": "2024-12-19",
        "interet": True,
        "date_presentation_metiers": "2024-12-25",
        "pilote": "Caroline Dubois",
        "actions_commentaires": "Test de création par Caroline",
        "date_prochaine_action": "2025-01-15"
    }
    
    response = requests.post(f"{API_URL}/sourcing", json=caroline_sourcing_data)
    if response.status_code == 200:
        partner = response.json()
        sourcing_id = partner['id']
        print(f"✅ SOURCING CREATION SUCCESS: Created partner '{partner['nom_entreprise']}'")
        print(f"   - ID: {sourcing_id}")
        print(f"   - Status: {partner['statut']}")
        print(f"   - Domain: {partner['domaine_activite']}")
        print(f"   - Pilot: {partner['pilote']}")
        
        # Verify partner appears in list
        list_response = requests.get(f"{API_URL}/sourcing")
        if list_response.status_code == 200:
            partners = list_response.json()
            caroline_partner = next((p for p in partners if p['id'] == sourcing_id), None)
            if caroline_partner:
                print(f"✅ VERIFICATION SUCCESS: Partner appears in sourcing list")
            else:
                print(f"❌ VERIFICATION FAILED: Partner not found in sourcing list")
        
        sourcing_success = True
    else:
        print(f"❌ SOURCING CREATION FAILED: {response.status_code}")
        print(f"   Error: {response.text}")
        sourcing_success = False
        sourcing_id = None
    
    # Test 2: POST /api/dealflow with Caroline's exact scenario
    print("\n2. Testing POST /api/dealflow with realistic Caroline data")
    caroline_dealflow_data = {
        "nom": "Caroline Dealflow Test",
        "statut": "En cours avec les métiers",
        "domaine": "FinTech",
        "typologie": "Startup",
        "objet": "Plateforme fintech avancée",
        "source": "Réseau Caroline",
        "pilote": "Caroline Dubois",
        "metiers_concernes": "DSI, Finance, Innovation",
        "date_reception_fichier": "2024-12-19",
        "date_pre_qualification": "2024-12-22",
        "date_presentation_meetup_referents": "2024-12-28",
        "actions_commentaires": "Test de création dealflow par Caroline",
        "date_prochaine_action": "2025-01-20"
    }
    
    response = requests.post(f"{API_URL}/dealflow", json=caroline_dealflow_data)
    if response.status_code == 200:
        partner = response.json()
        dealflow_id = partner['id']
        print(f"✅ DEALFLOW CREATION SUCCESS: Created partner '{partner['nom']}'")
        print(f"   - ID: {dealflow_id}")
        print(f"   - Status: {partner['statut']}")
        print(f"   - Domain: {partner['domaine']}")
        print(f"   - Pilot: {partner['pilote']}")
        
        # Verify partner appears in list
        list_response = requests.get(f"{API_URL}/dealflow")
        if list_response.status_code == 200:
            partners = list_response.json()
            caroline_partner = next((p for p in partners if p['id'] == dealflow_id), None)
            if caroline_partner:
                print(f"✅ VERIFICATION SUCCESS: Partner appears in dealflow list")
            else:
                print(f"❌ VERIFICATION FAILED: Partner not found in dealflow list")
        
        dealflow_success = True
    else:
        print(f"❌ DEALFLOW CREATION FAILED: {response.status_code}")
        print(f"   Error: {response.text}")
        dealflow_success = False
        dealflow_id = None
    
    return sourcing_success, dealflow_success, sourcing_id, dealflow_id

def test_caroline_company_enrichment():
    """Test Caroline's new company enrichment endpoint"""
    print("\n=== TESTING CAROLINE'S NEW COMPANY ENRICHMENT ENDPOINT ===")
    print("Testing POST /api/enrich-company endpoint with various company names")
    
    # Test companies Caroline mentioned
    test_companies = [
        {"query": "Google", "expected_success": True},
        {"query": "Microsoft", "expected_success": True},
        {"query": "Test Company", "expected_success": True},
        {"query": "Société Générale", "expected_success": True},  # French company for SIRENE API
        {"query": "BNP Paribas", "expected_success": True},       # Another French company
        {"query": "NonExistentCompany12345", "expected_success": False}  # Should fail gracefully
    ]
    
    successful_tests = 0
    total_tests = len(test_companies)
    
    for i, test_case in enumerate(test_companies, 1):
        company_name = test_case["query"]
        expected_success = test_case["expected_success"]
        
        print(f"\n{i}. Testing company: '{company_name}'")
        
        # Test with just company name
        enrichment_request = {
            "query": company_name
        }
        
        response = requests.post(f"{API_URL}/enrich-company", json=enrichment_request)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            required_fields = ["success", "company_data", "error_message", "api_source"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print(f"✅ Response structure correct for '{company_name}'")
                
                if data["success"]:
                    print(f"✅ Enrichment SUCCESS for '{company_name}'")
                    print(f"   - API Source: {data.get('api_source', 'unknown')}")
                    
                    company_data = data.get("company_data", {})
                    if company_data:
                        print(f"   - Company Name: {company_data.get('name', 'N/A')}")
                        print(f"   - Industry: {company_data.get('industry', 'N/A')}")
                        print(f"   - Country: {company_data.get('country', 'N/A')}")
                        print(f"   - Domain: {company_data.get('domain', 'N/A')}")
                        print(f"   - Founded: {company_data.get('year_founded', 'N/A')}")
                        print(f"   - Employees: {company_data.get('employees_count', 'N/A')}")
                        
                        # Check if we got meaningful data
                        meaningful_fields = ['name', 'industry', 'country', 'domain']
                        filled_fields = [field for field in meaningful_fields if company_data.get(field)]
                        
                        if len(filled_fields) >= 2:
                            print(f"✅ Meaningful data retrieved ({len(filled_fields)}/4 key fields)")
                            successful_tests += 1
                        else:
                            print(f"⚠️ Limited data retrieved ({len(filled_fields)}/4 key fields)")
                            if expected_success:
                                successful_tests += 0.5  # Partial success
                    else:
                        print(f"⚠️ No company data returned for '{company_name}'")
                        
                else:
                    print(f"⚠️ Enrichment failed for '{company_name}': {data.get('error_message', 'Unknown error')}")
                    if not expected_success:
                        print(f"✅ Expected failure handled gracefully")
                        successful_tests += 1
                        
            else:
                print(f"❌ Missing response fields for '{company_name}': {missing_fields}")
                
        else:
            print(f"❌ HTTP Error for '{company_name}': {response.status_code}")
            print(f"   Error: {response.text}")
    
    # Test with domain parameter
    print(f"\n{total_tests + 1}. Testing enrichment with domain parameter")
    enrichment_with_domain = {
        "query": "Google",
        "domain": "google.com"
    }
    
    response = requests.post(f"{API_URL}/enrich-company", json=enrichment_with_domain)
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print(f"✅ Enrichment with domain parameter successful")
            print(f"   - API Source: {data.get('api_source', 'unknown')}")
            successful_tests += 1
        else:
            print(f"⚠️ Enrichment with domain failed: {data.get('error_message')}")
    else:
        print(f"❌ HTTP Error with domain parameter: {response.status_code}")
    
    # Summary
    total_tests += 1  # Include domain test
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"\n=== COMPANY ENRICHMENT TEST SUMMARY ===")
    print(f"✅ Successful tests: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 70:
        print(f"✅ COMPANY ENRICHMENT ENDPOINT WORKING - Ready for Caroline's use")
        return True
    else:
        print(f"❌ COMPANY ENRICHMENT NEEDS ATTENTION - Success rate below 70%")
        return False

def main():
    """Run Caroline's critical functionality tests"""
    print("🚀 TESTING CAROLINE'S CRITICAL FUNCTIONALITIES")
    print("=" * 60)
    print("PRIORITY 1: Partner Creation Functionality")
    print("PRIORITY 2: New Company Enrichment Endpoint")
    print("=" * 60)
    
    try:
        # Test 1: Caroline's Partner Creation Issue (CRITICAL)
        print("\n" + "🔥" * 60)
        print("CRITICAL TEST 1: PARTNER CREATION FUNCTIONALITY")
        print("🔥" * 60)
        
        sourcing_success, dealflow_success, sourcing_id, dealflow_id = test_caroline_partner_creation_issue()
        
        # Test 2: Caroline's New Company Enrichment Feature
        print("\n" + "🆕" * 60)
        print("NEW FEATURE TEST 2: COMPANY ENRICHMENT ENDPOINT")
        print("🆕" * 60)
        
        enrichment_working = test_caroline_company_enrichment()
        
        # Summary for Caroline
        print("\n" + "=" * 60)
        print("🎯 CAROLINE'S FUNCTIONALITY TEST RESULTS")
        print("=" * 60)
        
        if sourcing_success or dealflow_success:
            print("✅ PARTNER CREATION: WORKING - Backend API handles partner creation correctly")
            print("   → Issue is likely in FRONTEND form submission or validation")
            if sourcing_success:
                print("   → Sourcing partner creation: ✅ WORKING")
            if dealflow_success:
                print("   → Dealflow partner creation: ✅ WORKING")
        else:
            print("❌ PARTNER CREATION: FAILED - Backend API has issues")
        
        if enrichment_working:
            print("✅ COMPANY ENRICHMENT: WORKING - New endpoint ready for use")
            print("   → Caroline can use enrichment feature for company data")
        else:
            print("⚠️ COMPANY ENRICHMENT: PARTIAL - Some functionality working")
        
        print("\n🚀 CAROLINE'S CRITICAL TESTING COMPLETED!")
        
        # Additional quick tests to verify overall system health
        print("\n" + "=" * 60)
        print("📋 QUICK SYSTEM HEALTH CHECK")
        print("=" * 60)
        
        # Quick sourcing list test
        response = requests.get(f"{API_URL}/sourcing")
        if response.status_code == 200:
            partners = response.json()
            print(f"✅ Sourcing list: {len(partners)} partners available")
        else:
            print(f"❌ Sourcing list failed: {response.status_code}")
        
        # Quick dealflow list test
        response = requests.get(f"{API_URL}/dealflow")
        if response.status_code == 200:
            partners = response.json()
            print(f"✅ Dealflow list: {len(partners)} partners available")
        else:
            print(f"❌ Dealflow list failed: {response.status_code}")
        
        # Quick statistics test
        response = requests.get(f"{API_URL}/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistics: {stats.get('total_sourcing', 0)} sourcing, {stats.get('total_dealflow', 0)} dealflow")
        else:
            print(f"❌ Statistics failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during Caroline's testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()