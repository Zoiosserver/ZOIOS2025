#!/usr/bin/env python3
"""
ZOIOS ERP Critical Fixes Testing Script
Tests the three critical fixes implemented by the main agent:

1. Sister Company Display Fix - GET /api/companies/management endpoint
2. Chart of Accounts Field Mapping Fix - GET /api/companies/{company_id}/accounts/enhanced endpoint  
3. Consolidated Accounts Field Mapping Fix - GET /api/companies/consolidated-accounts/enhanced endpoint
4. Complete Integration Test - End-to-end flow testing
"""

import requests
import json
import os
from datetime import datetime
import sys
import time
import random

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://zoios-erp-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Generate unique test credentials for fresh testing
timestamp = str(int(time.time()))
random_suffix = str(random.randint(1000, 9999))
TEST_EMAIL = f"criticaltest{timestamp}{random_suffix}@example.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "Critical Test User"
TEST_COMPANY = "Critical Test Company Inc"

class CriticalFixesTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.company_id = None
        self.sister_company_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def setup_test_environment(self):
        """Setup test environment with user, company, and sister company"""
        self.log("Setting up test environment...")
        
        # 1. Create test user
        if not self.create_test_user():
            return False
            
        # 2. Setup main company as Group Company
        if not self.setup_group_company():
            return False
            
        # 3. Add sister company
        if not self.add_sister_company():
            return False
            
        self.log("✅ Test environment setup complete")
        return True
        
    def create_test_user(self):
        """Create a test user and authenticate"""
        self.log("Creating test user...")
        
        signup_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "company": TEST_COMPANY
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            self.log(f"User creation response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log(f"✅ Test user created: {TEST_EMAIL}")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                # Try to login instead
                return self.login_test_user()
            else:
                self.log(f"❌ User creation failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ User creation error: {str(e)}")
            return False
    
    def login_test_user(self):
        """Login with test user credentials"""
        self.log("Logging in test user...")
        
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
                self.log(f"✅ Test user logged in: {TEST_EMAIL}")
                return True
            else:
                self.log(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}")
            return False
    
    def setup_group_company(self):
        """Setup main company as Group Company"""
        self.log("Setting up Group Company...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Company setup data for Group Company
        setup_data = {
            "company_name": "Critical Test Group Company",
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR", "GBP"],
            "business_type": "Group Company",  # This is key for sister companies
            "industry": "Technology",
            "address": "123 Group Street",
            "city": "Group City",
            "state": "CA",
            "postal_code": "12345",
            "phone": "+1-555-123-4567",
            "email": TEST_EMAIL,
            "website": "https://criticaltest.com",
            "tax_number": "TAX123456789",
            "registration_number": "REG987654321"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Company setup response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.company_id = data.get('id')
                self.log(f"✅ Group Company setup complete: {self.company_id}")
                return True
            elif response.status_code == 400 and "already completed" in response.text:
                # Get existing company
                return self.get_existing_company()
            else:
                self.log(f"❌ Company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company setup error: {str(e)}")
            return False
    
    def get_existing_company(self):
        """Get existing company setup"""
        self.log("Getting existing company setup...")
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.company_id = data.get('id')
                self.log(f"✅ Found existing company: {self.company_id}")
                return True
            else:
                self.log(f"❌ Could not get existing company: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Get existing company error: {str(e)}")
            return False
    
    def add_sister_company(self):
        """Add a sister company to the group"""
        self.log("Adding sister company...")
        
        if not self.auth_token or not self.company_id:
            self.log("❌ Missing auth token or company ID")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        sister_data = {
            "company_name": "Critical Test Sister Company",
            "country_code": "GB",
            "base_currency": "GBP",
            "business_type": "Private Limited Company",
            "industry": "Technology",
            "fiscal_year_start": "01-04"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/company/sister-companies", json=sister_data, headers=headers)
            self.log(f"Sister company creation response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.sister_company_id = data.get('id')
                self.log(f"✅ Sister company added: {self.sister_company_id}")
                return True
            else:
                self.log(f"❌ Sister company creation failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister company creation error: {str(e)}")
            return False
    
    def test_sister_company_display_fix(self):
        """Test Fix #1: Sister Company Display in /api/companies/management"""
        self.log("🔍 Testing Fix #1: Sister Company Display...")
        
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
                self.log(f"Found {len(companies)} companies in management list")
                
                # Check for main company and sister company
                main_companies = [c for c in companies if c.get('is_main_company') == True]
                sister_companies = [c for c in companies if c.get('is_main_company') == False]
                
                self.log(f"Main companies: {len(main_companies)}")
                self.log(f"Sister companies: {len(sister_companies)}")
                
                # Verify main company properties
                if main_companies:
                    main_company = main_companies[0]
                    self.log(f"Main company: {main_company.get('company_name')}")
                    self.log(f"is_main_company: {main_company.get('is_main_company')}")
                    self.log(f"parent_company_id: {main_company.get('parent_company_id')}")
                    
                    if main_company.get('is_main_company') == True and main_company.get('parent_company_id') is None:
                        self.log("✅ Main company has correct flags")
                    else:
                        self.log("❌ Main company flags incorrect")
                        return False
                else:
                    self.log("❌ No main companies found")
                    return False
                
                # Verify sister company properties
                if sister_companies:
                    sister_company = sister_companies[0]
                    self.log(f"Sister company: {sister_company.get('company_name')}")
                    self.log(f"is_main_company: {sister_company.get('is_main_company')}")
                    self.log(f"parent_company_id: {sister_company.get('parent_company_id')}")
                    
                    if (sister_company.get('is_main_company') == False and 
                        sister_company.get('parent_company_id') is not None):
                        self.log("✅ Sister company has correct flags")
                        self.log("🎉 Fix #1: Sister Company Display - WORKING CORRECTLY")
                        return True
                    else:
                        self.log("❌ Sister company flags incorrect")
                        return False
                else:
                    self.log("❌ No sister companies found in management list")
                    return False
            else:
                self.log(f"❌ Companies management endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister company display test error: {str(e)}")
            return False
    
    def test_chart_of_accounts_field_mapping_fix(self):
        """Test Fix #2: Chart of Accounts Field Mapping"""
        self.log("🔍 Testing Fix #2: Chart of Accounts Field Mapping...")
        
        if not self.auth_token or not self.company_id:
            self.log("❌ Missing auth token or company ID")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/{self.company_id}/accounts/enhanced", headers=headers)
            self.log(f"Enhanced accounts response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('accounts', [])
                self.log(f"Found {len(accounts)} accounts")
                
                if accounts:
                    # Check first few accounts for proper field mapping
                    field_mapping_correct = True
                    
                    for i, account in enumerate(accounts[:5]):  # Check first 5 accounts
                        account_code = account.get('account_code')
                        account_name = account.get('account_name')
                        
                        self.log(f"Account {i+1}: code='{account_code}', name='{account_name}'")
                        
                        # Verify both account_code and account_name fields exist and are not empty
                        if not account_code or not account_name:
                            self.log(f"❌ Account {i+1} missing account_code or account_name")
                            field_mapping_correct = False
                        elif account_code == 'N/A' or account_name == 'N/A':
                            self.log(f"❌ Account {i+1} has N/A values")
                            field_mapping_correct = False
                        else:
                            self.log(f"✅ Account {i+1} has proper field mapping")
                    
                    if field_mapping_correct:
                        self.log("🎉 Fix #2: Chart of Accounts Field Mapping - WORKING CORRECTLY")
                        return True
                    else:
                        self.log("❌ Chart of Accounts field mapping has issues")
                        return False
                else:
                    self.log("❌ No accounts found")
                    return False
            else:
                self.log(f"❌ Enhanced accounts endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Chart of accounts field mapping test error: {str(e)}")
            return False
    
    def test_consolidated_accounts_field_mapping_fix(self):
        """Test Fix #3: Consolidated Accounts Field Mapping"""
        self.log("🔍 Testing Fix #3: Consolidated Accounts Field Mapping...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/consolidated-accounts/enhanced", headers=headers)
            self.log(f"Consolidated accounts response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                consolidated_accounts = data.get('consolidated_accounts', [])
                companies = data.get('companies', [])
                
                self.log(f"Found {len(consolidated_accounts)} consolidated accounts")
                self.log(f"Found {len(companies)} companies in consolidation")
                
                if consolidated_accounts:
                    # Check first few accounts for proper field mapping
                    field_mapping_correct = True
                    
                    for i, account in enumerate(consolidated_accounts[:5]):  # Check first 5 accounts
                        account_code = account.get('account_code')
                        account_name = account.get('account_name')
                        company_name = account.get('company_name')
                        
                        self.log(f"Consolidated Account {i+1}: code='{account_code}', name='{account_name}', company='{company_name}'")
                        
                        # Verify both account_code and account_name fields exist and are not empty
                        if not account_code or not account_name:
                            self.log(f"❌ Consolidated Account {i+1} missing account_code or account_name")
                            field_mapping_correct = False
                        elif account_code == 'N/A' or account_name == 'N/A':
                            self.log(f"❌ Consolidated Account {i+1} has N/A values")
                            field_mapping_correct = False
                        else:
                            self.log(f"✅ Consolidated Account {i+1} has proper field mapping")
                    
                    if field_mapping_correct:
                        self.log("🎉 Fix #3: Consolidated Accounts Field Mapping - WORKING CORRECTLY")
                        return True
                    else:
                        self.log("❌ Consolidated Accounts field mapping has issues")
                        return False
                else:
                    self.log("❌ No consolidated accounts found")
                    return False
            else:
                self.log(f"❌ Consolidated accounts endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Consolidated accounts field mapping test error: {str(e)}")
            return False
    
    def test_complete_integration_flow(self):
        """Test Fix #4: Complete Integration Test"""
        self.log("🔍 Testing Fix #4: Complete Integration Flow...")
        
        # Test the complete flow: company setup → sister companies → accounts → consolidated view
        
        # 1. Verify company setup is complete
        if not self.company_id:
            self.log("❌ Company setup not complete")
            return False
        
        # 2. Verify sister company exists
        if not self.sister_company_id:
            self.log("❌ Sister company not created")
            return False
        
        # 3. Test company management shows both companies
        if not self.test_sister_company_display_fix():
            self.log("❌ Sister company display not working")
            return False
        
        # 4. Test chart of accounts for main company
        if not self.test_chart_of_accounts_field_mapping_fix():
            self.log("❌ Chart of accounts field mapping not working")
            return False
        
        # 5. Test consolidated accounts view
        if not self.test_consolidated_accounts_field_mapping_fix():
            self.log("❌ Consolidated accounts field mapping not working")
            return False
        
        # 6. Test sister company chart of accounts
        if not self.test_sister_company_accounts():
            self.log("❌ Sister company accounts not working")
            return False
        
        self.log("🎉 Fix #4: Complete Integration Flow - ALL TESTS PASSED")
        return True
    
    def test_sister_company_accounts(self):
        """Test chart of accounts for sister company"""
        self.log("Testing sister company chart of accounts...")
        
        if not self.auth_token or not self.sister_company_id:
            self.log("❌ Missing auth token or sister company ID")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/{self.sister_company_id}/accounts/enhanced", headers=headers)
            self.log(f"Sister company accounts response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('accounts', [])
                self.log(f"Sister company has {len(accounts)} accounts")
                
                if accounts:
                    # Check field mapping for sister company accounts
                    first_account = accounts[0]
                    account_code = first_account.get('account_code')
                    account_name = first_account.get('account_name')
                    
                    if account_code and account_name and account_code != 'N/A' and account_name != 'N/A':
                        self.log("✅ Sister company accounts have proper field mapping")
                        return True
                    else:
                        self.log("❌ Sister company accounts have field mapping issues")
                        return False
                else:
                    self.log("❌ Sister company has no accounts")
                    return False
            else:
                self.log(f"❌ Sister company accounts endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister company accounts test error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all critical fixes tests"""
        self.log("🚀 Starting Critical Fixes Testing...")
        self.log("=" * 60)
        
        # Setup test environment
        if not self.setup_test_environment():
            self.log("❌ Test environment setup failed")
            return False
        
        self.log("=" * 60)
        
        # Test results tracking
        test_results = {}
        
        # Test Fix #1: Sister Company Display
        self.log("Testing Fix #1: Sister Company Display...")
        test_results['sister_company_display'] = self.test_sister_company_display_fix()
        self.log("=" * 60)
        
        # Test Fix #2: Chart of Accounts Field Mapping
        self.log("Testing Fix #2: Chart of Accounts Field Mapping...")
        test_results['chart_accounts_mapping'] = self.test_chart_of_accounts_field_mapping_fix()
        self.log("=" * 60)
        
        # Test Fix #3: Consolidated Accounts Field Mapping
        self.log("Testing Fix #3: Consolidated Accounts Field Mapping...")
        test_results['consolidated_accounts_mapping'] = self.test_consolidated_accounts_field_mapping_fix()
        self.log("=" * 60)
        
        # Test Fix #4: Complete Integration
        self.log("Testing Fix #4: Complete Integration Flow...")
        test_results['complete_integration'] = self.test_complete_integration_flow()
        self.log("=" * 60)
        
        # Summary
        self.log("🏁 CRITICAL FIXES TEST SUMMARY")
        self.log("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"{test_name}: {status}")
            if result:
                passed_tests += 1
        
        self.log("=" * 60)
        self.log(f"OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            self.log("🎉 ALL CRITICAL FIXES ARE WORKING CORRECTLY!")
            return True
        else:
            self.log("❌ Some critical fixes need attention")
            return False

def main():
    """Main test execution"""
    tester = CriticalFixesTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All critical fixes tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some critical fixes tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()