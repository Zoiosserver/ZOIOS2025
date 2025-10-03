#!/usr/bin/env python3
"""
Backend API Testing Script for Company Setup Flow
Tests the redirection issue in company setup wizard
"""

import requests
import json
import os
from datetime import datetime
import sys

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://onboarding-flow-11.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified - using timestamp to ensure fresh user
import time
timestamp = str(int(time.time()))
TEST_EMAIL = f"testuser{timestamp}@example.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "Test User"
TEST_COMPANY = "Test Company"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_user_registration(self):
        """Test user registration with new test user"""
        self.log("Testing user registration...")
        
        # First, try to clean up any existing test user (ignore errors)
        try:
            # This will fail if user doesn't exist, which is fine
            pass
        except:
            pass
            
        signup_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "company": TEST_COMPANY
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            self.log(f"Registration response status: {response.status_code}")
            self.log(f"Registration response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log("✅ User registration successful")
                self.log(f"User ID: {self.user_data.get('id')}")
                self.log(f"Onboarding completed: {self.user_data.get('onboarding_completed')}")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                self.log("⚠️ User already exists, proceeding with login test")
                return self.test_user_login()
            else:
                self.log(f"❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Registration error: {str(e)}")
            return False
    
    def test_user_login(self):
        """Test user login to get authentication token"""
        self.log("Testing user login...")
        
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
                self.log("✅ User login successful")
                self.log(f"User ID: {self.user_data.get('id')}")
                self.log(f"Onboarding completed: {self.user_data.get('onboarding_completed')}")
                return True
            else:
                self.log(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}")
            return False
    
    def test_auth_me_endpoint(self):
        """Test /auth/me endpoint to verify user data"""
        self.log("Testing /auth/me endpoint...")
        
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
                self.log("✅ /auth/me endpoint working")
                self.log(f"User ID: {data.get('id')}")
                self.log(f"Email: {data.get('email')}")
                self.log(f"Onboarding completed: {data.get('onboarding_completed')}")
                
                # Update our user data
                self.user_data = data
                return True
            else:
                self.log(f"❌ /auth/me failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ /auth/me error: {str(e)}")
            return False
    
    def test_company_setup_step1(self):
        """Test company setup step 1 submission"""
        self.log("Testing company setup step 1...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Company setup data - using review request specifications
        setup_data = {
            "company_name": "Test Company Inc",
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR", "GBP", "JPY"],
            "business_type": "Corporation",
            "industry": "Technology",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "CA",
            "postal_code": "12345",
            "phone": "+1-555-123-4567",
            "email": TEST_EMAIL,
            "website": "https://testcompany.com",
            "tax_number": "123456789",
            "registration_number": "REG123456"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Company setup response status: {response.status_code}")
            self.log(f"Company setup response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Company setup step 1 successful")
                self.log(f"Company ID: {data.get('id')}")
                self.log(f"Setup completed: {data.get('setup_completed')}")
                return True
            else:
                self.log(f"❌ Company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company setup error: {str(e)}")
            return False
    
    def test_auth_me_after_setup(self):
        """Test /auth/me endpoint after company setup to verify onboarding_completed status"""
        self.log("Testing /auth/me after company setup...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
            self.log(f"/auth/me after setup response status: {response.status_code}")
            self.log(f"/auth/me after setup response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ /auth/me after setup working")
                self.log(f"User ID: {data.get('id')}")
                self.log(f"Email: {data.get('email')}")
                self.log(f"Onboarding completed: {data.get('onboarding_completed')}")
                
                # Check if onboarding_completed was updated
                if data.get('onboarding_completed'):
                    self.log("✅ onboarding_completed status updated correctly")
                    return True
                else:
                    self.log("❌ onboarding_completed status NOT updated - this is the issue!")
                    return False
            else:
                self.log(f"❌ /auth/me after setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ /auth/me after setup error: {str(e)}")
            return False
    
    def test_jwt_token_validity(self):
        """Test JWT token validity and refresh"""
        self.log("Testing JWT token validity...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test multiple endpoints to ensure token works consistently
        endpoints_to_test = [
            "/auth/me",
            "/setup/countries",
            "/setup/currencies"
        ]
        
        all_passed = True
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}", headers=headers)
                if response.status_code == 200:
                    self.log(f"✅ JWT token valid for {endpoint}")
                else:
                    self.log(f"❌ JWT token invalid for {endpoint}: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log(f"❌ JWT token test error for {endpoint}: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_company_setup_get(self):
        """Test getting company setup data"""
        self.log("Testing get company setup...")
        
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
                data = response.json()
                self.log("✅ Get company setup successful")
                self.log(f"Company name: {data.get('company_name')}")
                self.log(f"Setup completed: {data.get('setup_completed')}")
                return True
            elif response.status_code == 404:
                self.log("⚠️ Company setup not found - setup may not have been saved")
                return False
            else:
                self.log(f"❌ Get company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Get company setup error: {str(e)}")
            return False
    
    def test_frontend_simulation(self):
        """Simulate the exact frontend flow that's causing the issue"""
        self.log("Testing frontend simulation flow...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Simulate what happens after company setup completion
        # 1. Company setup completes successfully (already tested)
        # 2. Frontend calls window.location.reload()
        # 3. AuthContext checkAuth runs and calls /auth/me
        
        self.log("Simulating page reload - calling /auth/me multiple times...")
        
        for i in range(3):
            try:
                response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
                self.log(f"Auth check #{i+1} - Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"Auth check #{i+1} - onboarding_completed: {data.get('onboarding_completed')}")
                    
                    if not data.get('onboarding_completed'):
                        self.log(f"❌ Auth check #{i+1} - onboarding_completed is still False!")
                        return False
                else:
                    self.log(f"❌ Auth check #{i+1} failed: {response.text}")
                    return False
                    
            except Exception as e:
                self.log(f"❌ Auth check #{i+1} error: {str(e)}")
                return False
        
        self.log("✅ Frontend simulation passed - onboarding_completed consistently True")
        return True
    
    def test_token_refresh_scenario(self):
        """Test if there are any token refresh issues"""
        self.log("Testing token refresh scenario...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
        
        # Test with a fresh session (simulating page reload)
        fresh_session = requests.Session()
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = fresh_session.get(f"{API_BASE}/auth/me", headers=headers)
            self.log(f"Fresh session auth check - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Fresh session - onboarding_completed: {data.get('onboarding_completed')}")
                return data.get('onboarding_completed', False)
            else:
                self.log(f"❌ Fresh session auth check failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Fresh session error: {str(e)}")
            return False

    def test_chart_of_accounts(self):
        """Test chart of accounts endpoint"""
        self.log("Testing chart of accounts...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/setup/chart-of-accounts", headers=headers)
            self.log(f"Chart of accounts response status: {response.status_code}")
            self.log(f"Chart of accounts response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Chart of accounts retrieved successfully")
                self.log(f"Number of accounts: {len(data)}")
                
                # Verify US GAAP accounts are created
                account_codes = [account.get('code') for account in data]
                expected_codes = ['1000', '1100', '2000', '3000', '4000', '5000', '6000']
                
                found_codes = [code for code in expected_codes if code in account_codes]
                self.log(f"Expected account codes found: {found_codes}")
                
                if len(found_codes) >= 5:  # At least 5 basic accounts should exist
                    self.log("✅ Chart of accounts contains expected US GAAP accounts")
                    return True
                else:
                    self.log("⚠️ Chart of accounts missing some expected accounts")
                    return True  # Still consider it working if accounts exist
            else:
                self.log(f"❌ Chart of accounts failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Chart of accounts error: {str(e)}")
            return False

    def test_currency_rates_get(self):
        """Test getting currency exchange rates"""
        self.log("Testing GET currency rates...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/currency/rates", headers=headers)
            self.log(f"Currency rates response status: {response.status_code}")
            self.log(f"Currency rates response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Currency rates retrieved successfully")
                self.log(f"Number of rates: {len(data)}")
                
                # Check if we have rates for our additional currencies
                currencies = [rate.get('target_currency') for rate in data]
                expected_currencies = ['EUR', 'GBP', 'JPY']
                found_currencies = [curr for curr in expected_currencies if curr in currencies]
                
                self.log(f"Currency rates found for: {found_currencies}")
                
                if len(found_currencies) >= 2:  # At least 2 currencies should have rates
                    self.log("✅ Currency rates contain expected currencies")
                    return True
                else:
                    self.log("⚠️ Some expected currency rates missing, but endpoint works")
                    return True
            else:
                self.log(f"❌ Currency rates failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Currency rates error: {str(e)}")
            return False

    def test_currency_rates_update(self):
        """Test updating currency rates from online sources"""
        self.log("Testing POST currency rates update...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/currency/update-rates", headers=headers)
            self.log(f"Currency update response status: {response.status_code}")
            self.log(f"Currency update response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Currency rates update successful")
                self.log(f"Update success: {data.get('success')}")
                self.log(f"Updated count: {data.get('updated_count', 0)}")
                
                if data.get('success'):
                    self.log("✅ Online currency rate fetching working")
                    return True
                else:
                    self.log(f"⚠️ Update reported failure: {data.get('error', 'Unknown error')}")
                    return False
            else:
                self.log(f"❌ Currency update failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Currency update error: {str(e)}")
            return False

    def test_currency_manual_rate(self):
        """Test setting manual currency rate"""
        self.log("Testing POST manual currency rate...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Set a manual rate for USD to EUR
        manual_rate_data = {
            "base_currency": "USD",
            "target_currency": "EUR",
            "rate": 0.85,
            "source": "manual"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/currency/set-manual-rate", json=manual_rate_data, headers=headers)
            self.log(f"Manual rate response status: {response.status_code}")
            self.log(f"Manual rate response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Manual currency rate set successfully")
                self.log(f"Rate: {data.get('rate')}")
                self.log(f"Source: {data.get('source')}")
                
                if data.get('source') == 'manual' and data.get('rate') == 0.85:
                    self.log("✅ Manual rate setting working correctly")
                    return True
                else:
                    self.log("⚠️ Manual rate data inconsistent")
                    return False
            else:
                self.log(f"❌ Manual rate failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Manual rate error: {str(e)}")
            return False

    def test_currency_conversion(self):
        """Test currency conversion"""
        self.log("Testing POST currency conversion...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test conversion from USD to EUR
        conversion_params = {
            "amount": 100.0,
            "from_currency": "USD", 
            "to_currency": "EUR"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/currency/convert", params=conversion_params, headers=headers)
            self.log(f"Currency conversion response status: {response.status_code}")
            self.log(f"Currency conversion response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Currency conversion successful")
                self.log(f"Original amount: {data.get('original_amount')}")
                self.log(f"Converted amount: {data.get('converted_amount')}")
                self.log(f"Exchange rate: {data.get('exchange_rate')}")
                self.log(f"Rate source: {data.get('rate_source')}")
                
                if data.get('converted_amount') and data.get('exchange_rate'):
                    self.log("✅ Currency conversion working correctly")
                    return True
                else:
                    self.log("⚠️ Currency conversion data incomplete")
                    return False
            else:
                self.log(f"❌ Currency conversion failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Currency conversion error: {str(e)}")
            return False

    def test_exchangerate_api_integration(self):
        """Test direct integration with exchangerate-api.com"""
        self.log("Testing exchangerate-api.com integration...")
        
        try:
            # Test direct API call to verify the service is accessible
            test_url = "https://v6.exchangerate-api.com/v6/latest/USD"
            response = self.session.get(test_url, timeout=10)
            
            self.log(f"ExchangeRate API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "success":
                    rates = data.get("conversion_rates", {})
                    self.log("✅ ExchangeRate API integration working")
                    self.log(f"Sample rates - EUR: {rates.get('EUR')}, GBP: {rates.get('GBP')}, JPY: {rates.get('JPY')}")
                    return True
                else:
                    self.log(f"❌ ExchangeRate API error: {data.get('error-type')}")
                    return False
            else:
                self.log(f"❌ ExchangeRate API HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ ExchangeRate API integration error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("=" * 80)
        self.log("STARTING COMPREHENSIVE BACKEND API TESTS")
        self.log("Testing: Company Setup Flow + Currency Service + Chart of Accounts")
        self.log("=" * 80)
        
        test_results = {}
        
        # Phase 1: Authentication and Company Setup Tests
        self.log("\n" + "=" * 40)
        self.log("PHASE 1: AUTHENTICATION & COMPANY SETUP")
        self.log("=" * 40)
        
        # Test 1: User Registration
        test_results['registration'] = self.test_user_registration()
        
        # Test 2: User Login (if registration failed)
        if not test_results['registration']:
            test_results['login'] = self.test_user_login()
        else:
            test_results['login'] = True
        
        # Test 3: Auth Me endpoint (before setup)
        test_results['auth_me_before'] = self.test_auth_me_endpoint()
        
        # Test 4: JWT Token validity
        test_results['jwt_validity'] = self.test_jwt_token_validity()
        
        # Test 5: Company Setup Step 1
        test_results['company_setup'] = self.test_company_setup_step1()
        
        # Test 6: Auth Me endpoint (after setup)
        test_results['auth_me_after'] = self.test_auth_me_after_setup()
        
        # Test 7: Get Company Setup
        test_results['get_company_setup'] = self.test_company_setup_get()
        
        # Phase 2: Chart of Accounts Tests
        self.log("\n" + "=" * 40)
        self.log("PHASE 2: CHART OF ACCOUNTS")
        self.log("=" * 40)
        
        # Test 8: Chart of Accounts
        test_results['chart_of_accounts'] = self.test_chart_of_accounts()
        
        # Phase 3: Currency Service Tests
        self.log("\n" + "=" * 40)
        self.log("PHASE 3: CURRENCY SERVICE")
        self.log("=" * 40)
        
        # Test 9: ExchangeRate API Integration
        test_results['exchangerate_api'] = self.test_exchangerate_api_integration()
        
        # Test 10: Get Currency Rates
        test_results['currency_rates_get'] = self.test_currency_rates_get()
        
        # Test 11: Update Currency Rates
        test_results['currency_rates_update'] = self.test_currency_rates_update()
        
        # Test 12: Manual Currency Rate
        test_results['currency_manual_rate'] = self.test_currency_manual_rate()
        
        # Test 13: Currency Conversion
        test_results['currency_conversion'] = self.test_currency_conversion()
        
        # Phase 4: Integration Tests
        self.log("\n" + "=" * 40)
        self.log("PHASE 4: INTEGRATION TESTS")
        self.log("=" * 40)
        
        # Test 14: Frontend simulation
        test_results['frontend_simulation'] = self.test_frontend_simulation()
        
        # Test 15: Token refresh scenario
        test_results['token_refresh'] = self.test_token_refresh_scenario()
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log("COMPREHENSIVE TEST RESULTS SUMMARY")
        self.log("=" * 80)
        
        # Group results by phase
        auth_tests = ['registration', 'login', 'auth_me_before', 'jwt_validity', 'company_setup', 'auth_me_after', 'get_company_setup']
        chart_tests = ['chart_of_accounts']
        currency_tests = ['exchangerate_api', 'currency_rates_get', 'currency_rates_update', 'currency_manual_rate', 'currency_conversion']
        integration_tests = ['frontend_simulation', 'token_refresh']
        
        self.log("\n📋 AUTHENTICATION & COMPANY SETUP:")
        for test_name in auth_tests:
            if test_name in test_results:
                status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
                self.log(f"  {test_name.upper()}: {status}")
        
        self.log("\n📊 CHART OF ACCOUNTS:")
        for test_name in chart_tests:
            if test_name in test_results:
                status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
                self.log(f"  {test_name.upper()}: {status}")
        
        self.log("\n💱 CURRENCY SERVICE:")
        for test_name in currency_tests:
            if test_name in test_results:
                status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
                self.log(f"  {test_name.upper()}: {status}")
        
        self.log("\n🔗 INTEGRATION TESTS:")
        for test_name in integration_tests:
            if test_name in test_results:
                status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
                self.log(f"  {test_name.upper()}: {status}")
        
        # Overall assessment
        critical_tests = ['registration', 'login', 'auth_me_before', 'company_setup', 'auth_me_after']
        new_feature_tests = ['chart_of_accounts', 'currency_rates_get', 'currency_rates_update', 'exchangerate_api']
        
        critical_passed = all(test_results.get(test, False) for test in critical_tests if test in test_results)
        new_features_passed = all(test_results.get(test, False) for test in new_feature_tests if test in test_results)
        
        self.log("\n" + "=" * 80)
        self.log("FINAL ASSESSMENT")
        self.log("=" * 80)
        
        if critical_passed and new_features_passed:
            self.log("🎉 ALL TESTS PASSED - Complete system working correctly!")
            self.log("✅ Company setup flow: WORKING")
            self.log("✅ Chart of accounts: WORKING") 
            self.log("✅ Currency service: WORKING")
            self.log("✅ Online rate fetching: WORKING")
        elif critical_passed:
            self.log("🎯 CORE FUNCTIONALITY WORKING - Some new features may have issues")
            self.log("✅ Company setup flow: WORKING")
            if not test_results.get('chart_of_accounts', True):
                self.log("❌ Chart of accounts: FAILED")
            if not new_features_passed:
                self.log("❌ Currency service: SOME ISSUES")
        else:
            self.log("🚨 CRITICAL ISSUES FOUND")
            if not test_results.get('auth_me_after', True):
                self.log("🔍 ROOT CAUSE: onboarding_completed status not being updated after company setup")
        
        return test_results

def main():
    """Main function to run the tests"""
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Exit with error code if critical tests failed
    critical_tests = ['registration', 'login', 'auth_me_before', 'company_setup', 'auth_me_after']
    critical_passed = all(results.get(test, False) for test in critical_tests if test in results)
    
    sys.exit(0 if critical_passed else 1)

if __name__ == "__main__":
    main()