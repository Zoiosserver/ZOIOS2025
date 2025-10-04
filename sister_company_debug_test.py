#!/usr/bin/env python3
"""
Sister Company Debug Test Script
Comprehensive testing for sister company creation and display issue as requested in review.

Tests:
1. Create a Group Company with sister companies - step by step process
2. Verify sister company database storage
3. Test API response structure for GET /api/companies/management
4. Debug the company setup process (POST /api/setup/company)
5. Provide detailed API response structure
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

# Generate unique test credentials for fresh testing
timestamp = str(int(time.time()))
random_suffix = str(random.randint(1000, 9999))
TEST_EMAIL = f"sistertest{timestamp}{random_suffix}@example.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "Sister Company Test User"
TEST_COMPANY = "Main Group Company"

class SisterCompanyDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.company_setup_data = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def step_1_create_account(self):
        """Step 1: Create new account"""
        self.log("=== STEP 1: Creating new account ===")
        
        signup_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "company": TEST_COMPANY
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            self.log(f"Account creation response status: {response.status_code}")
            self.log(f"Account creation response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log("✅ Account created successfully")
                self.log(f"User ID: {self.user_data.get('id')}")
                self.log(f"Email: {self.user_data.get('email')}")
                self.log(f"Onboarding completed: {self.user_data.get('onboarding_completed')}")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                self.log("⚠️ User already exists, proceeding with login")
                return self.login_existing_user()
            else:
                self.log(f"❌ Account creation failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Account creation error: {str(e)}")
            return False
    
    def login_existing_user(self):
        """Login with existing user credentials"""
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log("✅ Login successful")
                return True
            else:
                self.log(f"❌ Login failed: {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}")
            return False
    
    def step_2_create_group_company_with_sisters(self):
        """Step 2: During company setup, select 'Group Company' and add 2-3 sister companies"""
        self.log("=== STEP 2: Creating Group Company with Sister Companies ===")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Company setup data with Group Company type and sister companies
        setup_data = {
            "company_name": "Main Group Company Ltd",
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR", "GBP", "INR"],
            "business_type": "Group Company",  # This is the key - Group Company
            "industry": "Technology",
            "address": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "phone": "+1-555-123-4567",
            "email": TEST_EMAIL,
            "website": "https://maingroupcompany.com",
            "tax_number": "TAX123456789",
            "registration_number": "REG987654321",
            # Sister companies - this is what we're testing
            "sister_companies": [
                {
                    "company_name": "Sister Company Alpha",
                    "country": "US",
                    "base_currency": "USD",
                    "business_type": "Private Limited Company",
                    "industry": "Technology",
                    "fiscal_year_start": "01-01"
                },
                {
                    "company_name": "Sister Company Beta",
                    "country": "GB",
                    "base_currency": "GBP",
                    "business_type": "Private Limited Company", 
                    "industry": "Finance",
                    "fiscal_year_start": "04-01"
                },
                {
                    "company_name": "Sister Company Gamma",
                    "country": "IN",
                    "base_currency": "INR",
                    "business_type": "Private Limited Company",
                    "industry": "Manufacturing",
                    "fiscal_year_start": "04-01"
                }
            ]
        }
        
        self.log(f"Sending company setup with {len(setup_data['sister_companies'])} sister companies:")
        for i, sister in enumerate(setup_data['sister_companies']):
            self.log(f"  Sister {i+1}: {sister['company_name']} ({sister['country']}, {sister['base_currency']})")
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Company setup response status: {response.status_code}")
            self.log(f"Company setup response: {response.text}")
            
            if response.status_code == 200:
                self.company_setup_data = response.json()
                self.log("✅ Group Company setup successful")
                self.log(f"Main Company ID: {self.company_setup_data.get('id')}")
                self.log(f"Company Name: {self.company_setup_data.get('company_name')}")
                self.log(f"Business Type: {self.company_setup_data.get('business_type')}")
                self.log(f"Setup Completed: {self.company_setup_data.get('setup_completed')}")
                return True
            else:
                self.log(f"❌ Company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company setup error: {str(e)}")
            return False
    
    def step_3_verify_sister_company_database_storage(self):
        """Step 3: Verify sister companies are actually saved to the database"""
        self.log("=== STEP 3: Verifying Sister Company Database Storage ===")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test GET /api/company/sister-companies endpoint
            response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
            self.log(f"Sister companies API response status: {response.status_code}")
            self.log(f"Sister companies API response: {response.text}")
            
            if response.status_code == 200:
                sister_companies = response.json()
                self.log(f"✅ Sister companies API working - found {len(sister_companies)} sister companies")
                
                if len(sister_companies) > 0:
                    self.log("Sister companies found in database:")
                    for i, sister in enumerate(sister_companies):
                        self.log(f"  Sister {i+1}:")
                        self.log(f"    ID: {sister.get('id')}")
                        self.log(f"    Name: {sister.get('company_name')}")
                        self.log(f"    Country: {sister.get('country_code')}")
                        self.log(f"    Currency: {sister.get('base_currency')}")
                        self.log(f"    Group Company ID: {sister.get('group_company_id')}")
                        self.log(f"    Is Active: {sister.get('is_active')}")
                    
                    # Verify group_company_id linking
                    main_company_id = self.company_setup_data.get('id') if self.company_setup_data else None
                    if main_company_id:
                        correct_linking = all(sister.get('group_company_id') == main_company_id for sister in sister_companies)
                        if correct_linking:
                            self.log("✅ Sister companies correctly linked to main company")
                        else:
                            self.log("❌ Sister companies NOT correctly linked to main company")
                            return False
                    
                    return True
                else:
                    self.log("❌ No sister companies found in database - this is the issue!")
                    return False
            else:
                self.log(f"❌ Sister companies API failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister companies verification error: {str(e)}")
            return False
    
    def step_4_test_companies_management_api(self):
        """Step 4: Test GET /api/companies/management endpoint and examine response structure"""
        self.log("=== STEP 4: Testing Companies Management API ===")
        
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
            self.log(f"Companies management API response status: {response.status_code}")
            self.log(f"Companies management API response: {response.text}")
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Companies management API working - found {len(companies)} companies")
                
                # Analyze the response structure
                self.log("=== DETAILED API RESPONSE ANALYSIS ===")
                self.log(f"Response type: {type(companies)}")
                self.log(f"Number of companies returned: {len(companies)}")
                
                if len(companies) > 0:
                    for i, company in enumerate(companies):
                        self.log(f"\nCompany {i+1} structure:")
                        self.log(f"  ID: {company.get('id')}")
                        self.log(f"  Name: {company.get('company_name')}")
                        self.log(f"  Business Type: {company.get('business_type')}")
                        self.log(f"  Country: {company.get('country_code')}")
                        self.log(f"  Currency: {company.get('base_currency')}")
                        self.log(f"  Is Main Company: {company.get('is_main_company')}")
                        self.log(f"  Parent Company ID: {company.get('parent_company_id')}")
                        self.log(f"  All fields: {list(company.keys())}")
                    
                    # Check for main company
                    main_companies = [c for c in companies if c.get('is_main_company') == True]
                    sister_companies = [c for c in companies if c.get('is_main_company') == False]
                    
                    self.log(f"\nMain companies found: {len(main_companies)}")
                    self.log(f"Sister companies found: {len(sister_companies)}")
                    
                    if len(main_companies) > 0:
                        self.log("✅ Main company found with is_main_company: true")
                    else:
                        self.log("❌ No main company found with is_main_company: true")
                    
                    if len(sister_companies) > 0:
                        self.log("✅ Sister companies found with is_main_company: false")
                        for sister in sister_companies:
                            parent_id = sister.get('parent_company_id')
                            if parent_id:
                                self.log(f"  Sister company '{sister.get('company_name')}' has parent_company_id: {parent_id}")
                            else:
                                self.log(f"  ❌ Sister company '{sister.get('company_name')}' missing parent_company_id")
                    else:
                        self.log("❌ No sister companies found with is_main_company: false - THIS IS THE ISSUE!")
                        return False
                    
                    return True
                else:
                    self.log("❌ No companies found in management API - this is the issue!")
                    return False
            else:
                self.log(f"❌ Companies management API failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Companies management API error: {str(e)}")
            return False
    
    def step_5_test_company_list_api(self):
        """Step 5: Test GET /api/company/list endpoint for comparison"""
        self.log("=== STEP 5: Testing Company List API for Comparison ===")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test GET /api/company/list endpoint
            response = self.session.get(f"{API_BASE}/company/list", headers=headers)
            self.log(f"Company list API response status: {response.status_code}")
            self.log(f"Company list API response: {response.text}")
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Company list API working - found {len(companies)} companies")
                
                # Compare with companies/management API
                self.log("=== COMPANY LIST API STRUCTURE ===")
                for i, company in enumerate(companies):
                    self.log(f"\nCompany {i+1} from /company/list:")
                    self.log(f"  ID: {company.get('id')}")
                    self.log(f"  Name: {company.get('name')}")
                    self.log(f"  Business Type: {company.get('business_type')}")
                    self.log(f"  Country: {company.get('country_code')}")
                    self.log(f"  Currency: {company.get('base_currency')}")
                    self.log(f"  Is Main Company: {company.get('is_main_company')}")
                    self.log(f"  Ownership Percentage: {company.get('ownership_percentage')}")
                
                return True
            else:
                self.log(f"❌ Company list API failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company list API error: {str(e)}")
            return False
    
    def step_6_debug_company_setup_process(self):
        """Step 6: Debug the company setup process by examining the request payload"""
        self.log("=== STEP 6: Debugging Company Setup Process ===")
        
        # This step analyzes what we sent vs what should be processed
        if not self.company_setup_data:
            self.log("❌ No company setup data available for analysis")
            return False
        
        self.log("Company setup request analysis:")
        self.log(f"  Main company created: {self.company_setup_data.get('company_name')}")
        self.log(f"  Business type: {self.company_setup_data.get('business_type')}")
        self.log(f"  Setup completed: {self.company_setup_data.get('setup_completed')}")
        
        # Check if sister companies were mentioned in the response
        if 'sister_companies' in self.company_setup_data:
            self.log(f"  Sister companies in response: {len(self.company_setup_data['sister_companies'])}")
        else:
            self.log("  ❌ No sister_companies field in setup response")
        
        return True
    
    def step_7_verify_auth_me_after_setup(self):
        """Step 7: Verify user authentication state after company setup"""
        self.log("=== STEP 7: Verifying Auth State After Setup ===")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
            self.log(f"/auth/me response status: {response.status_code}")
            self.log(f"/auth/me response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ /auth/me working after company setup")
                self.log(f"  User ID: {data.get('id')}")
                self.log(f"  Email: {data.get('email')}")
                self.log(f"  Onboarding completed: {data.get('onboarding_completed')}")
                self.log(f"  Role: {data.get('role')}")
                
                if data.get('onboarding_completed'):
                    self.log("✅ Onboarding completed status updated correctly")
                else:
                    self.log("❌ Onboarding completed status NOT updated")
                
                return True
            else:
                self.log(f"❌ /auth/me failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ /auth/me error: {str(e)}")
            return False
    
    def run_comprehensive_debug(self):
        """Run all debug steps in sequence"""
        self.log("🔍 STARTING COMPREHENSIVE SISTER COMPANY DEBUG TEST")
        self.log("=" * 80)
        
        results = {}
        
        # Step 1: Create account
        results['step_1_account'] = self.step_1_create_account()
        
        # Step 2: Create Group Company with sister companies
        if results['step_1_account']:
            results['step_2_group_setup'] = self.step_2_create_group_company_with_sisters()
        else:
            results['step_2_group_setup'] = False
        
        # Step 3: Verify sister company database storage
        if results['step_2_group_setup']:
            results['step_3_database_verify'] = self.step_3_verify_sister_company_database_storage()
        else:
            results['step_3_database_verify'] = False
        
        # Step 4: Test companies management API
        if results['step_2_group_setup']:
            results['step_4_management_api'] = self.step_4_test_companies_management_api()
        else:
            results['step_4_management_api'] = False
        
        # Step 5: Test company list API
        if results['step_2_group_setup']:
            results['step_5_list_api'] = self.step_5_test_company_list_api()
        else:
            results['step_5_list_api'] = False
        
        # Step 6: Debug company setup process
        results['step_6_debug_setup'] = self.step_6_debug_company_setup_process()
        
        # Step 7: Verify auth state
        if results['step_2_group_setup']:
            results['step_7_auth_verify'] = self.step_7_verify_auth_me_after_setup()
        else:
            results['step_7_auth_verify'] = False
        
        # Summary
        self.log("=" * 80)
        self.log("🔍 COMPREHENSIVE DEBUG TEST RESULTS SUMMARY")
        self.log("=" * 80)
        
        for step, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{step}: {status}")
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        self.log(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
        
        if not results.get('step_3_database_verify', False):
            self.log("\n🚨 CRITICAL ISSUE IDENTIFIED:")
            self.log("Sister companies are NOT being saved to the database correctly!")
            self.log("This explains why they don't appear in the Company Management section.")
        
        if not results.get('step_4_management_api', False):
            self.log("\n🚨 CRITICAL ISSUE IDENTIFIED:")
            self.log("Companies Management API is not returning sister companies!")
            self.log("Even if saved, they're not being retrieved properly.")
        
        return results

def main():
    """Main function to run the sister company debug test"""
    debugger = SisterCompanyDebugger()
    results = debugger.run_comprehensive_debug()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()