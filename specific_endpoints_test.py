#!/usr/bin/env python3
"""
ZOIOS ERP Backend API Specific Endpoints Testing Script
Tests the specific API endpoints reported as not working by the user:

1. Enable Sister Companies functionality - PUT /api/setup/company/convert-to-group
2. Chart of Accounts functionality - GET /api/companies/{company_id}/chart-of-accounts  
3. Consolidated Accounts functionality - GET /api/companies/consolidated-accounts/enhanced
4. Export functionality - GET /api/companies/consolidated-accounts/export

This script will provide detailed testing results for these specific endpoints.
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

# Test credentials - create fresh account for testing
timestamp = str(int(time.time()))
TEST_EMAIL = f"endpointtest{timestamp}@example.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "Endpoint Test User"
TEST_COMPANY = "Endpoint Test Company"

class SpecificEndpointsTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.company_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_signup_and_login(self):
        """Create fresh test account and login"""
        self.log("Creating fresh test account...")
        
        # First try to signup
        signup_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "company": TEST_COMPANY
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            self.log(f"Signup response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log("✅ Signup and login successful")
                self.log(f"User ID: {self.user_data.get('id')}")
                self.log(f"Email: {self.user_data.get('email')}")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                self.log("⚠️ User already exists, trying login...")
                return self.test_login()
            else:
                self.log(f"❌ Signup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Signup error: {str(e)}")
            return False
    
    def test_login(self):
        """Login with test account"""
        self.log("Testing login...")
        
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            self.log(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log("✅ Login successful")
                self.log(f"User ID: {self.user_data.get('id')}")
                self.log(f"Email: {self.user_data.get('email')}")
                return True
            else:
                self.log(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}")
            return False
    
    def get_company_setup(self):
        """Get company setup to find company ID"""
        self.log("Getting company setup...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            self.log(f"Company setup response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.company_id = data.get('id')
                self.log(f"✅ Company setup found - ID: {self.company_id}")
                self.log(f"Company name: {data.get('company_name')}")
                self.log(f"Business type: {data.get('business_type')}")
                return True
            else:
                self.log(f"❌ Company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company setup error: {str(e)}")
            return False

    def test_enable_sister_companies_endpoint(self):
        """Test PUT /api/setup/company/convert-to-group endpoint"""
        self.log("=" * 60)
        self.log("TESTING: Enable Sister Companies Functionality")
        self.log("Endpoint: PUT /api/setup/company/convert-to-group")
        self.log("=" * 60)
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/setup/company/convert-to-group", headers=headers)
            self.log(f"Convert to Group response status: {response.status_code}")
            self.log(f"Convert to Group response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ ENABLE SISTER COMPANIES ENDPOINT WORKING")
                self.log(f"Success: {data.get('success')}")
                self.log(f"Message: {data.get('message')}")
                self.log(f"Business Type: {data.get('business_type')}")
                
                # Verify the conversion was saved
                if data.get('success') and data.get('business_type') == 'Group Company':
                    self.log("✅ Company successfully converted to Group Company")
                    return True
                else:
                    self.log("❌ Conversion response indicates failure")
                    return False
            else:
                self.log(f"❌ ENABLE SISTER COMPANIES ENDPOINT FAILED: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Enable Sister Companies endpoint error: {str(e)}")
            return False

    def test_chart_of_accounts_endpoint(self):
        """Test GET /api/companies/{company_id}/chart-of-accounts endpoint"""
        self.log("=" * 60)
        self.log("TESTING: Chart of Accounts Functionality")
        self.log(f"Endpoint: GET /api/companies/{self.company_id}/chart-of-accounts")
        self.log("=" * 60)
        
        if not self.auth_token or not self.company_id:
            self.log("❌ No auth token or company ID available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/{self.company_id}/chart-of-accounts", headers=headers)
            self.log(f"Chart of Accounts response status: {response.status_code}")
            self.log(f"Chart of Accounts response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ CHART OF ACCOUNTS ENDPOINT WORKING")
                
                # Check response structure
                company_info = data.get('company')
                accounts_by_category = data.get('accounts_by_category')
                total_accounts = data.get('total_accounts')
                
                if company_info:
                    self.log(f"✅ Company info: {company_info.get('name')} (ID: {company_info.get('id')})")
                    self.log(f"✅ Business type: {company_info.get('business_type')}")
                    self.log(f"✅ Is main company: {company_info.get('is_main_company')}")
                
                if accounts_by_category:
                    self.log(f"✅ Accounts by category: {len(accounts_by_category)} categories")
                    for category, accounts in accounts_by_category.items():
                        self.log(f"   - {category}: {len(accounts)} accounts")
                
                if total_accounts is not None:
                    self.log(f"✅ Total accounts: {total_accounts}")
                
                return True
            else:
                self.log(f"❌ CHART OF ACCOUNTS ENDPOINT FAILED: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Chart of Accounts endpoint error: {str(e)}")
            return False

    def test_consolidated_accounts_endpoint(self):
        """Test GET /api/companies/consolidated-accounts/enhanced endpoint"""
        self.log("=" * 60)
        self.log("TESTING: Consolidated Accounts Functionality")
        self.log("Endpoint: GET /api/companies/consolidated-accounts/enhanced")
        self.log("=" * 60)
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/consolidated-accounts/enhanced", headers=headers)
            self.log(f"Consolidated Accounts response status: {response.status_code}")
            self.log(f"Consolidated Accounts response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ CONSOLIDATED ACCOUNTS ENDPOINT WORKING")
                
                # Check response structure
                companies = data.get('companies', [])
                consolidated_accounts = data.get('consolidated_accounts', [])
                grouped_accounts = data.get('grouped_accounts', {})
                total_accounts = data.get('total_accounts', 0)
                
                self.log(f"✅ Companies found: {len(companies)}")
                for company in companies:
                    self.log(f"   - {company.get('company_name')} (ID: {company.get('id')})")
                
                self.log(f"✅ Consolidated accounts: {len(consolidated_accounts)}")
                self.log(f"✅ Grouped accounts: {len(grouped_accounts)} account types")
                for account_type, accounts in grouped_accounts.items():
                    self.log(f"   - {account_type}: {len(accounts)} accounts")
                
                self.log(f"✅ Total accounts: {total_accounts}")
                
                # Verify data includes sister companies
                if len(companies) > 1:
                    self.log("✅ Multiple companies found - includes sister companies")
                else:
                    self.log("⚠️ Only one company found - may not include sister companies")
                
                return True
            else:
                self.log(f"❌ CONSOLIDATED ACCOUNTS ENDPOINT FAILED: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Consolidated Accounts endpoint error: {str(e)}")
            return False

    def test_export_functionality(self):
        """Test POST /api/companies/consolidated-accounts/export endpoint"""
        self.log("=" * 60)
        self.log("TESTING: Export Functionality")
        self.log("Endpoint: POST /api/companies/consolidated-accounts/export")
        self.log("=" * 60)
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test both PDF and Excel export formats
        export_formats = ["pdf", "excel"]
        all_passed = True
        
        for export_format in export_formats:
            self.log(f"Testing {export_format.upper()} export...")
            
            export_data = {
                "format": export_format,
                "filters": {}
            }
            
            try:
                response = self.session.post(f"{API_BASE}/companies/consolidated-accounts/export", 
                                           json=export_data, headers=headers)
                self.log(f"{export_format.upper()} export response status: {response.status_code}")
                self.log(f"{export_format.upper()} export response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ {export_format.upper()} EXPORT WORKING")
                    
                    # Check response structure
                    success = data.get('success')
                    format_returned = data.get('format')
                    filename = data.get('filename')
                    export_data_returned = data.get('data')
                    
                    if success:
                        self.log(f"✅ Export success: {success}")
                    if format_returned:
                        self.log(f"✅ Format: {format_returned}")
                    if filename:
                        self.log(f"✅ Filename: {filename}")
                    if export_data_returned:
                        self.log(f"✅ Export data structure present")
                        if isinstance(export_data_returned, dict):
                            self.log(f"   - Title: {export_data_returned.get('title')}")
                            self.log(f"   - Companies: {export_data_returned.get('total_companies', 0)}")
                            self.log(f"   - Accounts: {export_data_returned.get('total_accounts', 0)}")
                    
                else:
                    self.log(f"❌ {export_format.upper()} EXPORT FAILED: {response.text}")
                    all_passed = False
                    
            except Exception as e:
                self.log(f"❌ {export_format.upper()} export error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_sister_companies_list(self):
        """Test GET /api/company/sister-companies endpoint to verify sister companies exist"""
        self.log("=" * 60)
        self.log("ADDITIONAL TEST: Sister Companies List")
        self.log("Endpoint: GET /api/company/sister-companies")
        self.log("=" * 60)
        
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
                data = response.json()
                self.log(f"✅ Sister companies endpoint working - found {len(data)} sister companies")
                
                for i, sister in enumerate(data):
                    self.log(f"   Sister {i+1}: {sister.get('company_name')} (ID: {sister.get('id')})")
                    self.log(f"      Business Type: {sister.get('business_type')}")
                    self.log(f"      Currency: {sister.get('base_currency')}")
                
                return True
            else:
                self.log(f"❌ Sister companies endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister companies endpoint error: {str(e)}")
            return False

    def test_companies_management_endpoint(self):
        """Test GET /api/companies/management endpoint to verify all companies"""
        self.log("=" * 60)
        self.log("ADDITIONAL TEST: Companies Management")
        self.log("Endpoint: GET /api/companies/management")
        self.log("=" * 60)
        
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
                data = response.json()
                self.log(f"✅ Companies management endpoint working - found {len(data)} companies")
                
                main_companies = [c for c in data if c.get('is_main_company')]
                sister_companies = [c for c in data if not c.get('is_main_company')]
                
                self.log(f"   Main companies: {len(main_companies)}")
                self.log(f"   Sister companies: {len(sister_companies)}")
                
                for company in data:
                    company_type = "MAIN" if company.get('is_main_company') else "SISTER"
                    self.log(f"   {company_type}: {company.get('company_name')} (ID: {company.get('id')})")
                    if not company.get('is_main_company'):
                        self.log(f"      Parent ID: {company.get('parent_company_id')}")
                
                return True
            else:
                self.log(f"❌ Companies management endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Companies management endpoint error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all specific endpoint tests"""
        self.log("🚀 Starting Specific Endpoints Testing...")
        self.log(f"Backend URL: {BACKEND_URL}")
        self.log(f"Test Account: {TEST_EMAIL}")
        
        test_results = {}
        
        # Step 1: Signup and Login
        if not self.test_signup_and_login():
            self.log("❌ Signup/Login failed - cannot proceed with tests")
            return False
        
        # Step 2: Setup company with sister companies
        if not self.setup_company_with_sisters():
            self.log("❌ Company setup failed - cannot proceed with tests")
            return False
        
        # Step 3: Get company setup
        if not self.get_company_setup():
            self.log("❌ Company setup retrieval failed - cannot proceed with tests")
            return False
        
        # Step 3: Test specific endpoints
        test_results['enable_sister_companies'] = self.test_enable_sister_companies_endpoint()
        test_results['chart_of_accounts'] = self.test_chart_of_accounts_endpoint()
        test_results['consolidated_accounts'] = self.test_consolidated_accounts_endpoint()
        test_results['export_functionality'] = self.test_export_functionality()
        
        # Additional verification tests
        test_results['sister_companies_list'] = self.test_sister_companies_list()
        test_results['companies_management'] = self.test_companies_management_endpoint()
        
        # Summary
        self.log("=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed_tests += 1
        
        self.log("=" * 60)
        self.log(f"OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            self.log("🎉 ALL TESTS PASSED - All reported endpoints are working correctly!")
            return True
        else:
            self.log(f"⚠️ {total_tests - passed_tests} tests failed - Some endpoints need attention")
            return False

def main():
    """Main function to run the tests"""
    tester = SpecificEndpointsTester()
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()