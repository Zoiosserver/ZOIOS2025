#!/usr/bin/env python3
"""
Quick test for ERP endpoints to debug the issues
"""

import requests
import json
import os
import time

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://zoios-erp-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_erp_endpoints():
    # Create a test user and company first
    timestamp = str(int(time.time()))
    test_email = f"erptest{timestamp}@example.com"
    test_password = "testpass123"
    
    session = requests.Session()
    
    # Sign up
    signup_data = {
        "email": test_email,
        "password": test_password,
        "name": "ERP Test User",
        "company": "ERP Test Company"
    }
    
    response = session.post(f"{API_BASE}/auth/signup", json=signup_data)
    print(f"Signup status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Signup failed: {response.text}")
        return
    
    token = response.json().get('access_token')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Setup company
    setup_data = {
        "company_name": "ERP Test Company",
        "country_code": "US",
        "base_currency": "USD",
        "additional_currencies": ["EUR"],
        "business_type": "Corporation",
        "industry": "Technology",
        "address": "123 Test Street",
        "city": "Test City",
        "state": "CA",
        "postal_code": "12345",
        "phone": "+1-555-123-4567",
        "email": test_email,
        "website": "https://testcompany.com",
        "tax_number": "123456789",
        "registration_number": "REG123456"
    }
    
    response = session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
    print(f"Company setup status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Company setup failed: {response.text}")
        return
    
    company_data = response.json()
    company_id = company_data.get('id')
    print(f"Company created with ID: {company_id}")
    
    # Now test the ERP endpoints
    print("\n=== Testing ERP Endpoints ===")
    
    # Test 1: GET /companies/management
    response = session.get(f"{API_BASE}/companies/management", headers=headers)
    print(f"GET companies/management status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
    
    if response.status_code == 200:
        companies = response.json()
        print(f"Found {len(companies)} companies")
        
        if companies:
            # Test 2: GET company details
            response = session.get(f"{API_BASE}/companies/management/{company_id}", headers=headers)
            print(f"GET company details status: {response.status_code}")
            
            # Test 3: Enhanced accounts
            response = session.get(f"{API_BASE}/companies/{company_id}/accounts/enhanced", headers=headers)
            print(f"GET enhanced accounts status: {response.status_code}")
            print(f"Enhanced accounts response: {response.text[:200]}...")
            
            # Test 4: Export
            export_data = {"format": "pdf"}
            response = session.post(f"{API_BASE}/companies/{company_id}/accounts/export", json=export_data, headers=headers)
            print(f"POST export status: {response.status_code}")
            print(f"Export response: {response.text[:200]}...")
    
    # Test authentication without token
    print("\n=== Testing Authentication ===")
    response = session.get(f"{API_BASE}/companies/management")
    print(f"No auth companies/management status: {response.status_code}")

if __name__ == "__main__":
    test_erp_endpoints()