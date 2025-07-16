#!/usr/bin/env python3
"""
Additional SURM Backend API Tests - Edge Cases and Data Validation
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
API_URL = f"{BASE_URL}/api"

def test_enum_validations():
    """Test all enum validations work correctly"""
    print("\n=== TESTING ENUM VALIDATIONS ===")
    
    # Test valid sourcing statuses
    valid_sourcing_statuses = ["A traiter", "Clos", "Dealflow", "Klaxoon"]
    for status in valid_sourcing_statuses:
        test_data = {
            "nom_entreprise": f"Test Company {status}",
            "statut": status,
            "pays_origine": "France",
            "domaine_activite": "Test Domain",
            "typologie": "Test Type",
            "objet": "Test Object",
            "cas_usage": "Test Usage",
            "technologie": "Test Tech",
            "source": "Test Source",
            "date_entree_sourcing": "2024-01-01",
            "interet": True,
            "pilote": "Test Pilot"
        }
        response = requests.post(f"{API_URL}/sourcing", json=test_data)
        if response.status_code == 200:
            print(f"✅ Valid sourcing status '{status}' accepted")
        else:
            print(f"❌ Valid sourcing status '{status}' rejected: {response.status_code}")
    
    # Test valid dealflow statuses
    valid_dealflow_statuses = ["Clos", "En cours avec les métiers", "En cours avec l'équipe inno"]
    for status in valid_dealflow_statuses:
        test_data = {
            "nom": f"Test Dealflow {status}",
            "statut": status,
            "domaine": "Test Domain",
            "typologie": "Test Type",
            "objet": "Test Object",
            "source": "Test Source",
            "pilote": "Test Pilot",
            "metiers_concernes": "Test Metiers",
            "date_reception_fichier": "2024-01-01"
        }
        response = requests.post(f"{API_URL}/dealflow", json=test_data)
        if response.status_code == 200:
            print(f"✅ Valid dealflow status '{status}' accepted")
        else:
            print(f"❌ Valid dealflow status '{status}' rejected: {response.status_code}")

def test_date_handling():
    """Test various date formats and edge cases"""
    print("\n=== TESTING DATE HANDLING ===")
    
    # Test different date formats
    date_formats = [
        "2024-01-01",
        "2024-12-31",
        "2023-02-28",
        "2024-02-29"  # Leap year
    ]
    
    for date_str in date_formats:
        test_data = {
            "nom_entreprise": f"Date Test {date_str}",
            "statut": "A traiter",
            "pays_origine": "France",
            "domaine_activite": "Test Domain",
            "typologie": "Test Type",
            "objet": "Test Object",
            "cas_usage": "Test Usage",
            "technologie": "Test Tech",
            "source": "Test Source",
            "date_entree_sourcing": date_str,
            "interet": True,
            "pilote": "Test Pilot"
        }
        response = requests.post(f"{API_URL}/sourcing", json=test_data)
        if response.status_code == 200:
            print(f"✅ Date format '{date_str}' accepted")
        else:
            print(f"❌ Date format '{date_str}' rejected: {response.status_code}")

def test_optional_fields():
    """Test that optional fields work correctly"""
    print("\n=== TESTING OPTIONAL FIELDS ===")
    
    # Test sourcing with minimal required fields
    minimal_sourcing = {
        "nom_entreprise": "Minimal Test Company",
        "statut": "A traiter",
        "pays_origine": "France",
        "domaine_activite": "Test Domain",
        "typologie": "Test Type",
        "objet": "Test Object",
        "cas_usage": "Test Usage",
        "technologie": "Test Tech",
        "source": "Test Source",
        "date_entree_sourcing": "2024-01-01",
        "interet": True,
        "pilote": "Test Pilot"
    }
    
    response = requests.post(f"{API_URL}/sourcing", json=minimal_sourcing)
    if response.status_code == 200:
        print("✅ Sourcing with minimal fields accepted")
        sourcing_id = response.json()['id']
        
        # Test updating with optional fields
        update_data = {
            "date_presentation_metiers": "2024-01-15",
            "actions_commentaires": "Added optional fields"
        }
        response = requests.put(f"{API_URL}/sourcing/{sourcing_id}", json=update_data)
        if response.status_code == 200:
            print("✅ Optional fields update successful")
        else:
            print(f"❌ Optional fields update failed: {response.status_code}")
    else:
        print(f"❌ Minimal sourcing rejected: {response.status_code}")

def test_statistics_accuracy():
    """Test that statistics calculations are accurate"""
    print("\n=== TESTING STATISTICS ACCURACY ===")
    
    # Get current statistics
    response = requests.get(f"{API_URL}/statistics")
    if response.status_code == 200:
        stats = response.json()
        
        # Get actual data to verify
        sourcing_response = requests.get(f"{API_URL}/sourcing")
        dealflow_response = requests.get(f"{API_URL}/dealflow")
        
        if sourcing_response.status_code == 200 and dealflow_response.status_code == 200:
            sourcing_partners = sourcing_response.json()
            dealflow_partners = dealflow_response.json()
            
            # Verify totals
            if stats['total_sourcing'] == len(sourcing_partners):
                print(f"✅ Sourcing total accurate: {stats['total_sourcing']}")
            else:
                print(f"❌ Sourcing total mismatch: stats={stats['total_sourcing']}, actual={len(sourcing_partners)}")
            
            if stats['total_dealflow'] == len(dealflow_partners):
                print(f"✅ Dealflow total accurate: {stats['total_dealflow']}")
            else:
                print(f"❌ Dealflow total mismatch: stats={stats['total_dealflow']}, actual={len(dealflow_partners)}")
            
            # Verify domain distribution
            actual_domains = {}
            for partner in sourcing_partners:
                domain = partner.get('domaine_activite', 'Unknown')
                actual_domains[domain] = actual_domains.get(domain, 0) + 1
            for partner in dealflow_partners:
                domain = partner.get('domaine', 'Unknown')
                actual_domains[domain] = actual_domains.get(domain, 0) + 1
            
            stats_domains_total = sum(stats['domain_distribution'].values())
            actual_domains_total = sum(actual_domains.values())
            
            if stats_domains_total == actual_domains_total:
                print(f"✅ Domain distribution totals match: {stats_domains_total}")
            else:
                print(f"❌ Domain distribution mismatch: stats={stats_domains_total}, actual={actual_domains_total}")
        
    else:
        print(f"❌ Failed to get statistics: {response.status_code}")

def test_transition_data_inheritance():
    """Test that transition properly inherits data"""
    print("\n=== TESTING TRANSITION DATA INHERITANCE ===")
    
    # Create a sourcing partner with specific data
    sourcing_data = {
        "nom_entreprise": "Transition Test Company",
        "statut": "A traiter",
        "pays_origine": "Espagne",
        "domaine_activite": "Blockchain",
        "typologie": "Startup",
        "objet": "Smart Contracts Platform",
        "cas_usage": "Automated legal contracts",
        "technologie": "Ethereum",
        "source": "Tech Conference",
        "date_entree_sourcing": "2024-01-01",
        "interet": True,
        "pilote": "Carlos Rodriguez",
        "actions_commentaires": "Very promising technology"
    }
    
    response = requests.post(f"{API_URL}/sourcing", json=sourcing_data)
    if response.status_code == 200:
        sourcing_partner = response.json()
        sourcing_id = sourcing_partner['id']
        print(f"✅ Created sourcing partner for transition test: {sourcing_id}")
        
        # Transition to dealflow
        transition_data = {
            "statut": "En cours avec les métiers",
            "metiers_concernes": "Legal, IT",
            "date_reception_fichier": "2024-01-15"
        }
        
        response = requests.post(f"{API_URL}/transition/{sourcing_id}", json=transition_data)
        if response.status_code == 200:
            dealflow_partner = response.json()
            print("✅ Transition successful")
            
            # Verify data inheritance
            inheritance_checks = [
                ("nom", sourcing_data["nom_entreprise"], "Company name"),
                ("domaine", sourcing_data["domaine_activite"], "Domain"),
                ("typologie", sourcing_data["typologie"], "Typologie"),
                ("objet", sourcing_data["objet"], "Object"),
                ("source", sourcing_data["source"], "Source"),
                ("pilote", sourcing_data["pilote"], "Pilot"),
                ("pays_origine", sourcing_data["pays_origine"], "Country"),
                ("cas_usage", sourcing_data["cas_usage"], "Use case"),
                ("technologie", sourcing_data["technologie"], "Technology"),
                ("interet", sourcing_data["interet"], "Interest"),
                ("sourcing_id", sourcing_id, "Sourcing ID reference")
            ]
            
            for field, expected, description in inheritance_checks:
                if dealflow_partner.get(field) == expected:
                    print(f"✅ {description} correctly inherited")
                else:
                    print(f"❌ {description} not inherited correctly: expected={expected}, got={dealflow_partner.get(field)}")
        else:
            print(f"❌ Transition failed: {response.status_code} - {response.text}")
    else:
        print(f"❌ Failed to create sourcing partner: {response.status_code}")

def main():
    """Run additional tests"""
    print("🔍 Running Additional SURM Backend API Tests")
    print("=" * 50)
    
    try:
        test_enum_validations()
        test_date_handling()
        test_optional_fields()
        test_statistics_accuracy()
        test_transition_data_inheritance()
        
        print("\n" + "=" * 50)
        print("🎉 Additional Testing Complete!")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during additional testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()