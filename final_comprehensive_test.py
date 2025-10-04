#!/usr/bin/env python3
"""
Final Comprehensive Test for Sister Company Issues
Tests all aspects mentioned in the review request
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

# Known working test account
WORKING_EMAIL = "usertestsister@example.com"
WORKING_PASSWORD = "testsister123"

class FinalComprehensiveTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.test_results = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_working_account_sister_companies(self):
        """Test the known working account to verify sister companies are visible"""
        self.log("🔍 TESTING WORKING ACCOUNT SISTER COMPANIES")
        self.log("=" * 50)
        
        # Login with working account
        login_data = {
            "email": WORKING_EMAIL,
            "password": WORKING_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code != 200:
                self.log(f"❌ Login failed: {response.text}")
                return False
            
            data = response.json()
            self.auth_token = data.get('access_token')
            self.user_data = data.get('user')
            
            self.log(f"✅ Logged in as: {self.user_data.get('email')}")
            self.log(f"User ID: {self.user_data.get('id')}")
            self.log(f"Onboarding completed: {self.user_data.get('onboarding_completed')}")
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            # Test company management endpoint
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            if response.status_code == 200:
                companies = response.json()
                main_companies = [c for c in companies if c.get('is_main_company', False)]
                sister_companies = [c for c in companies if not c.get('is_main_company', True)]
                
                self.log(f"✅ Total companies found: {len(companies)}")
                self.log(f"✅ Main companies: {len(main_companies)}")
                self.log(f"✅ Sister companies: {len(sister_companies)}")
                
                # Display company details
                for i, company in enumerate(companies):
                    company_type = "MAIN" if company.get('is_main_company', False) else "SISTER"
                    self.log(f"  Company {i+1} ({company_type}): {company.get('company_name')}")
                    self.log(f"    Business Type: {company.get('business_type')}")
                    self.log(f"    Base Currency: {company.get('base_currency')}")
                    if not company.get('is_main_company', False):
                        self.log(f"    Parent Company ID: {company.get('parent_company_id')}")
                
                self.test_results['working_account_sister_companies'] = len(sister_companies) > 0
                return len(sister_companies) > 0
            else:
                self.log(f"❌ Companies management failed: {response.text}")
                self.test_results['working_account_sister_companies'] = False
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.test_results['working_account_sister_companies'] = False
            return False
    
    def test_company_setup_already_completed_error(self):
        """Test the 'company setup already completed' error"""
        self.log("\n🔍 TESTING 'COMPANY SETUP ALREADY COMPLETED' ERROR")
        self.log("=" * 50)
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Try to create another company setup (should fail)
        setup_data = {
            "company_name": "Another Test Company",
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR"],
            "business_type": "Corporation",
            "industry": "Technology",
            "address": "456 Another Street",
            "city": "Another City",
            "state": "CA",
            "postal_code": "54321",
            "phone": "+1-555-987-6543",
            "email": WORKING_EMAIL,
            "website": "https://another.com",
            "tax_number": "ANOTHER123",
            "registration_number": "ANOTHERREG123"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Company setup attempt response status: {response.status_code}")
            self.log(f"Company setup attempt response: {response.text}")
            
            if response.status_code == 400 and "already completed" in response.text:
                self.log("✅ 'Company setup already completed' error confirmed")
                self.log("✅ This is working as designed - prevents multiple main companies")
                self.test_results['company_setup_limitation'] = True
                return True
            else:
                self.log(f"⚠️ Unexpected response - limitation may not be working")
                self.test_results['company_setup_limitation'] = False
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.test_results['company_setup_limitation'] = False
            return False
    
    def test_sister_company_addition_after_setup(self):
        """Test adding sister companies after initial setup"""
        self.log("\n🔍 TESTING SISTER COMPANY ADDITION AFTER SETUP")
        self.log("=" * 50)
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Check current company setup
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            if response.status_code == 200:
                company_data = response.json()
                business_type = company_data.get('business_type')
                self.log(f"Current business type: {business_type}")
                
                if business_type == "Group Company":
                    self.log("✅ Account is Group Company - can add sister companies")
                    
                    # Try to add a new sister company
                    sister_data = {
                        "company_name": f"New Sister Company {int(time.time())}",
                        "country_code": "CA",
                        "base_currency": "CAD",
                        "business_type": "Corporation",
                        "industry": "Finance",
                        "fiscal_year_start": "01-01"
                    }
                    
                    response = self.session.post(f"{API_BASE}/company/sister-companies", json=sister_data, headers=headers)
                    self.log(f"Sister company addition response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.log("✅ Sister company addition successful")
                        self.log(f"New sister company ID: {data.get('id')}")
                        self.log(f"New sister company name: {data.get('company_name')}")
                        self.test_results['sister_company_addition'] = True
                        return True
                    else:
                        self.log(f"❌ Sister company addition failed: {response.text}")
                        self.test_results['sister_company_addition'] = False
                        return False
                else:
                    self.log(f"⚠️ Account is {business_type} - cannot add sister companies")
                    self.log("💡 This explains why user cannot see sister companies!")
                    self.test_results['sister_company_addition'] = False
                    return False
            else:
                self.log(f"❌ Could not get company setup: {response.text}")
                self.test_results['sister_company_addition'] = False
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.test_results['sister_company_addition'] = False
            return False
    
    def test_different_account_scenarios(self):
        """Test different account scenarios to understand the issue"""
        self.log("\n🔍 TESTING DIFFERENT ACCOUNT SCENARIOS")
        self.log("=" * 50)
        
        scenarios = [
            {
                "name": "Private Limited Company",
                "business_type": "Private Limited Company",
                "should_have_sisters": False
            },
            {
                "name": "Group Company with Sisters",
                "business_type": "Group Company", 
                "should_have_sisters": True,
                "sister_companies": [
                    {
                        "company_name": "Test Sister A",
                        "country": "GB",
                        "base_currency": "GBP",
                        "business_type": "Private Limited Company",
                        "industry": "Finance"
                    }
                ]
            }
        ]
        
        results = {}
        
        for scenario in scenarios:
            self.log(f"\n--- Testing Scenario: {scenario['name']} ---")
            
            # Create test account
            test_email = f"scenario{int(time.time())}{scenario['name'].replace(' ', '').lower()}@example.com"
            signup_data = {
                "email": test_email,
                "password": "testpass123",
                "name": f"Test {scenario['name']} User",
                "company": f"Test {scenario['name']} Company"
            }
            
            try:
                # Sign up
                response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
                if response.status_code != 200:
                    self.log(f"❌ Signup failed: {response.text}")
                    continue
                
                token = response.json().get('access_token')
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Setup company
                setup_data = {
                    "company_name": f"Test {scenario['name']} Company",
                    "country_code": "US",
                    "base_currency": "USD",
                    "additional_currencies": ["EUR"],
                    "business_type": scenario["business_type"],
                    "industry": "Technology",
                    "address": "123 Test Street",
                    "city": "Test City",
                    "state": "CA",
                    "postal_code": "12345",
                    "phone": "+1-555-123-4567",
                    "email": test_email,
                    "website": "https://test.com",
                    "tax_number": "123456789",
                    "registration_number": "REG123456"
                }
                
                # Add sister companies if specified
                if scenario.get("sister_companies"):
                    setup_data["sister_companies"] = scenario["sister_companies"]
                
                response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
                if response.status_code != 200:
                    self.log(f"❌ Company setup failed: {response.text}")
                    continue
                
                self.log(f"✅ Created {scenario['name']} account")
                
                # Check companies
                response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
                if response.status_code == 200:
                    companies = response.json()
                    sister_count = len([c for c in companies if not c.get('is_main_company', True)])
                    
                    self.log(f"Companies found: {len(companies)} (Sisters: {sister_count})")
                    
                    if scenario["should_have_sisters"]:
                        if sister_count > 0:
                            self.log("✅ Sister companies found as expected")
                            results[scenario['name']] = True
                        else:
                            self.log("❌ No sister companies found - unexpected!")
                            results[scenario['name']] = False
                    else:
                        if sister_count == 0:
                            self.log("✅ No sister companies as expected")
                            results[scenario['name']] = True
                        else:
                            self.log("❌ Sister companies found - unexpected!")
                            results[scenario['name']] = False
                else:
                    self.log(f"❌ Could not get companies: {response.text}")
                    results[scenario['name']] = False
                    
            except Exception as e:
                self.log(f"❌ Scenario error: {str(e)}")
                results[scenario['name']] = False
        
        self.test_results['account_scenarios'] = results
        return all(results.values())
    
    def provide_solutions(self):
        """Provide solutions for the identified issues"""
        self.log("\n💡 SOLUTIONS FOR USER'S SISTER COMPANY ISSUES")
        self.log("=" * 50)
        
        self.log("ISSUE 1: User's account doesn't show sister companies")
        self.log("SOLUTION OPTIONS:")
        self.log("1. Check user's business_type in company setup:")
        self.log("   - If 'Private Limited Company': Convert to 'Group Company'")
        self.log("   - Update database: UPDATE company_setups SET business_type='Group Company'")
        
        self.log("\n2. Add sister companies to existing Group Company:")
        self.log("   - Use POST /api/company/sister-companies endpoint")
        self.log("   - Or reset onboarding to allow setup modification")
        
        self.log("\nISSUE 2: 'Company setup already completed' error")
        self.log("SOLUTION OPTIONS:")
        self.log("1. Allow company setup modification after completion:")
        self.log("   - Add PUT /api/setup/company endpoint for updates")
        self.log("   - Or add separate endpoint for business type conversion")
        
        self.log("\n2. Reset user's onboarding status:")
        self.log("   - Set onboarding_completed = false in users table")
        self.log("   - Allow user to go through setup again")
        
        self.log("\n3. Add 'Convert to Group Company' feature:")
        self.log("   - New endpoint: POST /api/company/convert-to-group")
        self.log("   - Updates business_type and enables sister company features")
    
    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        self.log("🚀 STARTING FINAL COMPREHENSIVE SISTER COMPANY TEST")
        self.log("=" * 60)
        
        # Test 1: Working account sister companies
        test1_result = self.test_working_account_sister_companies()
        
        # Test 2: Company setup limitation
        test2_result = self.test_company_setup_already_completed_error()
        
        # Test 3: Sister company addition after setup
        test3_result = self.test_sister_company_addition_after_setup()
        
        # Test 4: Different account scenarios
        test4_result = self.test_different_account_scenarios()
        
        # Provide solutions
        self.provide_solutions()
        
        # Final summary
        self.log("\n" + "=" * 60)
        self.log("📊 FINAL TEST SUMMARY")
        self.log("=" * 60)
        
        tests = [
            ("Working Account Sister Companies", test1_result),
            ("Company Setup Limitation", test2_result),
            ("Sister Company Addition", test3_result),
            ("Account Scenarios", test4_result)
        ]
        
        for test_name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name}: {status}")
        
        # Overall conclusion
        passed_tests = sum(1 for _, result in tests if result)
        total_tests = len(tests)
        
        self.log(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            self.log("🎉 ALL TESTS PASSED - Sister company functionality is working correctly")
        else:
            self.log("⚠️ Some tests failed - Issues identified and solutions provided")
        
        return self.test_results

if __name__ == "__main__":
    tester = FinalComprehensiveTest()
    results = tester.run_comprehensive_test()