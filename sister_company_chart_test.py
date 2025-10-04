#!/usr/bin/env python3
"""
Sister Company Chart of Accounts Investigation Test
Tests the specific issue reported: "View Chart of Accounts" for sister companies shows "Failed to load accounts" and "No accounts found for this company"

Investigation Areas:
1. Check if sister companies have chart of accounts created when they are set up
2. Test GET /api/company/{sister_company_id}/chart-of-accounts for sister companies
3. Check if the backend creates accounts for sister companies during setup
4. Test the chart of accounts creation process for Group Companies with sister companies
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

# Use existing working accounts from test_result.md
WORKING_ACCOUNTS = [
    {"email": "usertestsister@example.com", "password": "testsister123"},
    {"email": "userfix1759589474@example.com", "password": "userfix123"}
]

class SisterCompanyChartTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.main_company_id = None
        self.sister_companies = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def login_with_working_account(self):
        """Login with one of the known working accounts that has sister companies"""
        self.log("Attempting to login with working account that has sister companies...")
        
        for account in WORKING_ACCOUNTS:
            login_data = {
                "email": account["email"],
                "password": account["password"]
            }
            
            try:
                response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                self.log(f"Login attempt for {account['email']} - Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get('access_token')
                    self.user_data = data.get('user')
                    self.log(f"✅ Successfully logged in as {account['email']}")
                    self.log(f"User ID: {self.user_data.get('id')}")
                    self.log(f"Onboarding completed: {self.user_data.get('onboarding_completed')}")
                    return True
                else:
                    self.log(f"❌ Login failed for {account['email']}: {response.text}")
                    
            except Exception as e:
                self.log(f"❌ Login error for {account['email']}: {str(e)}")
                
        return False
    
    def get_companies_management(self):
        """Get all companies (main + sister companies) for the logged-in user"""
        self.log("Getting companies management data...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            self.log(f"Companies management response status: {response.status_code}")
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Found {len(companies)} companies")
                
                # Separate main company and sister companies
                main_companies = [c for c in companies if c.get('is_main_company', False)]
                sister_companies = [c for c in companies if not c.get('is_main_company', False)]
                
                if main_companies:
                    self.main_company_id = main_companies[0]['id']
                    self.log(f"Main company: {main_companies[0]['company_name']} (ID: {self.main_company_id})")
                
                self.sister_companies = sister_companies
                self.log(f"Sister companies found: {len(sister_companies)}")
                
                for i, sister in enumerate(sister_companies):
                    self.log(f"  Sister {i+1}: {sister['company_name']} (ID: {sister['id']})")
                
                return len(companies) > 0
            else:
                self.log(f"❌ Companies management failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Companies management error: {str(e)}")
            return False
    
    def test_main_company_chart_of_accounts(self):
        """Test chart of accounts for main company (should work)"""
        self.log("Testing main company chart of accounts...")
        
        if not self.main_company_id:
            self.log("❌ No main company ID available")
            return False
            
        return self.test_company_chart_of_accounts(self.main_company_id, "Main Company")
    
    def test_sister_companies_chart_of_accounts(self):
        """Test chart of accounts for all sister companies (this is where the issue should be)"""
        self.log("Testing sister companies chart of accounts...")
        
        if not self.sister_companies:
            self.log("❌ No sister companies available for testing")
            return False
        
        all_passed = True
        for i, sister in enumerate(self.sister_companies):
            self.log(f"\n--- Testing Sister Company {i+1}: {sister['company_name']} ---")
            result = self.test_company_chart_of_accounts(sister['id'], f"Sister Company {i+1}")
            if not result:
                all_passed = False
        
        return all_passed
    
    def test_company_chart_of_accounts(self, company_id, company_type):
        """Test chart of accounts for a specific company"""
        self.log(f"Testing chart of accounts for {company_type} (ID: {company_id})...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/company/{company_id}/chart-of-accounts", headers=headers)
            self.log(f"Chart of accounts response status: {response.status_code}")
            self.log(f"Chart of accounts response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Chart of accounts retrieved for {company_type}")
                
                # Check company info
                company_info = data.get('company', {})
                self.log(f"Company name: {company_info.get('name')}")
                self.log(f"Business type: {company_info.get('business_type')}")
                self.log(f"Base currency: {company_info.get('base_currency')}")
                self.log(f"Is main company: {company_info.get('is_main_company')}")
                
                # Check accounts by category
                accounts_by_category = data.get('accounts_by_category', {})
                total_accounts = data.get('total_accounts', 0)
                
                self.log(f"Total accounts: {total_accounts}")
                self.log(f"Categories found: {list(accounts_by_category.keys())}")
                
                if total_accounts > 0:
                    self.log(f"✅ {company_type} has {total_accounts} accounts")
                    
                    # Show sample accounts from each category
                    for category, accounts in accounts_by_category.items():
                        self.log(f"  {category}: {len(accounts)} accounts")
                        if accounts:
                            sample_account = accounts[0]
                            self.log(f"    Sample: {sample_account.get('code')} - {sample_account.get('name')}")
                    
                    return True
                else:
                    self.log(f"❌ {company_type} has NO accounts - THIS IS THE ISSUE!")
                    return False
                    
            elif response.status_code == 403:
                self.log(f"❌ Access denied to {company_type} chart of accounts")
                return False
            elif response.status_code == 404:
                self.log(f"❌ {company_type} not found or no chart of accounts")
                return False
            else:
                self.log(f"❌ Chart of accounts failed for {company_type}: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Chart of accounts error for {company_type}: {str(e)}")
            return False
    
    def investigate_sister_company_setup_process(self):
        """Investigate how sister companies are created and if accounts are generated"""
        self.log("Investigating sister company setup process...")
        
        if not self.sister_companies:
            self.log("❌ No sister companies to investigate")
            return False
        
        # Check if we can find the sister companies in the database
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Get sister companies list via API
            response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
            self.log(f"Sister companies API response status: {response.status_code}")
            
            if response.status_code == 200:
                sister_companies_api = response.json()
                self.log(f"✅ Sister companies API returned {len(sister_companies_api)} companies")
                
                for i, sister in enumerate(sister_companies_api):
                    self.log(f"Sister {i+1} from API:")
                    self.log(f"  ID: {sister.get('id')}")
                    self.log(f"  Name: {sister.get('company_name')}")
                    self.log(f"  Country: {sister.get('country_code')}")
                    self.log(f"  Currency: {sister.get('base_currency')}")
                    self.log(f"  Business Type: {sister.get('business_type')}")
                    self.log(f"  Accounting System: {sister.get('accounting_system')}")
                    self.log(f"  Is Active: {sister.get('is_active')}")
                
                return True
            else:
                self.log(f"❌ Sister companies API failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister company investigation error: {str(e)}")
            return False
    
    def create_fresh_test_account(self):
        """Create a fresh test account with Group Company and sister companies"""
        self.log("Creating fresh test account with Group Company setup...")
        
        # Generate unique test credentials
        timestamp = str(int(time.time()))
        test_email = f"charttest{timestamp}@example.com"
        test_password = "charttest123"
        
        # Sign up new user
        signup_data = {
            "email": test_email,
            "password": test_password,
            "name": "Chart Test User",
            "company": "Chart Test Company"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            self.log(f"Fresh user signup response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log(f"✅ Fresh user created: {test_email}")
                
                # Create Group Company with sister companies
                return self.setup_group_company_with_sisters()
            else:
                self.log(f"❌ Fresh user signup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Fresh user creation error: {str(e)}")
            return False
    
    def setup_group_company_with_sisters(self):
        """Setup Group Company with sister companies"""
        self.log("Setting up Group Company with sister companies...")
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        setup_data = {
            "company_name": "Chart Test Group Company",
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR", "GBP"],
            "business_type": "Group Company",
            "industry": "Technology",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "CA",
            "postal_code": "12345",
            "phone": "+1-555-123-4567",
            "email": self.user_data.get('email'),
            "website": "https://testcompany.com",
            "tax_number": "123456789",
            "registration_number": "REG123456",
            "sister_companies": [
                {
                    "company_name": "Chart Test Sister Alpha",
                    "country": "US",
                    "base_currency": "USD",
                    "business_type": "Private Limited Company",
                    "industry": "Technology"
                },
                {
                    "company_name": "Chart Test Sister Beta",
                    "country": "GB",
                    "base_currency": "GBP",
                    "business_type": "Limited Company",
                    "industry": "Technology"
                }
            ]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Group Company setup response status: {response.status_code}")
            self.log(f"Group Company setup response: {response.text}")
            
            if response.status_code == 200:
                self.log("✅ Group Company with sister companies created successfully")
                return True
            else:
                self.log(f"❌ Group Company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Group Company setup error: {str(e)}")
            return False

    def test_create_fresh_group_company_with_sister(self):
        """Create a fresh Group Company with sister companies to test the setup process"""
        self.log("Testing fresh Group Company creation with sister companies...")
        
        # Generate unique test credentials
        timestamp = str(int(time.time()))
        test_email = f"sistertest{timestamp}@example.com"
        test_password = "sistertest123"
        
        # Sign up new user
        signup_data = {
            "email": test_email,
            "password": test_password,
            "name": "Sister Test User",
            "company": "Sister Test Company"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            self.log(f"Fresh user signup response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                fresh_token = data.get('access_token')
                self.log("✅ Fresh user created successfully")
                
                headers = {
                    "Authorization": f"Bearer {fresh_token}",
                    "Content-Type": "application/json"
                }
                
                # Create Group Company with sister companies
                setup_data = {
                    "company_name": "Fresh Sister Test Group Company",
                    "country_code": "US",
                    "base_currency": "USD",
                    "additional_currencies": ["EUR", "GBP"],
                    "business_type": "Group Company",
                    "industry": "Technology",
                    "address": "123 Test Street",
                    "city": "Test City",
                    "state": "CA",
                    "postal_code": "12345",
                    "phone": "+1-555-123-4567",
                    "email": test_email,
                    "website": "https://testcompany.com",
                    "tax_number": "123456789",
                    "registration_number": "REG123456",
                    "sister_companies": [
                        {
                            "company_name": "Fresh Sister Company Alpha",
                            "country": "US",
                            "base_currency": "USD",
                            "business_type": "Private Limited Company",
                            "industry": "Technology"
                        },
                        {
                            "company_name": "Fresh Sister Company Beta",
                            "country": "GB",
                            "base_currency": "GBP",
                            "business_type": "Limited Company",
                            "industry": "Technology"
                        }
                    ]
                }
                
                response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
                self.log(f"Fresh Group Company setup response status: {response.status_code}")
                self.log(f"Fresh Group Company setup response: {response.text}")
                
                if response.status_code == 200:
                    self.log("✅ Fresh Group Company with sister companies created")
                    
                    # Now test chart of accounts for the fresh companies
                    # Get companies list
                    companies_response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
                    if companies_response.status_code == 200:
                        companies = companies_response.json()
                        self.log(f"Fresh setup created {len(companies)} companies")
                        
                        # Test chart of accounts for each company
                        for company in companies:
                            company_type = "Main Company" if company.get('is_main_company') else "Sister Company"
                            self.log(f"\n--- Testing Fresh {company_type}: {company['company_name']} ---")
                            
                            chart_response = self.session.get(f"{API_BASE}/company/{company['id']}/chart-of-accounts", headers=headers)
                            self.log(f"Chart response status: {chart_response.status_code}")
                            
                            if chart_response.status_code == 200:
                                chart_data = chart_response.json()
                                total_accounts = chart_data.get('total_accounts', 0)
                                self.log(f"✅ {company_type} has {total_accounts} accounts")
                                
                                if total_accounts == 0:
                                    self.log(f"❌ CRITICAL ISSUE: {company_type} has NO chart of accounts!")
                                    return False
                            else:
                                self.log(f"❌ Chart of accounts failed for {company_type}: {chart_response.text}")
                                return False
                        
                        self.log("✅ Fresh Group Company setup test completed successfully")
                        return True
                    else:
                        self.log("❌ Could not get companies list for fresh setup")
                        return False
                else:
                    self.log(f"❌ Fresh Group Company setup failed: {response.text}")
                    return False
            else:
                self.log(f"❌ Fresh user signup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Fresh Group Company test error: {str(e)}")
            return False
    
    def run_comprehensive_investigation(self):
        """Run comprehensive investigation of sister company chart of accounts issue"""
        self.log("=== SISTER COMPANY CHART OF ACCOUNTS INVESTIGATION ===")
        
        # Step 1: Try to login with working account, if fails create fresh account
        if not self.login_with_working_account():
            self.log("⚠️ Could not login with existing accounts, creating fresh test account...")
            if not self.create_fresh_test_account():
                self.log("❌ Could not create fresh test account")
                return False
        
        # Step 2: Get companies data
        if not self.get_companies_management():
            self.log("❌ Could not get companies data")
            return False
        
        # Step 3: Test main company chart of accounts (should work)
        self.log("\n=== TESTING MAIN COMPANY CHART OF ACCOUNTS ===")
        main_result = self.test_main_company_chart_of_accounts()
        
        # Step 4: Test sister companies chart of accounts (this is where the issue should be)
        self.log("\n=== TESTING SISTER COMPANIES CHART OF ACCOUNTS ===")
        sister_result = self.test_sister_companies_chart_of_accounts()
        
        # Step 5: Investigate sister company setup process
        self.log("\n=== INVESTIGATING SISTER COMPANY SETUP PROCESS ===")
        setup_result = self.investigate_sister_company_setup_process()
        
        # Step 6: Test fresh Group Company creation
        self.log("\n=== TESTING FRESH GROUP COMPANY CREATION ===")
        fresh_result = self.test_create_fresh_group_company_with_sister()
        
        # Summary
        self.log("\n=== INVESTIGATION SUMMARY ===")
        self.log(f"Main company chart of accounts: {'✅ WORKING' if main_result else '❌ FAILED'}")
        self.log(f"Sister companies chart of accounts: {'✅ WORKING' if sister_result else '❌ FAILED'}")
        self.log(f"Sister company setup investigation: {'✅ WORKING' if setup_result else '❌ FAILED'}")
        self.log(f"Fresh Group Company test: {'✅ WORKING' if fresh_result else '❌ FAILED'}")
        
        if not sister_result:
            self.log("\n❌ CRITICAL ISSUE CONFIRMED: Sister companies do not have chart of accounts!")
            self.log("RECOMMENDATION: Check backend logic in /api/setup/company endpoint")
            self.log("- Verify that chart of accounts are created for sister companies during Group Company setup")
            self.log("- Check if sister company IDs are being used correctly in chart_of_accounts table")
            self.log("- Ensure sister companies get the same chart template as main company")
        else:
            self.log("\n✅ Sister company chart of accounts working correctly")
        
        return main_result and sister_result and setup_result and fresh_result

def main():
    """Main function to run the sister company chart of accounts investigation"""
    tester = SisterCompanyChartTester()
    
    try:
        success = tester.run_comprehensive_investigation()
        
        if success:
            print("\n🎉 INVESTIGATION COMPLETED SUCCESSFULLY")
            print("All sister company chart of accounts functionality is working correctly")
            sys.exit(0)
        else:
            print("\n❌ INVESTIGATION FOUND ISSUES")
            print("Sister company chart of accounts functionality has problems that need to be fixed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Investigation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Investigation failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()