#!/usr/bin/env python3
"""
ZOIOS ERP Critical Issues Debug Script
Debug the three critical issues reported by the user:

1. Sister Company Display Issue
2. Chart of Accounts Investigation  
3. Consolidated Accounts Investigation
4. Database Content Verification
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

# Admin credentials for testing
ADMIN_EMAIL = "admin@zoios.com"
ADMIN_PASSWORD = "admin123"

class CriticalIssuesDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.company_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def admin_login(self):
        """Login with admin credentials"""
        self.log("Logging in with admin credentials...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            self.log(f"Admin login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log("✅ Admin login successful")
                return True
            else:
                self.log(f"❌ Admin login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Admin login error: {str(e)}")
            return False

    def setup_test_company(self):
        """Setup a test company with sister companies for debugging"""
        self.log("Setting up test company with sister companies...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Check if company setup already exists
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            if response.status_code == 200:
                company_data = response.json()
                self.company_id = company_data.get('id')
                self.log(f"✅ Company setup already exists with ID: {self.company_id}")
                return True
        except:
            pass
        
        # Create company setup with Group Company type to enable sister companies
        setup_data = {
            "company_name": "Debug Test Group Company",
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR", "GBP", "INR"],
            "business_type": "Group Company",  # This enables sister companies
            "industry": "Technology",
            "address": "123 Debug Street",
            "city": "Test City",
            "state": "CA",
            "postal_code": "12345",
            "phone": "+1-555-123-4567",
            "email": ADMIN_EMAIL,
            "website": "https://debugtest.com",
            "tax_number": "DEBUG123456789",
            "registration_number": "DEBUGREG123456",
            "sister_companies": [
                {
                    "company_name": "Debug Sister Company 1",
                    "country": "US",
                    "business_type": "Private Limited Company",
                    "industry": "Technology",
                    "fiscal_year_start": "01-01"
                },
                {
                    "company_name": "Debug Sister Company 2", 
                    "country": "GB",
                    "business_type": "Public Limited Company",
                    "industry": "Finance",
                    "fiscal_year_start": "04-01"
                }
            ]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Company setup response status: {response.status_code}")
            self.log(f"Company setup response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.company_id = data.get('id')
                self.log(f"✅ Test company setup created with ID: {self.company_id}")
                return True
            elif response.status_code == 400 and "already completed" in response.text:
                self.log("✅ Company setup already completed")
                return True
            else:
                self.log(f"❌ Company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company setup error: {str(e)}")
            return False

    def debug_sister_company_display_issue(self):
        """Debug Issue #1: Sister Company Display Issue"""
        self.log("=" * 80)
        self.log("DEBUGGING ISSUE #1: SISTER COMPANY DISPLAY ISSUE")
        self.log("=" * 80)
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Check what companies are returned by GET /api/companies/management
        self.log("🔍 Testing GET /api/companies/management endpoint...")
        try:
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            self.log(f"GET /api/companies/management status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Found {len(companies)} companies")
                
                for i, company in enumerate(companies):
                    self.log(f"Company {i+1}:")
                    self.log(f"  - ID: {company.get('id')}")
                    self.log(f"  - Name: {company.get('company_name')}")
                    self.log(f"  - Business Type: {company.get('business_type')}")
                    self.log(f"  - Country: {company.get('country_code')}")
                    self.log(f"  - Is Main Company: {company.get('is_main_company', 'N/A')}")
                    
                    # Check if this is a Group Company
                    if company.get('business_type') == 'Group Company':
                        self.log(f"  ⭐ This is a Group Company - should have sister companies")
            else:
                self.log(f"❌ GET /api/companies/management failed: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Error testing companies/management: {str(e)}")
        
        # Test 2: Check GET /api/company/sister-companies endpoint
        self.log("\n🔍 Testing GET /api/company/sister-companies endpoint...")
        try:
            response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
            self.log(f"GET /api/company/sister-companies status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                sister_companies = response.json()
                self.log(f"✅ Found {len(sister_companies)} sister companies")
                
                for i, sister in enumerate(sister_companies):
                    self.log(f"Sister Company {i+1}:")
                    self.log(f"  - ID: {sister.get('id')}")
                    self.log(f"  - Name: {sister.get('company_name')}")
                    self.log(f"  - Business Type: {sister.get('business_type')}")
                    self.log(f"  - Country: {sister.get('country_code')}")
                    self.log(f"  - Group Company ID: {sister.get('group_company_id')}")
                    self.log(f"  - Is Active: {sister.get('is_active')}")
            else:
                self.log(f"❌ GET /api/company/sister-companies failed: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Error testing sister-companies: {str(e)}")
        
        # Test 3: Check company list endpoint
        self.log("\n🔍 Testing GET /api/company/list endpoint...")
        try:
            response = self.session.get(f"{API_BASE}/company/list", headers=headers)
            self.log(f"GET /api/company/list status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Company list found {len(companies)} companies")
                
                for i, company in enumerate(companies):
                    self.log(f"Company {i+1}:")
                    self.log(f"  - ID: {company.get('id')}")
                    self.log(f"  - Name: {company.get('name')}")
                    self.log(f"  - Business Type: {company.get('business_type')}")
                    self.log(f"  - Is Main Company: {company.get('is_main_company')}")
            else:
                self.log(f"❌ GET /api/company/list failed: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Error testing company/list: {str(e)}")
        
        return True

    def debug_chart_of_accounts_investigation(self):
        """Debug Issue #2: Chart of Accounts Investigation"""
        self.log("=" * 80)
        self.log("DEBUGGING ISSUE #2: CHART OF ACCOUNTS INVESTIGATION")
        self.log("=" * 80)
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Check basic chart of accounts endpoint
        self.log("🔍 Testing GET /api/setup/chart-of-accounts endpoint...")
        try:
            response = self.session.get(f"{API_BASE}/setup/chart-of-accounts", headers=headers)
            self.log(f"GET /api/setup/chart-of-accounts status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                accounts = response.json()
                self.log(f"✅ Found {len(accounts)} accounts in chart of accounts")
                
                # Show first few accounts to see data structure
                for i, account in enumerate(accounts[:5]):
                    self.log(f"Account {i+1}:")
                    self.log(f"  - ID: {account.get('id')}")
                    self.log(f"  - Code: {account.get('code')}")
                    self.log(f"  - Name: {account.get('name')}")
                    self.log(f"  - Account Type: {account.get('account_type')}")
                    self.log(f"  - Category: {account.get('category')}")
                    self.log(f"  - Company ID: {account.get('company_id')}")
                    
                    # Check for field name variations
                    if 'account_code' in account:
                        self.log(f"  - Account Code (alt): {account.get('account_code')}")
                    if 'account_name' in account:
                        self.log(f"  - Account Name (alt): {account.get('account_name')}")
                        
                if len(accounts) > 5:
                    self.log(f"... and {len(accounts) - 5} more accounts")
            else:
                self.log(f"❌ GET /api/setup/chart-of-accounts failed: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Error testing chart-of-accounts: {str(e)}")
        
        # Test 2: Check enhanced chart of accounts endpoint
        if self.company_id:
            self.log(f"\n🔍 Testing GET /api/companies/{self.company_id}/accounts/enhanced endpoint...")
            try:
                response = self.session.get(f"{API_BASE}/companies/{self.company_id}/accounts/enhanced", headers=headers)
                self.log(f"GET enhanced accounts status: {response.status_code}")
                self.log(f"Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log("✅ Enhanced accounts endpoint working")
                    
                    # Check data structure
                    if 'accounts_by_category' in data:
                        accounts_by_category = data['accounts_by_category']
                        self.log(f"Found {len(accounts_by_category)} account categories:")
                        
                        for category, accounts in accounts_by_category.items():
                            self.log(f"  Category: {category} ({len(accounts)} accounts)")
                            if accounts:
                                sample_account = accounts[0]
                                self.log(f"    Sample account structure:")
                                for key, value in sample_account.items():
                                    self.log(f"      - {key}: {value}")
                    
                    if 'company' in data:
                        company_info = data['company']
                        self.log(f"Company info: {company_info}")
                        
                else:
                    self.log(f"❌ GET enhanced accounts failed: {response.text}")
                    
            except Exception as e:
                self.log(f"❌ Error testing enhanced accounts: {str(e)}")
        
        return True

    def debug_consolidated_accounts_investigation(self):
        """Debug Issue #3: Consolidated Accounts Investigation"""
        self.log("=" * 80)
        self.log("DEBUGGING ISSUE #3: CONSOLIDATED ACCOUNTS INVESTIGATION")
        self.log("=" * 80)
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Check consolidated accounts endpoint
        self.log("🔍 Testing GET /api/companies/consolidated-accounts/enhanced endpoint...")
        try:
            response = self.session.get(f"{API_BASE}/companies/consolidated-accounts/enhanced", headers=headers)
            self.log(f"GET consolidated accounts status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Consolidated accounts endpoint working")
                
                # Check data structure
                if isinstance(data, list):
                    self.log(f"Found {len(data)} consolidated accounts")
                    
                    # Show first few consolidated accounts
                    for i, account in enumerate(data[:3]):
                        self.log(f"Consolidated Account {i+1}:")
                        self.log(f"  - Group Company ID: {account.get('group_company_id')}")
                        self.log(f"  - Account Code: {account.get('account_code')}")
                        self.log(f"  - Account Name: {account.get('account_name')}")
                        self.log(f"  - Account Type: {account.get('account_type')}")
                        self.log(f"  - Category: {account.get('category')}")
                        self.log(f"  - Consolidated Balance: {account.get('consolidated_balance')}")
                        
                        # Check sister companies data
                        sister_data = account.get('sister_companies_data', [])
                        self.log(f"  - Sister Companies Data: {len(sister_data)} entries")
                        for j, sister in enumerate(sister_data):
                            self.log(f"    Sister {j+1}: {sister.get('company_name')} - Balance: {sister.get('balance')}")
                            
                elif isinstance(data, dict):
                    self.log("Consolidated accounts returned as dictionary:")
                    for key, value in data.items():
                        self.log(f"  - {key}: {value}")
                        
            else:
                self.log(f"❌ GET consolidated accounts failed: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Error testing consolidated accounts: {str(e)}")
        
        # Test 2: Check basic consolidated accounts endpoint (without enhanced)
        self.log("\n🔍 Testing GET /api/company/consolidated-accounts endpoint...")
        try:
            response = self.session.get(f"{API_BASE}/company/consolidated-accounts", headers=headers)
            self.log(f"GET basic consolidated accounts status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                accounts = response.json()
                self.log(f"✅ Basic consolidated accounts found: {len(accounts)} accounts")
                
                # Show sample data structure
                if accounts:
                    sample = accounts[0]
                    self.log("Sample consolidated account structure:")
                    for key, value in sample.items():
                        self.log(f"  - {key}: {value}")
            else:
                self.log(f"❌ GET basic consolidated accounts failed: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Error testing basic consolidated accounts: {str(e)}")
        
        return True

    def debug_database_content_verification(self):
        """Debug Issue #4: Database Content Verification"""
        self.log("=" * 80)
        self.log("DEBUGGING ISSUE #4: DATABASE CONTENT VERIFICATION")
        self.log("=" * 80)
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Get tenant information
        self.log("🔍 Testing GET /api/tenant/info endpoint...")
        try:
            response = self.session.get(f"{API_BASE}/tenant/info", headers=headers)
            self.log(f"GET tenant info status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                tenant_info = response.json()
                self.log("✅ Tenant info retrieved:")
                for key, value in tenant_info.items():
                    self.log(f"  - {key}: {value}")
            else:
                self.log(f"❌ GET tenant info failed: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Error testing tenant info: {str(e)}")
        
        # Test 2: Get company setup to see actual data structure
        self.log("\n🔍 Testing GET /api/setup/company endpoint for data structure...")
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            self.log(f"GET company setup status: {response.status_code}")
            
            if response.status_code == 200:
                company_data = response.json()
                self.log("✅ Company setup data structure:")
                for key, value in company_data.items():
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        self.log(f"  - {key}: {value}")
                    elif isinstance(value, list):
                        self.log(f"  - {key}: [{len(value)} items]")
                        if value:
                            self.log(f"    Sample: {value[0] if len(str(value[0])) < 100 else str(value[0])[:100] + '...'}")
                    else:
                        self.log(f"  - {key}: {type(value).__name__}")
            else:
                self.log(f"❌ GET company setup failed: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Error testing company setup: {str(e)}")
        
        # Test 3: Check field name variations in different endpoints
        self.log("\n🔍 Checking field name variations across endpoints...")
        
        # Get chart of accounts and check field names
        try:
            response = self.session.get(f"{API_BASE}/setup/chart-of-accounts", headers=headers)
            if response.status_code == 200:
                accounts = response.json()
                if accounts:
                    sample_account = accounts[0]
                    self.log("Chart of accounts field names:")
                    for field in sample_account.keys():
                        self.log(f"  - {field}")
                        
                    # Check for expected vs actual field names
                    expected_fields = ['account_code', 'account_name', 'code', 'name']
                    found_fields = []
                    for field in expected_fields:
                        if field in sample_account:
                            found_fields.append(field)
                            self.log(f"  ✅ Found field: {field} = {sample_account[field]}")
                        else:
                            self.log(f"  ❌ Missing field: {field}")
                    
                    self.log(f"Field mapping analysis:")
                    self.log(f"  - Frontend expects: account_code, account_name")
                    self.log(f"  - Backend provides: {', '.join(found_fields)}")
                    
                    if 'code' in found_fields and 'account_code' not in found_fields:
                        self.log(f"  🔍 ISSUE FOUND: Backend uses 'code' but frontend expects 'account_code'")
                    if 'name' in found_fields and 'account_name' not in found_fields:
                        self.log(f"  🔍 ISSUE FOUND: Backend uses 'name' but frontend expects 'account_name'")
                        
        except Exception as e:
            self.log(f"❌ Error checking field names: {str(e)}")
        
        return True

    def run_all_debug_tests(self):
        """Run all debug tests"""
        self.log("🚀 Starting Critical Issues Debug Session")
        self.log("=" * 80)
        
        # Login first
        if not self.admin_login():
            self.log("❌ Failed to login - cannot proceed with debugging")
            return False
        
        # Setup test company if needed
        if not self.setup_test_company():
            self.log("❌ Failed to setup test company - some tests may fail")
        
        # Run all debug tests
        tests = [
            ("Sister Company Display Issue", self.debug_sister_company_display_issue),
            ("Chart of Accounts Investigation", self.debug_chart_of_accounts_investigation),
            ("Consolidated Accounts Investigation", self.debug_consolidated_accounts_investigation),
            ("Database Content Verification", self.debug_database_content_verification)
        ]
        
        results = {}
        for test_name, test_func in tests:
            self.log(f"\n🔍 Running: {test_name}")
            try:
                result = test_func()
                results[test_name] = result
                self.log(f"✅ Completed: {test_name}")
            except Exception as e:
                self.log(f"❌ Error in {test_name}: {str(e)}")
                results[test_name] = False
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log("DEBUG SESSION SUMMARY")
        self.log("=" * 80)
        
        for test_name, result in results.items():
            status = "✅ COMPLETED" if result else "❌ FAILED"
            self.log(f"{status}: {test_name}")
        
        self.log("\n🎯 Key Findings:")
        self.log("1. Check the logs above for field name mismatches (code vs account_code, name vs account_name)")
        self.log("2. Verify sister company data structure and relationships")
        self.log("3. Confirm consolidated accounts data format")
        self.log("4. Review database field mappings between frontend and backend")
        
        return True

def main():
    """Main function to run the debug session"""
    debugger = CriticalIssuesDebugger()
    debugger.run_all_debug_tests()

if __name__ == "__main__":
    main()