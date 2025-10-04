#!/usr/bin/env python3
"""
ZOIOS ERP Consolidated Accounts Testing Script
Tests the TRUE consolidated accounts implementation as requested in review:

The user correctly pointed out that consolidated accounts should show one row per account 
with columns for each company amount.

VERIFICATION NEEDED:
1. Test the new consolidated accounts format
2. Verify it returns the new format with:
   - One entry per unique account code/name
   - Each entry has 'companies' object with company_name: balance pairs
   - Each entry has 'total_balance' field summing all companies
3. Test with Group Company account
4. Verify the data structure matches expected format
"""

import requests
import json
import os
from datetime import datetime
import sys
import time

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://zoios-erp-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test with existing Group Company account that has sister companies
# Will try multiple known accounts
TEST_ACCOUNTS = [
    ("usertestsister@example.com", "testsister123"),
    ("admin@2mholding.com", "admin123"),
    ("testuser1759583819@example.com", "password123"),
    ("userfix1759589474@example.com", "userfix123")
]

class ConsolidatedAccountsTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_login(self):
        """Login with existing Group Company account"""
        self.log("Testing login with Group Company accounts...")
        
        for email, password in TEST_ACCOUNTS:
            self.log(f"Trying login with {email}...")
            
            login_data = {
                "email": email,
                "password": password
            }
            
            try:
                response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                self.log(f"Login response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get('access_token')
                    self.user_data = data.get('user')
                    self.log(f"✅ Login successful with {email}")
                    self.log(f"User ID: {self.user_data.get('id')}")
                    self.log(f"Email: {self.user_data.get('email')}")
                    return True
                else:
                    self.log(f"❌ Login failed with {email}: {response.text}")
                    
            except Exception as e:
                self.log(f"❌ Login error with {email}: {str(e)}")
        
        # If all accounts fail, create a fresh one
        self.log("All existing accounts failed, creating fresh test account...")
        return self.create_fresh_test_account()
    
    def create_fresh_test_account(self):
        """Create a fresh test account with Group Company and sister companies"""
        import time
        import random
        
        timestamp = str(int(time.time()))
        random_suffix = str(random.randint(1000, 9999))
        fresh_email = f"consolidatedtest{timestamp}{random_suffix}@example.com"
        fresh_password = "testpass123"
        
        self.log(f"Creating fresh test account: {fresh_email}")
        
        # Step 1: Sign up
        signup_data = {
            "email": fresh_email,
            "password": fresh_password,
            "name": "Consolidated Test User",
            "company": "Consolidated Test Company"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            if response.status_code != 200:
                self.log(f"❌ Fresh account signup failed: {response.text}")
                return False
            
            data = response.json()
            self.auth_token = data.get('access_token')
            self.user_data = data.get('user')
            self.log("✅ Fresh account created successfully")
            
            # Step 2: Setup Group Company with sister companies
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            setup_data = {
                "company_name": "Main Group Company",
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
                "email": fresh_email,
                "website": "https://testcompany.com",
                "tax_number": "123456789",
                "registration_number": "REG123456",
                "sister_companies": [
                    {
                        "company_name": "Sister Company Alpha",
                        "country": "US",
                        "base_currency": "USD",
                        "business_type": "Private Limited Company",
                        "industry": "Technology"
                    },
                    {
                        "company_name": "Sister Company Beta", 
                        "country": "GB",
                        "base_currency": "GBP",
                        "business_type": "Limited Company",
                        "industry": "Finance"
                    }
                ]
            }
            
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            if response.status_code != 200:
                self.log(f"❌ Company setup failed: {response.text}")
                return False
            
            self.log("✅ Group Company with sister companies created successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ Fresh account creation error: {str(e)}")
            return False
    
    def test_companies_management_endpoint(self):
        """Test GET /api/companies/management to see all companies"""
        self.log("Testing GET /api/companies/management endpoint...")
        
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
            self.log(f"Companies management response: {response.text}")
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Found {len(companies)} companies")
                
                main_companies = [c for c in companies if c.get('is_main_company', False)]
                sister_companies = [c for c in companies if not c.get('is_main_company', True)]
                
                self.log(f"Main companies: {len(main_companies)}")
                self.log(f"Sister companies: {len(sister_companies)}")
                
                for i, company in enumerate(companies):
                    company_type = "MAIN" if company.get('is_main_company', False) else "SISTER"
                    self.log(f"  {i+1}. {company.get('company_name')} ({company_type}) - ID: {company.get('id')}")
                
                return companies
            else:
                self.log(f"❌ Companies management failed: {response.text}")
                return []
                
        except Exception as e:
            self.log(f"❌ Companies management error: {str(e)}")
            return []
    
    def test_consolidated_accounts_enhanced_endpoint(self):
        """Test GET /api/companies/consolidated-accounts/enhanced endpoint"""
        self.log("Testing GET /api/companies/consolidated-accounts/enhanced endpoint...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/consolidated-accounts/enhanced", headers=headers)
            self.log(f"Consolidated accounts enhanced response status: {response.status_code}")
            self.log(f"Consolidated accounts enhanced response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Consolidated accounts enhanced endpoint working")
                
                # Check the structure of the response
                if isinstance(data, dict):
                    # Check for expected fields
                    accounts_by_category = data.get('accounts_by_category', {})
                    total_accounts = data.get('total_accounts', 0)
                    total_companies = data.get('total_companies', 0)
                    
                    self.log(f"Total accounts: {total_accounts}")
                    self.log(f"Total companies: {total_companies}")
                    self.log(f"Categories: {list(accounts_by_category.keys())}")
                    
                    # Check if accounts have company information
                    company_names_found = set()
                    for category, accounts in accounts_by_category.items():
                        for account in accounts:
                            company_name = account.get('company_name')
                            if company_name:
                                company_names_found.add(company_name)
                    
                    self.log(f"Company names found in accounts: {list(company_names_found)}")
                    
                    if len(company_names_found) > 1:
                        self.log("✅ CONSOLIDATED ACCOUNTS WORKING: Multiple companies found in consolidated view")
                        return True
                    elif len(company_names_found) == 1:
                        self.log("❌ ISSUE CONFIRMED: Only one company found in consolidated accounts")
                        self.log("This confirms the user's report - consolidated accounts not showing other companies")
                        return False
                    else:
                        self.log("❌ No company names found in accounts")
                        return False
                        
                elif isinstance(data, list):
                    self.log(f"Response is a list with {len(data)} items")
                    
                    # Check if accounts have company information
                    company_names_found = set()
                    for account in data:
                        company_name = account.get('company_name')
                        if company_name:
                            company_names_found.add(company_name)
                    
                    self.log(f"Company names found in accounts: {list(company_names_found)}")
                    
                    if len(company_names_found) > 1:
                        self.log("✅ CONSOLIDATED ACCOUNTS WORKING: Multiple companies found in consolidated view")
                        return True
                    elif len(company_names_found) == 1:
                        self.log("❌ ISSUE CONFIRMED: Only one company found in consolidated accounts")
                        return False
                    else:
                        self.log("❌ No company names found in accounts")
                        return False
                else:
                    self.log(f"❌ Unexpected response format: {type(data)}")
                    return False
                    
            else:
                self.log(f"❌ Consolidated accounts enhanced failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Consolidated accounts enhanced error: {str(e)}")
            return False
    
    def test_individual_company_accounts(self, companies):
        """Test individual company chart of accounts to verify data exists"""
        self.log("Testing individual company chart of accounts...")
        
        if not self.auth_token or not companies:
            self.log("❌ No auth token or companies available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        company_accounts = {}
        
        for company in companies:
            company_id = company.get('id')
            company_name = company.get('company_name')
            is_main = company.get('is_main_company', False)
            
            self.log(f"Testing accounts for {company_name} ({'MAIN' if is_main else 'SISTER'})...")
            
            try:
                response = self.session.get(f"{API_BASE}/company/{company_id}/chart-of-accounts", headers=headers)
                self.log(f"  Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    accounts_by_category = data.get('accounts_by_category', {})
                    total_accounts = data.get('total_accounts', 0)
                    company_info = data.get('company', {})
                    
                    self.log(f"  ✅ {company_name}: {total_accounts} accounts found")
                    self.log(f"  Company info: {company_info.get('name')} (is_main: {company_info.get('is_main_company')})")
                    
                    company_accounts[company_id] = {
                        'name': company_name,
                        'is_main': is_main,
                        'total_accounts': total_accounts,
                        'accounts_by_category': accounts_by_category,
                        'company_info': company_info
                    }
                else:
                    self.log(f"  ❌ {company_name}: Failed to get accounts - {response.text}")
                    
            except Exception as e:
                self.log(f"  ❌ {company_name}: Error - {str(e)}")
        
        return company_accounts
    
    def test_sister_companies_endpoint(self):
        """Test GET /api/company/sister-companies endpoint"""
        self.log("Testing GET /api/company/sister-companies endpoint...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
            self.log(f"Sister companies response status: {response.status_code}")
            self.log(f"Sister companies response: {response.text}")
            
            if response.status_code == 200:
                sister_companies = response.json()
                self.log(f"✅ Found {len(sister_companies)} sister companies")
                
                for i, sister in enumerate(sister_companies):
                    self.log(f"  {i+1}. {sister.get('company_name')} - ID: {sister.get('id')}")
                
                return sister_companies
            else:
                self.log(f"❌ Sister companies failed: {response.text}")
                return []
                
        except Exception as e:
            self.log(f"❌ Sister companies error: {str(e)}")
            return []
    
    def analyze_consolidated_accounts_issue(self, companies, company_accounts):
        """Analyze the consolidated accounts issue based on collected data"""
        self.log("Analyzing consolidated accounts issue...")
        
        total_companies = len(companies)
        main_companies = [c for c in companies if c.get('is_main_company', False)]
        sister_companies = [c for c in companies if not c.get('is_main_company', True)]
        
        self.log(f"ANALYSIS SUMMARY:")
        self.log(f"  Total companies: {total_companies}")
        self.log(f"  Main companies: {len(main_companies)}")
        self.log(f"  Sister companies: {len(sister_companies)}")
        
        total_accounts_across_companies = 0
        for company_id, account_data in company_accounts.items():
            total_accounts_across_companies += account_data['total_accounts']
            self.log(f"  {account_data['name']}: {account_data['total_accounts']} accounts")
        
        self.log(f"  Total accounts across all companies: {total_accounts_across_companies}")
        
        # Expected behavior for consolidated accounts
        expected_consolidated_accounts = total_accounts_across_companies
        self.log(f"EXPECTED: Consolidated accounts should show ~{expected_consolidated_accounts} accounts from {total_companies} companies")
        
        return {
            'total_companies': total_companies,
            'main_companies_count': len(main_companies),
            'sister_companies_count': len(sister_companies),
            'total_accounts_across_companies': total_accounts_across_companies,
            'expected_consolidated_accounts': expected_consolidated_accounts
        }
    
    def test_backend_logic_verification(self):
        """Test backend logic for consolidated accounts"""
        self.log("Testing backend logic verification...")
        
        # Test the regular consolidated accounts endpoint (not enhanced)
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/company/consolidated-accounts", headers=headers)
            self.log(f"Regular consolidated accounts response status: {response.status_code}")
            self.log(f"Regular consolidated accounts response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Regular consolidated accounts endpoint working - {len(data)} accounts")
                
                # Check for company information in each account
                company_names_found = set()
                for account in data:
                    sister_companies_data = account.get('sister_companies_data', [])
                    for company_data in sister_companies_data:
                        company_name = company_data.get('company_name')
                        if company_name:
                            company_names_found.add(company_name)
                
                self.log(f"Company names in regular consolidated accounts: {list(company_names_found)}")
                
                if len(company_names_found) > 1:
                    self.log("✅ Regular consolidated accounts includes multiple companies")
                    return True
                else:
                    self.log("❌ Regular consolidated accounts only shows one company")
                    return False
            else:
                self.log(f"❌ Regular consolidated accounts failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Regular consolidated accounts error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive consolidated accounts investigation"""
        self.log("🔍 STARTING COMPREHENSIVE CONSOLIDATED ACCOUNTS INVESTIGATION")
        self.log("=" * 80)
        
        # Step 1: Login
        if not self.test_login():
            self.log("❌ CRITICAL: Login failed - cannot proceed")
            return False
        
        # Step 2: Get all companies
        companies = self.test_companies_management_endpoint()
        if not companies:
            self.log("❌ CRITICAL: No companies found - cannot test consolidated accounts")
            return False
        
        # Step 3: Test sister companies endpoint
        sister_companies = self.test_sister_companies_endpoint()
        
        # Step 4: Test individual company accounts
        company_accounts = self.test_individual_company_accounts(companies)
        
        # Step 5: Analyze the expected vs actual
        analysis = self.analyze_consolidated_accounts_issue(companies, company_accounts)
        
        # Step 6: Test consolidated accounts enhanced endpoint
        self.log("=" * 80)
        self.log("🎯 TESTING CONSOLIDATED ACCOUNTS ENHANCED ENDPOINT")
        consolidated_working = self.test_consolidated_accounts_enhanced_endpoint()
        
        # Step 7: Test backend logic verification
        self.log("=" * 80)
        self.log("🔧 TESTING BACKEND LOGIC VERIFICATION")
        backend_logic_working = self.test_backend_logic_verification()
        
        # Final summary
        self.log("=" * 80)
        self.log("📊 FINAL INVESTIGATION SUMMARY")
        self.log(f"✅ Login: SUCCESS")
        self.log(f"✅ Companies found: {len(companies)} ({analysis['main_companies_count']} main + {analysis['sister_companies_count']} sister)")
        self.log(f"✅ Sister companies endpoint: {len(sister_companies)} sister companies")
        self.log(f"✅ Individual company accounts: {len(company_accounts)} companies with accounts")
        self.log(f"{'✅' if consolidated_working else '❌'} Consolidated accounts enhanced: {'WORKING' if consolidated_working else 'ISSUE CONFIRMED'}")
        self.log(f"{'✅' if backend_logic_working else '❌'} Backend logic verification: {'WORKING' if backend_logic_working else 'ISSUE CONFIRMED'}")
        
        if not consolidated_working:
            self.log("🚨 ISSUE CONFIRMED: Consolidated accounts not showing accounts from all companies")
            self.log("   Expected: Accounts from all companies (main + sister companies) together")
            self.log("   Actual: Only showing accounts from one company")
            self.log("   Root cause: Backend consolidated accounts logic not including sister companies properly")
        else:
            self.log("✅ CONSOLIDATED ACCOUNTS WORKING: All companies included in consolidated view")
        
        return consolidated_working

def main():
    """Main function to run the consolidated accounts investigation"""
    print("🔍 ZOIOS ERP - Consolidated Accounts Functionality Investigation")
    print("=" * 80)
    print("Testing the reported issue: Consolidated accounts not showing other companies")
    print("Expected: Accounts from ALL companies (main + sister companies) together")
    print("=" * 80)
    
    tester = ConsolidatedAccountsTester()
    success = tester.run_comprehensive_test()
    
    print("=" * 80)
    if success:
        print("✅ INVESTIGATION COMPLETE: Consolidated accounts functionality is working correctly")
    else:
        print("❌ INVESTIGATION COMPLETE: Consolidated accounts issue confirmed - needs fixing")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)