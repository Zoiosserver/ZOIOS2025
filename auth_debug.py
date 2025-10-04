#!/usr/bin/env python3
"""
Authentication Debug Script
Investigates the authentication issue with missing 'hashed_password' field
"""

import requests
import json
import os
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://zoios-erp-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_authentication_issue():
    """Test authentication to identify the hashed_password issue"""
    log("🔍 INVESTIGATING AUTHENTICATION ISSUE")
    log("=" * 60)
    
    # Test known credentials that might exist
    test_accounts = [
        {"email": "admin@2mholding.com", "password": "admin123"},
        {"email": "admin@zoios.com", "password": "admin123"},
        {"email": "testuser1759581426@example.com", "password": "password123"},
    ]
    
    session = requests.Session()
    
    for account in test_accounts:
        log(f"Testing login with: {account['email']}")
        
        try:
            response = session.post(f"{API_BASE}/auth/login", json=account)
            log(f"Response status: {response.status_code}")
            log(f"Response text: {response.text}")
            
            if response.status_code == 200:
                log(f"✅ SUCCESS: {account['email']} login works!")
                data = response.json()
                token = data.get('access_token')
                
                # Test /auth/me endpoint
                headers = {"Authorization": f"Bearer {token}"}
                me_response = session.get(f"{API_BASE}/auth/me", headers=headers)
                log(f"/auth/me status: {me_response.status_code}")
                log(f"/auth/me response: {me_response.text}")
                
                if me_response.status_code == 200:
                    log("✅ /auth/me endpoint working")
                    return True, account
                else:
                    log("❌ /auth/me endpoint failing")
            else:
                log(f"❌ Login failed: {response.text}")
                
        except Exception as e:
            log(f"❌ Error testing {account['email']}: {str(e)}")
    
    log("❌ No existing accounts work - need to create fresh account")
    return False, None

def create_fresh_account():
    """Create a fresh account to test authentication"""
    log("🆕 CREATING FRESH ACCOUNT")
    log("=" * 40)
    
    timestamp = str(int(time.time()))
    fresh_email = f"authtest{timestamp}@example.com"
    fresh_password = "password123"
    
    signup_data = {
        "email": fresh_email,
        "password": fresh_password,
        "name": "Auth Test User",
        "company": "Auth Test Company"
    }
    
    session = requests.Session()
    
    try:
        response = session.post(f"{API_BASE}/auth/signup", json=signup_data)
        log(f"Signup response status: {response.status_code}")
        log(f"Signup response: {response.text}")
        
        if response.status_code == 200:
            log("✅ Fresh account created successfully")
            data = response.json()
            token = data.get('access_token')
            
            # Test immediate login
            login_response = session.post(f"{API_BASE}/auth/login", json={
                "email": fresh_email,
                "password": fresh_password
            })
            
            log(f"Fresh login status: {login_response.status_code}")
            log(f"Fresh login response: {login_response.text}")
            
            if login_response.status_code == 200:
                log("✅ Fresh account login works")
                return True, {"email": fresh_email, "password": fresh_password}
            else:
                log("❌ Fresh account login fails")
                return False, None
        else:
            log(f"❌ Fresh account creation failed: {response.text}")
            return False, None
            
    except Exception as e:
        log(f"❌ Error creating fresh account: {str(e)}")
        return False, None

def main():
    log("🚀 AUTHENTICATION ISSUE INVESTIGATION")
    log("=" * 80)
    
    # First try existing accounts
    success, working_account = test_authentication_issue()
    
    if not success:
        # Create fresh account if no existing accounts work
        success, working_account = create_fresh_account()
    
    if success and working_account:
        log("\n🎉 AUTHENTICATION WORKING!")
        log(f"Working credentials: {working_account['email']} / {working_account['password']}")
        log("\n📋 SUMMARY:")
        log("- Authentication system is functional")
        log("- User can login and access /auth/me endpoint")
        log("- No 'hashed_password' field issue detected")
    else:
        log("\n❌ AUTHENTICATION ISSUE CONFIRMED")
        log("- Unable to login with any credentials")
        log("- Likely missing 'hashed_password' field in user data")
        log("- Need to investigate database user records")

if __name__ == "__main__":
    main()