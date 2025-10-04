#!/usr/bin/env python3
"""
ZOIOS ERP Backend API Testing Script - Critical ERP Functionality
Tests the specific issues mentioned in the review request:
1. Sister Company Display Issue
2. Company Management API Testing  
3. User Management System
4. Currency Management
5. PDF Generation Issues
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
TEST_EMAIL = f"erptest{timestamp}{random_suffix}@example.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "ERP Test User"
TEST_COMPANY = "ERP Test Company Inc"

class ERPBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.company_id = None
        self.sister_company_ids = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def setup_test_environment(self):
        """Setup test environment with Group Company and sister companies"""
        self.log("Setting up test environment...")
        
        # 1. Create test user
        signup_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "company": TEST_COMPANY
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log("✅ Test user created successfully")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
                login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.auth_token = data.get('access_token')
                    self.user_data = data.get('user')
                    self.log("✅ Logged in with existing test user")
                else:
                    self.log(f"❌ Login failed: {login_response.text}")
                    return False
            else:
                self.log(f"❌ User creation failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Setup error: {str(e)}")
            return False
        
        # 2. Create Group Company with sister companies
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        setup_data = {
            "company_name": "ERP Group Company",
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR", "GBP", "JPY"],
            "business_type": "Group Company",  # This is key for sister companies
            "industry": "Technology",
            "address": "123 ERP Street",
            "city": "Test City",
            "state": "CA",
            "postal_code": "12345",
            "phone": "+1-555-123-4567",
            "email": TEST_EMAIL,
            "website": "https://erptest.com",
            "tax_number": "TAX123456789",
            "registration_number": "REG123456",
            "sister_companies": [
                {
                    "company_name": "Sister Company Alpha",
                    "country": "US",
                    "business_type": "Private Limited Company",
                    "industry": "Manufacturing",
                    "fiscal_year_start": "01-01"
                },
                {
                    "company_name": "Sister Company Beta", 
                    "country": "GB",
                    "business_type": "Partnership",
                    "industry": "Services",
                    "fiscal_year_start": "04-01"
                }
            ]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.company_id = data.get('id')
                self.log(f"✅ Group Company setup successful - ID: {self.company_id}")
                return True
            elif response.status_code == 400 and "already completed" in response.text:
                # Get existing company setup
                get_response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
                if get_response.status_code == 200:
                    data = get_response.json()
                    self.company_id = data.get('id')
                    self.log(f"✅ Using existing company setup - ID: {self.company_id}")
                    return True
                else:
                    self.log("❌ Could not retrieve existing company setup")
                    return False
            else:
                self.log(f"❌ Company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company setup error: {str(e)}")
            return False
    
    def test_sister_company_display_issue(self):
        """Test sister company display issue - Debug the sister company display issue"""
        self.log("🔍 TESTING SISTER COMPANY DISPLAY ISSUE")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Check if sister companies are being saved during company creation
        self.log("Test 1: Checking sister company creation and saving...")
        
        try:
            # Get sister companies via dedicated endpoint
            response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
            self.log(f"GET sister companies response status: {response.status_code}")
            self.log(f"GET sister companies response: {response.text}")
            
            if response.status_code == 200:
                sister_companies = response.json()
                self.log(f"✅ Sister companies endpoint working - found {len(sister_companies)} companies")
                
                if len(sister_companies) >= 2:
                    self.log("✅ Sister companies are being saved correctly")
                    for i, company in enumerate(sister_companies):
                        self.log(f"  Sister Company {i+1}: {company.get('company_name')} (ID: {company.get('id')})")
                        self.sister_company_ids.append(company.get('id'))
                else:
                    self.log("❌ Expected 2 sister companies but found fewer")
                    return False
            else:
                self.log(f"❌ Sister companies endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister companies test error: {str(e)}")
            return False
        
        # Test 2: Check GET /api/companies/management to see what companies are returned
        self.log("Test 2: Checking companies/management endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            self.log(f"GET companies/management response status: {response.status_code}")
            self.log(f"GET companies/management response: {response.text}")
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Companies management endpoint working - found {len(companies)} companies")
                
                # Check for is_main_company flags
                main_companies = [c for c in companies if c.get('is_main_company') == True]
                sister_companies = [c for c in companies if c.get('is_main_company') == False]
                
                self.log(f"Main companies: {len(main_companies)}")
                self.log(f"Sister companies: {len(sister_companies)}")
                
                if len(main_companies) == 1 and len(sister_companies) >= 2:
                    self.log("✅ is_main_company flags are working correctly")
                    
                    # Log details of each company
                    for company in companies:
                        self.log(f"  Company: {company.get('company_name')} - is_main: {company.get('is_main_company')} - ID: {company.get('id')}")
                    
                    return True
                else:
                    self.log(f"❌ Expected 1 main + 2 sister companies, got {len(main_companies)} main + {len(sister_companies)} sister")
                    return False
            else:
                self.log(f"❌ Companies management endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Companies management test error: {str(e)}")
            return False
    
    def test_company_management_api(self):
        """Test Company Management API Testing - View Chart of Accounts button API endpoints"""
        self.log("🔍 TESTING COMPANY MANAGEMENT API")
        
        if not self.auth_token or not self.company_id:
            self.log("❌ No auth token or company ID available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Check GET /api/companies/{company_id}/accounts/enhanced
        self.log("Test 1: Testing enhanced chart of accounts endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/companies/{self.company_id}/accounts/enhanced", headers=headers)
            self.log(f"GET enhanced accounts response status: {response.status_code}")
            self.log(f"GET enhanced accounts response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Enhanced chart of accounts endpoint working")
                
                # Check response structure
                if 'accounts_by_category' in data:
                    accounts_by_category = data['accounts_by_category']
                    total_accounts = sum(len(accounts) for accounts in accounts_by_category.values())
                    self.log(f"✅ Found {total_accounts} accounts grouped by {len(accounts_by_category)} categories")
                    
                    # Log categories
                    for category, accounts in accounts_by_category.items():
                        self.log(f"  Category '{category}': {len(accounts)} accounts")
                else:
                    self.log("❌ Response missing accounts_by_category structure")
                    return False
            else:
                self.log(f"❌ Enhanced accounts endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Enhanced accounts test error: {str(e)}")
            return False
        
        # Test 2: Test company details retrieval for editing
        self.log("Test 2: Testing company details retrieval...")
        
        try:
            response = self.session.get(f"{API_BASE}/companies/management/{self.company_id}", headers=headers)
            self.log(f"GET company details response status: {response.status_code}")
            self.log(f"GET company details response: {response.text}")
            
            if response.status_code == 200:
                company_details = response.json()
                self.log("✅ Company details retrieval working")
                
                # Check key fields for editing
                required_fields = ['company_name', 'business_type', 'country_code', 'base_currency']
                missing_fields = [field for field in required_fields if field not in company_details]
                
                if not missing_fields:
                    self.log("✅ All required fields present for editing")
                    return True
                else:
                    self.log(f"❌ Missing required fields: {missing_fields}")
                    return False
            else:
                self.log(f"❌ Company details retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company details test error: {str(e)}")
            return False
    
    def test_user_management_system(self):
        """Test User Management System - user creation, role assignment, permissions"""
        self.log("🔍 TESTING USER MANAGEMENT SYSTEM")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Check if user creation API exists
        self.log("Test 1: Testing user creation API...")
        
        try:
            # Test user creation (admin-only endpoint)
            new_user_data = {
                "email": f"newuser{timestamp}@example.com",
                "password": "newuserpass123",
                "name": "New Test User",
                "company": "Test Company",
                "role": "user"
            }
            
            response = self.session.post(f"{API_BASE}/auth/register", json=new_user_data, headers=headers)
            self.log(f"User creation response status: {response.status_code}")
            self.log(f"User creation response: {response.text}")
            
            if response.status_code == 200:
                self.log("✅ User creation API working")
                created_user = response.json().get('user', {})
                new_user_id = created_user.get('id')
            elif response.status_code == 403:
                self.log("⚠️ User creation requires admin role - this is expected behavior")
                new_user_id = self.user_data.get('id')  # Use current user for testing
            else:
                self.log(f"❌ User creation failed: {response.text}")
                new_user_id = self.user_data.get('id')  # Fallback to current user
                
        except Exception as e:
            self.log(f"❌ User creation test error: {str(e)}")
            new_user_id = self.user_data.get('id')
        
        # Test 2: Check role assignment APIs
        self.log("Test 2: Testing role assignment API...")
        
        try:
            role_data = {"role": "admin"}
            response = self.session.post(f"{API_BASE}/users/{new_user_id}/role", json=role_data, headers=headers)
            self.log(f"Role assignment response status: {response.status_code}")
            self.log(f"Role assignment response: {response.text}")
            
            if response.status_code == 200:
                self.log("✅ Role assignment API working")
            else:
                self.log(f"❌ Role assignment failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Role assignment test error: {str(e)}")
            return False
        
        # Test 3: Check permission system
        self.log("Test 3: Testing permission system...")
        
        try:
            permissions_data = {
                "permissions": {
                    "dashboard": True,
                    "crm_contacts": True,
                    "crm_companies": False,
                    "currency_management": True,
                    "user_management": False,
                    "company_accounts": True
                }
            }
            
            response = self.session.post(f"{API_BASE}/users/{new_user_id}/permissions", 
                                       json=permissions_data, headers=headers)
            self.log(f"Permissions update response status: {response.status_code}")
            self.log(f"Permissions update response: {response.text}")
            
            if response.status_code == 200:
                self.log("✅ Permission system API working")
                
                # Verify permissions via /auth/me
                auth_response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
                if auth_response.status_code == 200:
                    auth_data = auth_response.json()
                    if 'permissions' in auth_data:
                        self.log("✅ Permissions properly returned in /auth/me")
                        return True
                    else:
                        self.log("❌ Permissions not found in /auth/me response")
                        return False
                else:
                    self.log("❌ Could not verify permissions via /auth/me")
                    return False
            else:
                self.log(f"❌ Permission system failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Permission system test error: {str(e)}")
            return False
    
    def test_currency_management(self):
        """Test Currency Management - base and additional currencies, exchange rates, manual setting"""
        self.log("🔍 TESTING CURRENCY MANAGEMENT")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Check if currency endpoints return base and additional currencies
        self.log("Test 1: Testing currency rates endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/currency/rates", headers=headers)
            self.log(f"Currency rates response status: {response.status_code}")
            self.log(f"Currency rates response: {response.text}")
            
            if response.status_code == 200:
                rates = response.json()
                self.log(f"✅ Currency rates endpoint working - found {len(rates)} rates")
                
                # Check for expected currencies (EUR, GBP, JPY from setup)
                currencies = [rate.get('target_currency') for rate in rates]
                expected_currencies = ['EUR', 'GBP', 'JPY']
                found_currencies = [curr for curr in expected_currencies if curr in currencies]
                
                self.log(f"Expected currencies found: {found_currencies}")
                
                if len(found_currencies) >= 2:
                    self.log("✅ Additional currencies are properly configured")
                else:
                    self.log("⚠️ Some additional currencies missing, but endpoint works")
            else:
                self.log(f"❌ Currency rates endpoint failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Currency rates test error: {str(e)}")
            return False
        
        # Test 2: Check exchange rate functionality
        self.log("Test 2: Testing exchange rate update functionality...")
        
        try:
            response = self.session.post(f"{API_BASE}/currency/update-rates", headers=headers)
            self.log(f"Exchange rate update response status: {response.status_code}")
            self.log(f"Exchange rate update response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Exchange rate update endpoint working")
                
                # Check for proper response format (testing the undefined fix)
                if 'updated_rates' in data and data['updated_rates'] is not None:
                    self.log("✅ Exchange rate response format correct (no undefined)")
                    self.log(f"Updated rates: {data.get('updated_rates')}")
                    self.log(f"Base currency: {data.get('base_currency')}")
                    self.log(f"Target currencies: {data.get('target_currencies')}")
                else:
                    self.log("❌ Exchange rate response format incorrect")
                    return False
            else:
                self.log(f"❌ Exchange rate update failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Exchange rate update test error: {str(e)}")
            return False
        
        # Test 3: Verify manual exchange rate setting
        self.log("Test 3: Testing manual exchange rate setting...")
        
        try:
            manual_rate_data = {
                "base_currency": "USD",
                "target_currency": "EUR",
                "rate": 0.85
            }
            
            response = self.session.post(f"{API_BASE}/currency/set-manual-rate", 
                                       json=manual_rate_data, headers=headers)
            self.log(f"Manual rate setting response status: {response.status_code}")
            self.log(f"Manual rate setting response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Manual exchange rate setting working")
                
                if data.get('rate') == 0.85 and data.get('source') == 'manual':
                    self.log("✅ Manual rate correctly set and returned")
                    return True
                else:
                    self.log("❌ Manual rate data incorrect")
                    return False
            else:
                self.log(f"❌ Manual rate setting failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Manual rate setting test error: {str(e)}")
            return False
    
    def test_pdf_generation_issues(self):
        """Test PDF Generation Issues - PDF export endpoints, structured data, format validation"""
        self.log("🔍 TESTING PDF GENERATION ISSUES")
        
        if not self.auth_token or not self.company_id:
            self.log("❌ No auth token or company ID available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Test PDF export endpoints for individual company
        self.log("Test 1: Testing individual company PDF export...")
        
        try:
            export_data = {
                "format": "pdf",
                "filters": {}
            }
            
            response = self.session.post(f"{API_BASE}/companies/{self.company_id}/accounts/export", 
                                       json=export_data, headers=headers)
            self.log(f"Individual PDF export response status: {response.status_code}")
            self.log(f"Individual PDF export response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Individual company PDF export endpoint working")
                
                # Check if structured data is being returned correctly
                required_fields = ['export_data', 'company_info', 'filename']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log("✅ PDF export returns structured data correctly")
                else:
                    self.log(f"⚠️ Some fields missing from PDF export: {missing_fields}")
                    
            else:
                self.log(f"❌ Individual PDF export failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Individual PDF export test error: {str(e)}")
            return False
        
        # Test 2: Test consolidated PDF export
        self.log("Test 2: Testing consolidated PDF export...")
        
        try:
            export_data = {
                "format": "pdf",
                "company_ids": [self.company_id] + self.sister_company_ids[:2],  # Include main + sister companies
                "filters": {}
            }
            
            response = self.session.post(f"{API_BASE}/companies/consolidated-accounts/export", 
                                       json=export_data, headers=headers)
            self.log(f"Consolidated PDF export response status: {response.status_code}")
            self.log(f"Consolidated PDF export response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Consolidated PDF export endpoint working")
                
                # Check consolidated export structure
                if 'export_data' in data and 'companies' in data:
                    companies_count = len(data.get('companies', []))
                    self.log(f"✅ Consolidated export includes {companies_count} companies")
                else:
                    self.log("❌ Consolidated export missing expected structure")
                    return False
                    
            else:
                self.log(f"❌ Consolidated PDF export failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Consolidated PDF export test error: {str(e)}")
            return False
        
        # Test 3: Verify export format validation
        self.log("Test 3: Testing export format validation...")
        
        try:
            # Test invalid format
            invalid_export_data = {
                "format": "invalid_format",
                "filters": {}
            }
            
            response = self.session.post(f"{API_BASE}/companies/{self.company_id}/accounts/export", 
                                       json=invalid_export_data, headers=headers)
            self.log(f"Invalid format export response status: {response.status_code}")
            
            if response.status_code == 400:
                self.log("✅ Export format validation working (correctly rejects invalid format)")
                return True
            else:
                self.log(f"❌ Export format validation not working: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Export format validation test error: {str(e)}")
            return False
    
    def test_comprehensive_scenarios(self):
        """Test the comprehensive scenarios mentioned in the review request"""
        self.log("🔍 TESTING COMPREHENSIVE SCENARIOS")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Scenario 1: Create a Group Company with 2 sister companies (already done in setup)
        self.log("Scenario 1: Group Company with sister companies - ✅ COMPLETED IN SETUP")
        
        # Scenario 2: Login and check if all 3 companies appear in company management
        self.log("Scenario 2: Checking if all companies appear in management...")
        
        try:
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            if response.status_code == 200:
                companies = response.json()
                total_companies = len(companies)
                main_companies = len([c for c in companies if c.get('is_main_company') == True])
                sister_companies = len([c for c in companies if c.get('is_main_company') == False])
                
                self.log(f"Total companies found: {total_companies}")
                self.log(f"Main companies: {main_companies}")
                self.log(f"Sister companies: {sister_companies}")
                
                if total_companies >= 3 and main_companies == 1 and sister_companies >= 2:
                    self.log("✅ Scenario 2: All companies appear correctly")
                else:
                    self.log("❌ Scenario 2: Not all companies appearing")
                    return False
            else:
                self.log(f"❌ Scenario 2 failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Scenario 2 error: {str(e)}")
            return False
        
        # Scenario 3: Test editing company details
        self.log("Scenario 3: Testing company details editing...")
        
        try:
            update_data = {
                "company_name": "Updated ERP Group Company",
                "phone": "+1-555-999-8888"
            }
            
            response = self.session.put(f"{API_BASE}/companies/management/{self.company_id}", 
                                      json=update_data, headers=headers)
            if response.status_code == 200:
                self.log("✅ Scenario 3: Company editing working")
            else:
                self.log(f"❌ Scenario 3 failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Scenario 3 error: {str(e)}")
            return False
        
        # Scenario 4: Test user creation and permissions (already tested above)
        self.log("Scenario 4: User creation and permissions - ✅ COMPLETED IN USER MANAGEMENT TEST")
        
        # Scenario 5: Test currency management features (already tested above)
        self.log("Scenario 5: Currency management features - ✅ COMPLETED IN CURRENCY MANAGEMENT TEST")
        
        return True
    
    def run_all_tests(self):
        """Run all ERP backend tests"""
        self.log("🚀 STARTING COMPREHENSIVE ERP BACKEND TESTING")
        self.log("=" * 80)
        
        test_results = {}
        
        # Setup test environment
        if not self.setup_test_environment():
            self.log("❌ CRITICAL: Test environment setup failed")
            return False
        
        # Run all tests
        tests = [
            ("Sister Company Display Issue", self.test_sister_company_display_issue),
            ("Company Management API", self.test_company_management_api),
            ("User Management System", self.test_user_management_system),
            ("Currency Management", self.test_currency_management),
            ("PDF Generation Issues", self.test_pdf_generation_issues),
            ("Comprehensive Scenarios", self.test_comprehensive_scenarios)
        ]
        
        for test_name, test_func in tests:
            self.log(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                test_results[test_name] = result
                if result:
                    self.log(f"✅ {test_name}: PASSED")
                else:
                    self.log(f"❌ {test_name}: FAILED")
            except Exception as e:
                self.log(f"❌ {test_name}: ERROR - {str(e)}")
                test_results[test_name] = False
        
        # Summary
        self.log("\n" + "="*80)
        self.log("🏁 ERP BACKEND TESTING SUMMARY")
        self.log("="*80)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"{test_name}: {status}")
        
        self.log(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            self.log("🎉 ALL ERP BACKEND TESTS PASSED!")
            return True
        else:
            self.log("⚠️ SOME ERP BACKEND TESTS FAILED - See details above")
            return False

if __name__ == "__main__":
    tester = ERPBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)