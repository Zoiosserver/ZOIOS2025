#!/usr/bin/env python3
"""
Sister Company Functionality Testing Script
Tests the "Enable Sister Companies" button functionality as reported by user.

Specific test cases:
1. Login with test account: usertestsister@example.com / testsister123
2. Test convert-to-group endpoint directly: PUT /api/setup/company/convert-to-group
3. Check current company setup: GET /api/setup/company
4. Debug conversion process and verify business_type updates
5. Test with fresh account if needed
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

# Test credentials from review request
TEST_EMAIL = "usertestsister@example.com"
TEST_PASSWORD = "testsister123"

class SisterCompanyTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.company_data = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_login_with_test_account(self):
        """Test login with the specific test account: usertestsister@example.com / testsister123"""
        self.log("🔐 Testing login with test account: usertestsister@example.com")
        
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            self.log(f"Login response status: {response.status_code}")
            self.log(f"Login response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log("✅ Login successful with test account")
                self.log(f"User ID: {self.user_data.get('id')}")
                self.log(f"Email: {self.user_data.get('email')}")
                self.log(f"Onboarding completed: {self.user_data.get('onboarding_completed')}")
                return True
            else:
                self.log(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}")
            return False
    
    def test_get_current_company_setup(self):
        """Test GET /api/setup/company to see current business type"""
        self.log("📋 Testing GET /api/setup/company to check current business type")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            self.log(f"Get company setup response status: {response.status_code}")
            self.log(f"Get company setup response: {response.text}")
            
            if response.status_code == 200:
                self.company_data = response.json()
                business_type = self.company_data.get('business_type')
                company_name = self.company_data.get('company_name')
                
                self.log("✅ Company setup retrieved successfully")
                self.log(f"Company Name: {company_name}")
                self.log(f"Current Business Type: {business_type}")
                self.log(f"Setup Completed: {self.company_data.get('setup_completed')}")
                
                if business_type == "Group Company":
                    self.log("ℹ️ Company is already a Group Company")
                elif business_type == "Private Limited Company":
                    self.log("ℹ️ Company is Private Limited Company - can be converted to Group Company")
                else:
                    self.log(f"ℹ️ Company business type: {business_type}")
                
                return True
            else:
                self.log(f"❌ Get company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Get company setup error: {str(e)}")
            return False
    
    def test_convert_to_group_endpoint(self):
        """Test PUT /api/setup/company/convert-to-group endpoint directly"""
        self.log("🔄 Testing PUT /api/setup/company/convert-to-group endpoint")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/setup/company/convert-to-group", headers=headers)
            self.log(f"Convert to group response status: {response.status_code}")
            self.log(f"Convert to group response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Convert to Group Company endpoint working")
                self.log(f"Success: {data.get('success')}")
                self.log(f"Message: {data.get('message')}")
                self.log(f"New Business Type: {data.get('business_type')}")
                
                if data.get('success') and data.get('business_type') == 'Group Company':
                    self.log("✅ Conversion to Group Company successful")
                    return True
                else:
                    self.log("❌ Conversion response indicates failure")
                    return False
            else:
                self.log(f"❌ Convert to group failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Convert to group error: {str(e)}")
            return False
    
    def test_verify_conversion_in_database(self):
        """Verify the conversion was saved in database by re-fetching company setup"""
        self.log("🔍 Verifying conversion was saved in database")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            self.log(f"Verification response status: {response.status_code}")
            
            if response.status_code == 200:
                updated_company_data = response.json()
                business_type = updated_company_data.get('business_type')
                
                self.log(f"Updated Business Type: {business_type}")
                
                if business_type == "Group Company":
                    self.log("✅ Conversion verified - business_type updated to 'Group Company' in database")
                    return True
                else:
                    self.log(f"❌ Conversion NOT saved - business_type is still '{business_type}'")
                    return False
            else:
                self.log(f"❌ Verification failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Verification error: {str(e)}")
            return False
    
    def test_sister_companies_endpoints_after_conversion(self):
        """Test sister company endpoints after conversion to Group Company"""
        self.log("👥 Testing sister company endpoints after conversion")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test GET /api/company/sister-companies
            response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
            self.log(f"Get sister companies response status: {response.status_code}")
            self.log(f"Get sister companies response: {response.text}")
            
            if response.status_code == 200:
                sister_companies = response.json()
                self.log(f"✅ Sister companies endpoint working - found {len(sister_companies)} sister companies")
                
                for i, sister in enumerate(sister_companies):
                    self.log(f"Sister Company {i+1}: {sister.get('company_name')} ({sister.get('business_type')})")
                
                return True
            else:
                self.log(f"❌ Get sister companies failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister companies test error: {str(e)}")
            return False
    
    def test_add_sister_company_after_conversion(self):
        """Test adding a sister company after conversion to Group Company"""
        self.log("➕ Testing adding sister company after conversion")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Sister company data
        sister_company_data = {
            "company_name": "Test Sister Company",
            "country_code": "US",
            "base_currency": "USD",
            "business_type": "Private Limited Company",
            "industry": "Technology",
            "fiscal_year_start": "01-01"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/company/sister-companies", 
                                       json=sister_company_data, headers=headers)
            self.log(f"Add sister company response status: {response.status_code}")
            self.log(f"Add sister company response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Sister company added successfully")
                self.log(f"Sister Company ID: {data.get('id')}")
                self.log(f"Sister Company Name: {data.get('company_name')}")
                return True
            else:
                self.log(f"❌ Add sister company failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Add sister company error: {str(e)}")
            return False
    
    def test_companies_management_endpoint(self):
        """Test GET /api/companies/management to see all companies including sisters"""
        self.log("🏢 Testing GET /api/companies/management endpoint")
        
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
                self.log(f"✅ Companies management endpoint working - found {len(companies)} companies")
                
                main_companies = [c for c in companies if c.get('is_main_company', False)]
                sister_companies = [c for c in companies if not c.get('is_main_company', True)]
                
                self.log(f"Main companies: {len(main_companies)}")
                self.log(f"Sister companies: {len(sister_companies)}")
                
                for company in companies:
                    company_type = "Main" if company.get('is_main_company', False) else "Sister"
                    self.log(f"{company_type} Company: {company.get('company_name')} ({company.get('business_type')})")
                
                return True
            else:
                self.log(f"❌ Companies management failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Companies management error: {str(e)}")
            return False
    
    def test_fresh_account_conversion(self):
        """Test conversion with a fresh account to ensure it works from scratch"""
        self.log("🆕 Testing conversion with fresh account")
        
        # Generate unique credentials
        timestamp = str(int(time.time()))
        fresh_email = f"freshtest{timestamp}@example.com"
        fresh_password = "freshtest123"
        
        # Create fresh account
        signup_data = {
            "email": fresh_email,
            "password": fresh_password,
            "name": "Fresh Test User",
            "company": "Fresh Test Company"
        }
        
        try:
            # Sign up
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            if response.status_code != 200:
                self.log(f"❌ Fresh account signup failed: {response.text}")
                return False
            
            fresh_token = response.json().get('access_token')
            headers = {
                "Authorization": f"Bearer {fresh_token}",
                "Content-Type": "application/json"
            }
            
            # Setup company as Private Limited Company
            setup_data = {
                "company_name": "Fresh Test Company",
                "country_code": "US",
                "base_currency": "USD",
                "additional_currencies": ["EUR"],
                "business_type": "Private Limited Company",
                "industry": "Technology",
                "address": "123 Fresh Street",
                "city": "Fresh City",
                "state": "CA",
                "postal_code": "12345",
                "phone": "+1-555-123-4567",
                "email": fresh_email,
                "website": "https://freshtest.com",
                "tax_number": "123456789",
                "registration_number": "REG123456"
            }
            
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            if response.status_code != 200:
                self.log(f"❌ Fresh company setup failed: {response.text}")
                return False
            
            self.log("✅ Fresh account and company setup created")
            
            # Verify initial business type
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            if response.status_code == 200:
                initial_data = response.json()
                initial_business_type = initial_data.get('business_type')
                self.log(f"Initial business type: {initial_business_type}")
                
                if initial_business_type != "Private Limited Company":
                    self.log(f"⚠️ Expected 'Private Limited Company', got '{initial_business_type}'")
            
            # Test conversion to Group Company
            response = self.session.put(f"{API_BASE}/setup/company/convert-to-group", headers=headers)
            self.log(f"Fresh account conversion response status: {response.status_code}")
            self.log(f"Fresh account conversion response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('business_type') == 'Group Company':
                    self.log("✅ Fresh account conversion successful")
                    
                    # Verify conversion was saved
                    verify_response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        if verify_data.get('business_type') == 'Group Company':
                            self.log("✅ Fresh account conversion verified in database")
                            return True
                        else:
                            self.log("❌ Fresh account conversion not saved in database")
                            return False
                    else:
                        self.log("❌ Could not verify fresh account conversion")
                        return False
                else:
                    self.log("❌ Fresh account conversion failed")
                    return False
            else:
                self.log(f"❌ Fresh account conversion failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Fresh account test error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all sister company functionality tests"""
        self.log("🚀 Starting comprehensive sister company functionality testing")
        self.log("=" * 80)
        
        test_results = {}
        
        # Test 1: Login with test account
        self.log("\n📋 TEST 1: Login with test account")
        test_results['login'] = self.test_login_with_test_account()
        
        if test_results['login']:
            # Test 2: Check current company setup
            self.log("\n📋 TEST 2: Check current company setup")
            test_results['current_setup'] = self.test_get_current_company_setup()
            
            # Test 3: Test convert-to-group endpoint
            self.log("\n📋 TEST 3: Test convert-to-group endpoint")
            test_results['convert_endpoint'] = self.test_convert_to_group_endpoint()
            
            # Test 4: Verify conversion in database
            self.log("\n📋 TEST 4: Verify conversion in database")
            test_results['verify_conversion'] = self.test_verify_conversion_in_database()
            
            # Test 5: Test sister companies endpoints
            self.log("\n📋 TEST 5: Test sister companies endpoints")
            test_results['sister_endpoints'] = self.test_sister_companies_endpoints_after_conversion()
            
            # Test 6: Test adding sister company
            self.log("\n📋 TEST 6: Test adding sister company")
            test_results['add_sister'] = self.test_add_sister_company_after_conversion()
            
            # Test 7: Test companies management endpoint
            self.log("\n📋 TEST 7: Test companies management endpoint")
            test_results['companies_management'] = self.test_companies_management_endpoint()
        
        # Test 8: Test with fresh account
        self.log("\n📋 TEST 8: Test with fresh account")
        test_results['fresh_account'] = self.test_fresh_account_conversion()
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log("📊 TEST RESULTS SUMMARY")
        self.log("=" * 80)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name.upper()}: {status}")
            if result:
                passed_tests += 1
        
        self.log(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            self.log("🎉 ALL TESTS PASSED - Sister company functionality is working correctly!")
            return True
        else:
            self.log("⚠️ SOME TESTS FAILED - Sister company functionality has issues")
            return False

def main():
    """Main function to run sister company tests"""
    print("Sister Company Functionality Testing")
    print("=" * 50)
    
    tester = SisterCompanyTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ Sister company functionality testing completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Sister company functionality testing found issues")
        sys.exit(1)

if __name__ == "__main__":
    main()