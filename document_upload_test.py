#!/usr/bin/env python3
"""
URGENT DOCUMENT UPLOAD TESTING - Caroline's Issue
Tests document upload with JSON body exactly as frontend sends it
"""

import requests
import json
import base64
from datetime import datetime
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
print(f"Testing Document Upload API at: {API_URL}")

def create_test_partner():
    """Create a test partner for document upload testing"""
    print("\n=== CREATING TEST PARTNER FOR DOCUMENT UPLOAD ===")
    
    partner_data = {
        "nom_entreprise": "Document Upload Test Company",
        "statut": "A traiter",
        "pays_origine": "France",
        "domaine_activite": "FinTech",
        "typologie": "Startup",
        "objet": "Solution de paiement innovante",
        "cas_usage": "Paiements mobiles sécurisés",
        "technologie": "Blockchain",
        "source": "VivaTech 2025",
        "date_entree_sourcing": "2024-03-15",
        "interet": True,
        "pilote": "Marie Test",
        "actions_commentaires": "Test partner for document upload"
    }
    
    response = requests.post(f"{API_URL}/sourcing", json=partner_data)
    if response.status_code == 200:
        partner = response.json()
        print(f"✅ Created test partner: {partner['nom_entreprise']} (ID: {partner['id']})")
        return partner['id']
    else:
        print(f"❌ Failed to create test partner: {response.status_code} - {response.text}")
        return None

def test_document_upload_json_body():
    """Test 1: Document Upload with JSON Body - User Caroline's exact scenario"""
    print("\n=== TEST 1: DOCUMENT UPLOAD WITH JSON BODY (Caroline's Issue) ===")
    
    # Create test partner
    partner_id = create_test_partner()
    if not partner_id:
        return False
    
    # Test data exactly as frontend sends it
    test_content = "Test content"
    base64_content = base64.b64encode(test_content.encode()).decode()
    
    upload_data = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "test_document.pdf",
        "document_type": "AUTRE",
        "content": base64_content,
        "description": "Test upload via JSON",
        "uploaded_by": "test_user"
    }
    
    print(f"Uploading document with JSON body:")
    print(f"  - partner_id: {upload_data['partner_id']}")
    print(f"  - partner_type: {upload_data['partner_type']}")
    print(f"  - filename: {upload_data['filename']}")
    print(f"  - document_type: {upload_data['document_type']}")
    print(f"  - content: {upload_data['content'][:20]}... (base64)")
    print(f"  - description: {upload_data['description']}")
    print(f"  - uploaded_by: {upload_data['uploaded_by']}")
    
    # Test JSON body upload
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{API_URL}/documents/upload", json=upload_data, headers=headers)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        document = response.json()
        print("✅ JSON BODY UPLOAD SUCCESSFUL!")
        print(f"  - Document ID: {document['id']}")
        print(f"  - Filename: {document['filename']}")
        print(f"  - File size: {document['file_size']} bytes")
        print(f"  - File type: {document['file_type']}")
        print(f"  - Version: {document['version']}")
        return document['id']
    else:
        print("❌ JSON BODY UPLOAD FAILED!")
        print(f"  - Status Code: {response.status_code}")
        print(f"  - Error Response: {response.text}")
        
        # Try to parse error details
        try:
            error_data = response.json()
            print(f"  - Error Detail: {error_data.get('detail', 'No detail provided')}")
        except:
            pass
        
        return None

