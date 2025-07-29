#!/usr/bin/env python3
"""
SURM Backend API Testing Suite - Phase 3 Only
Tests Phase 3 features: User Management, Private Comments, Personal Dashboard, Enhanced Authorization
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
print(f"Testing SURM Backend API Phase 3 at: {API_URL}")

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

def main():
    """Run Phase 3 tests only"""
    print("🚀 Starting SURM Backend API Phase 3 Tests")
    print("=" * 60)
    
    try:
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
        
        print("\n" + "=" * 60)
        print("🎉 SURM Backend API Phase 3 Testing Complete!")
        print("Check the results above for any failures.")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()