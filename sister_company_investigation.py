#!/usr/bin/env python3
"""
Sister Company Investigation Script
Specifically investigating the user's reported issues:
1. User's account doesn't show sister companies
2. "Company setup already completed" error when trying to add companies
"""

import requests
import json
import os
from datetime import datetime
import sys
import time
import random

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://zoios-erp-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Known working test account from test_result.md
WORKING_TEST_EMAIL = "usertestsister@example.com"
WORKING_TEST_PASSWORD = "testsister123"

class SisterCompanyInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_working_account_login(self):
        """Test login with the known working account"""
        self.log("Testing login with known working account (usertestsister@example.com)...")
        
        login_data = {
            "email": WORKING_TEST_EMAIL,
            "password": WORKING_TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            self.log(f"Working account login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log("✅ Working account login successful")
                self.log(f"User ID: {self.user_data.get('id')}")
                self.log(f"Email: {self.user_data.get('email')}")
                self.log(f"Onboarding completed: {self.user_data.get('onboarding_completed')}")
                return True
            else:
                self.log(f"❌ Working account login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Working account login error: {str(e)}")
            return False
    
    def test_sister_company_display(self):
        """Test sister company display functionality"""
        self.log("Testing sister company display...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test GET /api/companies/management endpoint
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            self.log(f"Companies management response status: {response.status_code}")
            self.log(f"Companies management response: {response.text}")
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Found {len(companies)} companies")
                
                # Analyze company structure
                main_companies = [c for c in companies if c.get('is_main_company', False)]
                sister_companies = [c for c in companies if not c.get('is_main_company', True)]
                
                self.log(f"Main companies: {len(main_companies)}")
                self.log(f"Sister companies: {len(sister_companies)}")
                
                # Display detailed company information
                for i, company in enumerate(companies):
                    company_type = "MAIN" if company.get('is_main_company', False) else "SISTER"
                    self.log(f"Company {i+1} ({company_type}): {company.get('company_name')} - ID: {company.get('id')}")
                    self.log(f"  Business Type: {company.get('business_type')}")
                    self.log(f"  Parent Company ID: {company.get('parent_company_id')}")
                    self.log(f"  Base Currency: {company.get('base_currency')}")
                
                if len(sister_companies) > 0:
                    self.log("✅ Sister companies are visible in API response")
                    return True
                else:
                    self.log("❌ No sister companies found in API response")
                    return False
            else:
                self.log(f"❌ Companies management failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister company display error: {str(e)}")
            return False
    
    def test_company_setup_limitation(self):
        """Test the 'company setup already completed' limitation"""
        self.log("Testing company setup limitation...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Try to create another company setup
        setup_data = {
            "company_name": "Additional Test Company",
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR"],
            "business_type": "Corporation",
            "industry": "Technology",
            "address": "456 Additional Street",
            "city": "Additional City",
            "state": "CA",
            "postal_code": "54321",
            "phone": "+1-555-987-6543",
            "email": WORKING_TEST_EMAIL,
            "website": "https://additional.com",
            "tax_number": "ADD123456",
            "registration_number": "ADDREG123"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Additional company setup response status: {response.status_code}")
            self.log(f"Additional company setup response: {response.text}")
            
            if response.status_code == 400 and "already completed" in response.text:
                self.log("✅ Company setup limitation confirmed - 'already completed' error reproduced")
                return True
            elif response.status_code == 200:
                self.log("⚠️ Additional company setup succeeded - limitation may not be working")
                return False
            else:
                self.log(f"❌ Unexpected response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company setup limitation test error: {str(e)}")
            return False
    
    def test_sister_company_creation_endpoint(self):
        """Test the sister company creation endpoint"""
        self.log("Testing sister company creation endpoint...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Try to add a sister company
        sister_data = {
            "company_name": "New Sister Company Test",
            "country_code": "GB",
            "base_currency": "GBP",
            "business_type": "Private Limited Company",
            "industry": "Finance",
            "fiscal_year_start": "01-01"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/company/sister-companies", json=sister_data, headers=headers)
            self.log(f"Sister company creation response status: {response.status_code}")
            self.log(f"Sister company creation response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Sister company creation successful")
                self.log(f"Sister company ID: {data.get('id')}")
                self.log(f"Sister company name: {data.get('company_name')}")
                return True
            elif response.status_code == 400:
                self.log(f"❌ Sister company creation failed with validation error: {response.text}")
                return False
            elif response.status_code == 404:
                self.log(f"❌ Sister company creation failed - company setup not found: {response.text}")
                return False
            else:
                self.log(f"❌ Sister company creation failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister company creation error: {str(e)}")
            return False
    
    def test_get_sister_companies_endpoint(self):
        """Test the get sister companies endpoint"""
        self.log("Testing get sister companies endpoint...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
            self.log(f"Get sister companies response status: {response.status_code}")
            self.log(f"Get sister companies response: {response.text}")
            
            if response.status_code == 200:
                sister_companies = response.json()
                self.log(f"✅ Found {len(sister_companies)} sister companies via dedicated endpoint")
                
                for i, sister in enumerate(sister_companies):
                    self.log(f"Sister Company {i+1}: {sister.get('company_name')} - ID: {sister.get('id')}")
                    self.log(f"  Group Company ID: {sister.get('group_company_id')}")
                    self.log(f"  Business Type: {sister.get('business_type')}")
                    self.log(f"  Base Currency: {sister.get('base_currency')}")
                    self.log(f"  Is Active: {sister.get('is_active')}")
                
                return len(sister_companies) > 0
            else:
                self.log(f"❌ Get sister companies failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Get sister companies error: {str(e)}")
            return False
    
    def test_company_setup_details(self):
        """Test company setup details to understand the current setup"""
        self.log("Testing company setup details...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            self.log(f"Company setup details response status: {response.status_code}")
            self.log(f"Company setup details response: {response.text}")
            
            if response.status_code == 200:
                setup = response.json()
                self.log("✅ Company setup details retrieved")
                self.log(f"Company Name: {setup.get('company_name')}")
                self.log(f"Business Type: {setup.get('business_type')}")
                self.log(f"Setup Completed: {setup.get('setup_completed')}")
                self.log(f"User ID: {setup.get('user_id')}")
                self.log(f"Company ID: {setup.get('id')}")
                
                # Check if this is a Group Company
                if setup.get('business_type') == 'Group Company':
                    self.log("✅ This is a Group Company - should support sister companies")
                else:
                    self.log(f"⚠️ This is a {setup.get('business_type')} - may not support sister companies")
                
                return True
            else:
                self.log(f"❌ Company setup details failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company setup details error: {str(e)}")
            return False
    
    def investigate_recent_accounts(self):
        """Look for recent user accounts that might belong to the user"""
        self.log("Investigating recent user accounts...")
        
        # Try to login with admin credentials to check user list
        admin_credentials = [
            {"email": "admin@2mholding.com", "password": "admin123"},
            {"email": "admin@zoios.com", "password": "admin123"}
        ]
        
        for creds in admin_credentials:
            try:
                response = self.session.post(f"{API_BASE}/auth/login", json=creds)
                if response.status_code == 200:
                    admin_token = response.json().get('access_token')
                    headers = {
                        "Authorization": f"Bearer {admin_token}",
                        "Content-Type": "application/json"
                    }
                    
                    # Get all users
                    users_response = self.session.get(f"{API_BASE}/admin/users", headers=headers)
                    if users_response.status_code == 200:
                        users = users_response.json()
                        self.log(f"✅ Found {len(users)} total users in system")
                        
                        # Look for recent users (last 7 days)
                        recent_users = []
                        for user in users:
                            created_at = user.get('created_at')
                            if created_at:
                                try:
                                    # Parse the datetime
                                    if isinstance(created_at, str):
                                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                    else:
                                        created_date = created_at
                                    
                                    days_ago = (datetime.now(created_date.tzinfo) - created_date).days
                                    if days_ago <= 7:
                                        recent_users.append({
                                            'email': user.get('email'),
                                            'name': user.get('name'),
                                            'company': user.get('company'),
                                            'created_at': created_at,
                                            'days_ago': days_ago,
                                            'onboarding_completed': user.get('onboarding_completed')
                                        })
                                except:
                                    pass
                        
                        self.log(f"Recent users (last 7 days): {len(recent_users)}")
                        for user in recent_users:
                            self.log(f"  - {user['email']} ({user['name']}) - {user['days_ago']} days ago")
                            self.log(f"    Company: {user['company']}")
                            self.log(f"    Onboarding: {user['onboarding_completed']}")
                        
                        return recent_users
                    break
            except Exception as e:
                continue
        
        self.log("❌ Could not access admin user list")
        return []
    
    def test_user_account_scenarios(self):
        """Test different user account scenarios"""
        self.log("Testing different user account scenarios...")
        
        # Scenario 1: Create a new user with Private Limited Company
        self.log("\n=== SCENARIO 1: Private Limited Company ===")
        private_email = f"private{int(time.time())}@example.com"
        self.test_account_scenario(private_email, "Private Limited Company")
        
        # Scenario 2: Create a new user with Group Company
        self.log("\n=== SCENARIO 2: Group Company ===")
        group_email = f"group{int(time.time())}@example.com"
        self.test_account_scenario(group_email, "Group Company", with_sisters=True)
    
    def test_account_scenario(self, email, business_type, with_sisters=False):
        """Test a specific account scenario"""
        self.log(f"Testing account scenario: {email} with {business_type}")
        
        # Create account
        signup_data = {
            "email": email,
            "password": "testpass123",
            "name": "Test User",
            "company": "Test Company"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            if response.status_code != 200:
                self.log(f"❌ Account creation failed: {response.text}")
                return False
            
            token = response.json().get('access_token')
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Setup company
            setup_data = {
                "company_name": f"Test {business_type}",
                "country_code": "US",
                "base_currency": "USD",
                "additional_currencies": ["EUR"],
                "business_type": business_type,
                "industry": "Technology",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "CA",
                "postal_code": "12345",
                "phone": "+1-555-123-4567",
                "email": email,
                "website": "https://test.com",
                "tax_number": "123456789",
                "registration_number": "REG123456"
            }
            
            # Add sister companies if requested
            if with_sisters:
                setup_data["sister_companies"] = [
                    {
                        "company_name": "Sister Company 1",
                        "country": "GB",
                        "base_currency": "GBP",
                        "business_type": "Private Limited Company",
                        "industry": "Finance"
                    },
                    {
                        "company_name": "Sister Company 2", 
                        "country": "CA",
                        "base_currency": "CAD",
                        "business_type": "Corporation",
                        "industry": "Technology"
                    }
                ]
            
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            if response.status_code != 200:
                self.log(f"❌ Company setup failed: {response.text}")
                return False
            
            self.log(f"✅ Account scenario created successfully")
            
            # Test company management endpoint
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            if response.status_code == 200:
                companies = response.json()
                self.log(f"Companies found: {len(companies)}")
                
                for company in companies:
                    company_type = "MAIN" if company.get('is_main_company', False) else "SISTER"
                    self.log(f"  {company_type}: {company.get('company_name')}")
                
                # Try to create another company setup (should fail)
                self.log("Testing second company setup (should fail)...")
                response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
                if response.status_code == 400 and "already completed" in response.text:
                    self.log("✅ Second setup correctly blocked")
                else:
                    self.log(f"⚠️ Second setup response: {response.status_code} - {response.text}")
                
                return True
            else:
                self.log(f"❌ Companies management failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Account scenario error: {str(e)}")
            return False
    
    def run_investigation(self):
        """Run the complete sister company investigation"""
        self.log("🔍 Starting Sister Company Investigation...")
        self.log("=" * 60)
        
        results = {}
        
        # Test 1: Login with working account
        self.log("\n1. Testing login with known working account...")
        results['working_account_login'] = self.test_working_account_login()
        
        if results['working_account_login']:
            # Test 2: Check sister company display
            self.log("\n2. Testing sister company display...")
            results['sister_company_display'] = self.test_sister_company_display()
            
            # Test 3: Test company setup limitation
            self.log("\n3. Testing company setup limitation...")
            results['company_setup_limitation'] = self.test_company_setup_limitation()
            
            # Test 4: Test sister company creation endpoint
            self.log("\n4. Testing sister company creation endpoint...")
            results['sister_company_creation'] = self.test_sister_company_creation_endpoint()
            
            # Test 5: Test get sister companies endpoint
            self.log("\n5. Testing get sister companies endpoint...")
            results['get_sister_companies'] = self.test_get_sister_companies_endpoint()
            
            # Test 6: Test company setup details
            self.log("\n6. Testing company setup details...")
            results['company_setup_details'] = self.test_company_setup_details()
        
        # Test 7: Investigate recent accounts
        self.log("\n7. Investigating recent user accounts...")
        recent_users = self.investigate_recent_accounts()
        results['recent_users_found'] = len(recent_users) > 0
        
        # Test 8: Test different account scenarios
        self.log("\n8. Testing different user account scenarios...")
        self.test_user_account_scenarios()
        
        # Summary
        self.log("\n" + "=" * 60)
        self.log("🔍 INVESTIGATION SUMMARY")
        self.log("=" * 60)
        
        for test, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test}: {status}")
        
        # Analysis
        self.log("\n📊 ANALYSIS:")
        
        if results.get('working_account_login') and results.get('sister_company_display'):
            self.log("✅ Sister company functionality IS working with the test account")
        else:
            self.log("❌ Sister company functionality has issues")
        
        if results.get('company_setup_limitation'):
            self.log("✅ Company setup limitation is working as designed")
            self.log("   - Users can only complete company setup once")
            self.log("   - This prevents creating multiple main companies")
        else:
            self.log("❌ Company setup limitation may not be working")
        
        self.log("\n💡 RECOMMENDATIONS:")
        self.log("1. Check if user's account has business_type set to 'Group Company'")
        self.log("2. Verify sister companies were created during initial setup")
        self.log("3. Check if user is looking in the correct UI section")
        self.log("4. Consider allowing users to modify company setup after completion")

if __name__ == "__main__":
    investigator = SisterCompanyInvestigator()
    investigator.run_investigation()