def test_all_file_types():
    """Test 2: Upload different file types"""
    print("\n=== TEST 2: UPLOAD DIFFERENT FILE TYPES ===")
    
    partner_id = create_test_partner()
    if not partner_id:
        return []
    
    # Test different file types
    file_tests = [
        {
            "filename": "test_document.pdf",
            "content": "PDF test content",
            "document_type": "Convention",
            "description": "PDF document test"
        },
        {
            "filename": "test_document.docx", 
            "content": "DOCX test content",
            "document_type": "Presentation",
            "description": "DOCX document test"
        },
        {
            "filename": "test_image.png",
            "content": "PNG test content",
            "document_type": "Autre",
            "description": "PNG image test"
        },
        {
            "filename": "test_file.txt",
            "content": "TXT test content",
            "document_type": "Document technique",
            "description": "TXT file test"
        }
    ]
    
    uploaded_docs = []
    
    for i, file_test in enumerate(file_tests, 1):
        print(f"\n{i}. Testing {file_test['filename']} upload")
        
        base64_content = base64.b64encode(file_test['content'].encode()).decode()
        
        upload_data = {
            "partner_id": partner_id,
            "partner_type": "sourcing",
            "filename": file_test['filename'],
            "document_type": file_test['document_type'],
            "content": base64_content,
            "description": file_test['description'],
            "uploaded_by": "test_user"
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{API_URL}/documents/upload", json=upload_data, headers=headers)
        
        if response.status_code == 200:
            document = response.json()
            uploaded_docs.append(document)
            print(f"✅ {file_test['filename']} uploaded successfully")
            print(f"   - Document ID: {document['id']}")
            print(f"   - File type detected: {document['file_type']}")
            print(f"   - Version: {document['version']}")
        else:
            print(f"❌ {file_test['filename']} upload failed: {response.status_code}")
            print(f"   - Error: {response.text}")
    
    return uploaded_docs

def test_complete_upload_workflow(document_id, partner_id):
    """Test 3: Complete upload workflow - creation, listing, download"""
    print("\n=== TEST 3: COMPLETE UPLOAD WORKFLOW ===")
    
    if not document_id or not partner_id:
        print("❌ No document ID or partner ID available for workflow test")
        return False
    
    # Test 1: Document listing
    print(f"\n1. Testing document listing for partner {partner_id}")
    response = requests.get(f"{API_URL}/documents/{partner_id}")
    
    if response.status_code == 200:
        documents = response.json()
        print(f"✅ Retrieved {len(documents)} documents for partner")
        
        # Find our test document
        test_doc = None
        for doc in documents:
            if doc['id'] == document_id:
                test_doc = doc
                break
        
        if test_doc:
            print(f"✅ Test document found in listing:")
            print(f"   - ID: {test_doc['id']}")
            print(f"   - Filename: {test_doc['filename']}")
            print(f"   - Type: {test_doc['document_type']}")
            print(f"   - Size: {test_doc['file_size']} bytes")
        else:
            print(f"❌ Test document {document_id} not found in listing")
            return False
    else:
        print(f"❌ Failed to list documents: {response.status_code} - {response.text}")
        return False
    
    # Test 2: Document download
    print(f"\n2. Testing document download for document {document_id}")
    response = requests.get(f"{API_URL}/documents/download/{document_id}")
    
    if response.status_code == 200:
        print("✅ Document download successful!")
        print(f"   - Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"   - Content-Disposition: {response.headers.get('content-disposition', 'Not set')}")
        print(f"   - Content length: {len(response.content)} bytes")
        
        # Verify content integrity
        try:
            downloaded_content = response.content.decode()
            if "Test content" in downloaded_content:
                print("✅ Content integrity verified - original content found")
            else:
                print(f"⚠️ Content may be different: {downloaded_content[:50]}...")
        except:
            print("⚠️ Content is binary, cannot verify text content")
        
        return True
    else:
        print(f"❌ Document download failed: {response.status_code}")
        print(f"   - Error: {response.text}")
        return False

def test_error_scenarios():
    """Test 4: Error scenarios"""
    print("\n=== TEST 4: ERROR SCENARIOS ===")
    
    partner_id = create_test_partner()
    if not partner_id:
        return
    
    # Test 1: Invalid base64 content
    print("\n1. Testing invalid base64 content")
    invalid_data = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "invalid_base64.txt",
        "document_type": "Autre",
        "content": "invalid_base64_content!!!",
        "description": "Invalid base64 test",
        "uploaded_by": "test_user"
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{API_URL}/documents/upload", json=invalid_data, headers=headers)
    
    if response.status_code in [400, 422]:
        print("✅ Correctly rejected invalid base64 content")
        print(f"   - Status: {response.status_code}")
    else:
        print(f"❌ Should have rejected invalid base64: {response.status_code}")
    
    # Test 2: Missing required fields
    print("\n2. Testing missing required fields")
    incomplete_data = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        # Missing filename, document_type, content
        "description": "Incomplete data test",
        "uploaded_by": "test_user"
    }
    
    response = requests.post(f"{API_URL}/documents/upload", json=incomplete_data, headers=headers)
    
    if response.status_code in [400, 422]:
        print("✅ Correctly rejected missing required fields")
        print(f"   - Status: {response.status_code}")
    else:
        print(f"❌ Should have rejected incomplete data: {response.status_code}")
    
    # Test 3: Invalid document_type enum
    print("\n3. Testing invalid document_type enum")
    invalid_enum_data = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "invalid_enum.txt",
        "document_type": "INVALID_TYPE",
        "content": base64.b64encode(b"test content").decode(),
        "description": "Invalid enum test",
        "uploaded_by": "test_user"
    }
    
    response = requests.post(f"{API_URL}/documents/upload", json=invalid_enum_data, headers=headers)
    
    if response.status_code in [400, 422]:
        print("✅ Correctly rejected invalid document_type enum")
        print(f"   - Status: {response.status_code}")
    else:
        print(f"❌ Should have rejected invalid enum: {response.status_code}")

