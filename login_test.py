#!/usr/bin/env python3
"""
ZOIOS ERP Login Issue Investigation Script
Tests authentication system and provides working credentials for the user
"""

import requests
import json
import os
from datetime import datetime
import time
import random

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://zoios-erp-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_existing_accounts():
    """Test existing common test accounts as requested in review"""
    log("Testing existing common test accounts...")
    
    # Common test accounts to try
    test_accounts = [
        {"email": "admin@zoios.com", "password": "password123"},
        {"email": "admin@zoios.com", "password": "admin123"},
        {"email": "admin@2mholding.com", "password": "admin123"},
        {"email": "admin@2mholding.com", "password": "password123"},
        {"email": "testuser@example.com", "password": "password123"},
        {"email": "test@zoios.com", "password": "password123"}
    ]
    
    working_accounts = []
    session = requests.Session()
    
    for account in test_accounts:
        log(f"Testing account: {account['email']}")
        
        login_data = {
            "email": account["email"],
            "password": account["password"]
        }
        
        try:
            response = session.post(f"{API_BASE}/auth/login", json=login_data)
            log(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                auth_token = data.get('access_token')
                user_data = data.get('user')
                log(f"✅ WORKING ACCOUNT FOUND: {account['email']} / {account['password']}")
                log(f"User ID: {user_data.get('id')}")
                log(f"Role: {user_data.get('role')}")
                log(f"Onboarding completed: {user_data.get('onboarding_completed')}")
                working_accounts.append(account)
                
                # Test /auth/me to verify token works
                headers = {"Authorization": f"Bearer {auth_token}"}
                me_response = session.get(f"{API_BASE}/auth/me", headers=headers)
                if me_response.status_code == 200:
                    log("✅ Token validation working")
                else:
                    log("❌ Token validation failed")
                    
            else:
                log(f"❌ Login failed: {response.text}")
                
        except Exception as e:
            log(f"❌ Login error: {str(e)}")
    
    if working_accounts:
        log(f"\n🎉 FOUND {len(working_accounts)} WORKING ACCOUNT(S):")
        for account in working_accounts:
            log(f"   📧 {account['email']} / 🔑 {account['password']}")
        return working_accounts
    else:
        log("❌ NO EXISTING ACCOUNTS WORK - Need to create fresh account")
        return None

def test_create_fresh_account():
    """Create a fresh test account with simple credentials"""
    log("Creating fresh test account...")
    
    # Generate unique email to avoid conflicts
    timestamp = str(int(time.time()))
    fresh_email = f"testuser{timestamp}@example.com"
    fresh_password = "password123"
    
    signup_data = {
        "email": fresh_email,
        "password": fresh_password,
        "name": "Test User",
        "company": "Test Company"
    }
    
    session = requests.Session()
    
    try:
        response = session.post(f"{API_BASE}/auth/signup", json=signup_data)
        log(f"Signup response status: {response.status_code}")
        log(f"Signup response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get('access_token')
            user_data = data.get('user')
            
            log(f"✅ FRESH ACCOUNT CREATED SUCCESSFULLY!")
            log(f"📧 Email: {fresh_email}")
            log(f"🔑 Password: {fresh_password}")
            log(f"User ID: {user_data.get('id')}")
            log(f"Role: {user_data.get('role')}")
            
            # Test login with new account
            login_data = {
                "email": fresh_email,
                "password": fresh_password
            }
            
            login_response = session.post(f"{API_BASE}/auth/login", json=login_data)
            if login_response.status_code == 200:
                log("✅ Fresh account login verification successful")
                return {"email": fresh_email, "password": fresh_password}
            else:
                log("❌ Fresh account login verification failed")
                return None
                
        else:
            log(f"❌ Fresh account creation failed: {response.text}")
            return None
            
    except Exception as e:
        log(f"❌ Fresh account creation error: {str(e)}")
        return None

def test_authentication_endpoints(auth_token):
    """Test all authentication endpoints comprehensively"""
    log("Testing authentication endpoints...")
    
    if not auth_token:
        log("❌ No auth token available")
        return False
        
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    session = requests.Session()
    endpoints_tested = 0
    endpoints_passed = 0
    
    # Test /auth/me
    try:
        response = session.get(f"{API_BASE}/auth/me", headers=headers)
        endpoints_tested += 1
        if response.status_code == 200:
            endpoints_passed += 1
            log("✅ GET /auth/me - Working")
        else:
            log(f"❌ GET /auth/me - Failed: {response.status_code}")
    except Exception as e:
        log(f"❌ GET /auth/me - Error: {str(e)}")
        endpoints_tested += 1
    
    # Test protected endpoints to verify token validation
    protected_endpoints = [
        "/setup/countries",
        "/setup/currencies", 
        "/dashboard/stats"
    ]
    
    for endpoint in protected_endpoints:
        try:
            response = session.get(f"{API_BASE}{endpoint}", headers=headers)
            endpoints_tested += 1
            if response.status_code == 200:
                endpoints_passed += 1
                log(f"✅ GET {endpoint} - Token validation working")
            else:
                log(f"❌ GET {endpoint} - Token validation failed: {response.status_code}")
        except Exception as e:
            log(f"❌ GET {endpoint} - Error: {str(e)}")
            endpoints_tested += 1
    
    success_rate = (endpoints_passed / endpoints_tested * 100) if endpoints_tested > 0 else 0
    log(f"Authentication endpoints test: {endpoints_passed}/{endpoints_tested} passed ({success_rate:.1f}%)")
    
    return endpoints_passed == endpoints_tested

def test_database_connectivity():
    """Test database connectivity"""
    log("Testing database connectivity...")
    
    session = requests.Session()
    
    try:
        # Test a simple endpoint that requires database access
        response = session.get(f"{API_BASE}/setup/countries")
        log(f"Database test response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                log(f"✅ Database connectivity working - found {len(data)} countries")
                return True
            else:
                log("❌ Database returns empty data")
                return False
        else:
            log(f"❌ Database connectivity failed: {response.text}")
            return False
            
    except Exception as e:
        log(f"❌ Database connectivity error: {str(e)}")
        return False

def main():
    """Run focused tests to investigate and resolve login issues"""
    log("=" * 80)
    log("🔍 ZOIOS ERP LOGIN ISSUE INVESTIGATION")
    log("=" * 80)
    
    # Step 1: Test existing accounts
    log("\n📋 STEP 1: Testing existing common test accounts")
    log("-" * 50)
    working_accounts = test_existing_accounts()
    
    # Step 2: Create fresh account if needed
    working_credentials = None
    if not working_accounts:
        log("\n🆕 STEP 2: Creating fresh test account")
        log("-" * 50)
        working_credentials = test_create_fresh_account()
    
    # Step 3: Test database connectivity
    log("\n💾 STEP 3: Testing database connectivity")
    log("-" * 50)
    db_connectivity = test_database_connectivity()
    
    # Step 4: Test authentication endpoints if we have credentials
    if working_accounts or working_credentials:
        log("\n🔐 STEP 4: Testing authentication endpoints")
        log("-" * 50)
        
        # Get a token to test with
        test_token = None
        if working_accounts:
            # Login with first working account to get token
            session = requests.Session()
            login_data = {
                "email": working_accounts[0]["email"],
                "password": working_accounts[0]["password"]
            }
            response = session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                test_token = response.json().get('access_token')
        elif working_credentials:
            # Use token from fresh account creation
            session = requests.Session()
            login_data = {
                "email": working_credentials["email"],
                "password": working_credentials["password"]
            }
            response = session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                test_token = response.json().get('access_token')
        
        auth_endpoints_work = test_authentication_endpoints(test_token)
    else:
        auth_endpoints_work = False
    
    # Generate final report
    log("\n" + "=" * 80)
    log("🎯 LOGIN ISSUE INVESTIGATION RESULTS")
    log("=" * 80)
    
    if working_accounts:
        log("✅ EXISTING ACCOUNTS WORKING - User can login with existing credentials")
        log("\n🎉 WORKING CREDENTIALS FOR USER:")
        for account in working_accounts:
            log(f"   📧 {account['email']} / 🔑 {account['password']}")
    elif working_credentials:
        log(f"✅ FRESH ACCOUNT CREATED - User can login with: {working_credentials['email']} / {working_credentials['password']}")
        log("\n🎉 WORKING CREDENTIALS FOR USER:")
        log(f"   📧 {working_credentials['email']} / 🔑 {working_credentials['password']}")
    else:
        log("❌ CRITICAL: No working login credentials found")
    
    if auth_endpoints_work:
        log("✅ Authentication endpoints working properly")
    else:
        log("❌ Authentication endpoints have issues")
        
    if db_connectivity:
        log("✅ Database connectivity working")
    else:
        log("❌ Database connectivity issues detected")
    
    # Provide working credentials for user
    if working_accounts or working_credentials:
        log("\n🎉 SOLUTION FOR USER:")
        log("The user can now login with these working credentials:")
        if working_accounts:
            log(f"📧 Email: {working_accounts[0]['email']}")
            log(f"🔑 Password: {working_accounts[0]['password']}")
        elif working_credentials:
            log(f"📧 Email: {working_credentials['email']}")
            log(f"🔑 Password: {working_credentials['password']}")
        log("These credentials will provide access to the dashboard and all features.")
        return True
    else:
        log("\n❌ ISSUE REQUIRES FURTHER INVESTIGATION:")
        log("No working login credentials could be established.")
        log("Backend authentication system may need debugging.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)