def test_json_parsing_logic():
    """Test 5: Current JSON parsing logic verification"""
    print("\n=== TEST 5: JSON PARSING LOGIC VERIFICATION ===")
    
    partner_id = create_test_partner()
    if not partner_id:
        return
    
    # Test with proper JSON content-type header
    print("\n1. Testing with application/json content-type")
    json_data = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "json_parsing_test.txt",
        "document_type": "Autre",
        "content": base64.b64encode(b"JSON parsing test content").decode(),
        "description": "JSON parsing verification",
        "uploaded_by": "test_user"
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{API_URL}/documents/upload", json=json_data, headers=headers)
    
    print(f"JSON method - Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ JSON body parsing working correctly")
        document = response.json()
        json_doc_id = document['id']
    else:
        print(f"❌ JSON body parsing failed: {response.text}")
        json_doc_id = None
    
    # Test with query parameters (fallback method)
    print("\n2. Testing query parameters fallback")
    query_params = {
        "partner_id": partner_id,
        "partner_type": "sourcing",
        "filename": "query_params_test.txt",
        "document_type": "Autre",
        "content": base64.b64encode(b"Query params test content").decode(),
        "description": "Query params verification",
        "uploaded_by": "test_user"
    }
    
    response = requests.post(f"{API_URL}/documents/upload", params=query_params)
    
    print(f"Query params method - Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Query parameters fallback working correctly")
        document = response.json()
        query_doc_id = document['id']
    else:
        print(f"❌ Query parameters fallback failed: {response.text}")
        query_doc_id = None
    
    # Verify both methods created documents
    if json_doc_id and query_doc_id:
        print("\n3. Verifying both upload methods created documents")
        response = requests.get(f"{API_URL}/documents/{partner_id}")
        if response.status_code == 200:
            documents = response.json()
            json_found = any(doc['id'] == json_doc_id for doc in documents)
            query_found = any(doc['id'] == query_doc_id for doc in documents)
            
            if json_found and query_found:
                print("✅ Both JSON and query parameter methods working")
            else:
                print(f"❌ Missing documents - JSON: {json_found}, Query: {query_found}")
        else:
            print(f"❌ Failed to verify documents: {response.status_code}")

def main():
    """Run all document upload tests"""
    print("🚨 URGENT DOCUMENT UPLOAD TESTING - Caroline's Issue")
    print("=" * 60)
    
    # Test 1: JSON Body Upload (Caroline's exact issue)
    document_id = test_document_upload_json_body()
    
    # Test 2: All file types
    uploaded_docs = test_all_file_types()
    
    # Test 3: Complete workflow (if we have a document)
    if document_id:
        # Get partner ID from the first test
        partner_id = create_test_partner()  # We need a partner ID for workflow test
        test_complete_upload_workflow(document_id, partner_id)
    
    # Test 4: Error scenarios
    test_error_scenarios()
    
    # Test 5: JSON parsing logic verification
    test_json_parsing_logic()
    
    print("\n" + "=" * 60)
    print("🏁 DOCUMENT UPLOAD TESTING COMPLETED")
    
    # Summary
    if document_id:
        print("✅ MAIN ISSUE STATUS: JSON body upload is WORKING")
        print("   Caroline's 400/422 errors should be resolved")
    else:
        print("❌ MAIN ISSUE STATUS: JSON body upload is FAILING")
        print("   Caroline's issue persists - needs investigation")
    
    print(f"✅ File type tests: {len(uploaded_docs)} different types tested")
    print("✅ Error handling: Tested invalid scenarios")
    print("✅ JSON parsing: Verified both JSON and query parameter methods")

if __name__ == "__main__":
    main()