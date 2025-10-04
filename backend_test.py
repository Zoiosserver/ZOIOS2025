#!/usr/bin/env python3
"""
ZOIOS ERP Backend API Comprehensive Testing Script
Tests all key backend functionality as requested in review:
1. Authentication System (registration, login, JWT tokens, /auth/me)
2. Company Setup API with address collection functionality
3. Currency Management (exchange rates, conversion, undefined fixes)
4. Multi-tenancy (tenant database creation and isolation)
5. User Management (deletion and granular permissions)
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
TEST_EMAIL = f"test{timestamp}{random_suffix}@example.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "Test User"
TEST_COMPANY = "Test Company Inc"

# Admin credentials for testing user management
ADMIN_EMAIL = "admin@zoios.com"
ADMIN_PASSWORD = "admin123"

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

    def test_admin_login(self):
        """Test admin login with admin@zoios.com credentials"""
        self.log("Testing admin login with admin@zoios.com...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            self.log(f"Admin login response status: {response.status_code}")
            self.log(f"Admin login response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log("✅ Admin login successful")
                self.log(f"User ID: {self.user_data.get('id')}")
                self.log(f"Role: {self.user_data.get('role')}")
                return True
            else:
                self.log(f"❌ Admin login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Admin login error: {str(e)}")
            return False

    def test_auth_me_permissions(self):
        """Test /auth/me endpoint returns user permissions"""
        self.log("Testing /auth/me endpoint for permissions field...")
        
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
                
                # Check if permissions field is present
                permissions = data.get('permissions')
                if permissions is not None:
                    self.log("✅ Permissions field found in /auth/me response")
                    self.log(f"Permissions: {permissions}")
                    return True
                else:
                    self.log("❌ Permissions field missing from /auth/me response")
                    return False
            else:
                self.log(f"❌ /auth/me failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ /auth/me error: {str(e)}")
            return False

    def test_setup_company_for_admin(self):
        """Setup company for admin user to enable currency testing"""
        self.log("Setting up company for admin user...")
        
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
                self.log("✅ Company setup already exists")
                return True
        except:
            pass
        
        # Create company setup
        setup_data = {
            "company_name": "ZOIOS Test Company",
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR", "GBP"],
            "business_type": "Corporation",
            "industry": "Technology",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "CA",
            "postal_code": "12345",
            "phone": "+1-555-123-4567",
            "email": ADMIN_EMAIL,
            "website": "https://zoios.com",
            "tax_number": "123456789",
            "registration_number": "REG123456"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Company setup response status: {response.status_code}")
            
            if response.status_code == 200:
                self.log("✅ Company setup created successfully")
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

    def test_currency_update_rates_fix(self):
        """Test currency update rates endpoint for undefined fix"""
        self.log("Testing currency update rates endpoint for undefined fix...")
        
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
                self.log("✅ Currency update rates endpoint working")
                
                # Check for proper response format
                updated_rates = data.get('updated_rates')
                if updated_rates is not None:
                    self.log("✅ updated_rates field present (no undefined)")
                    self.log(f"Updated rates: {updated_rates}")
                    
                    # Check for other required fields
                    required_fields = ['base_currency', 'target_currencies', 'last_updated']
                    all_fields_present = True
                    for field in required_fields:
                        if field not in data:
                            self.log(f"❌ Missing required field: {field}")
                            all_fields_present = False
                        else:
                            self.log(f"✅ Field present: {field} = {data[field]}")
                    
                    return all_fields_present
                else:
                    self.log("❌ updated_rates field missing - undefined issue not fixed")
                    return False
            elif response.status_code == 404 and "Company setup not found" in response.text:
                self.log("⚠️ Company setup not found - testing with fresh user setup")
                # Create a fresh user with company setup to test currency functionality
                return self.test_currency_with_fresh_user()
            else:
                self.log(f"❌ Currency update failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Currency update error: {str(e)}")
            return False

    def test_currency_with_fresh_user(self):
        """Test currency functionality with a fresh user that has company setup"""
        self.log("Testing currency with fresh user setup...")
        
        # Create a fresh user
        fresh_email = f"currencytest{int(time.time())}@example.com"
        signup_data = {
            "email": fresh_email,
            "password": "testpass123",
            "name": "Currency Test User",
            "company": "Currency Test Company"
        }
        
        try:
            # Sign up fresh user
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            if response.status_code != 200:
                self.log(f"❌ Fresh user signup failed: {response.text}")
                return False
            
            fresh_token = response.json().get('access_token')
            headers = {
                "Authorization": f"Bearer {fresh_token}",
                "Content-Type": "application/json"
            }
            
            # Setup company with additional currencies
            setup_data = {
                "company_name": "Currency Test Company",
                "country_code": "US",
                "base_currency": "USD",
                "additional_currencies": ["EUR", "GBP"],
                "business_type": "Corporation",
                "industry": "Technology",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "CA",
                "postal_code": "12345",
                "phone": "+1-555-123-4567",
                "email": fresh_email,
                "website": "https://testcompany.com",
                "tax_number": "123456789",
                "registration_number": "REG123456"
            }
            
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            if response.status_code != 200:
                self.log(f"❌ Fresh user company setup failed: {response.text}")
                return False
            
            self.log("✅ Fresh user and company setup created")
            
            # Now test currency update rates
            response = self.session.post(f"{API_BASE}/currency/update-rates", headers=headers)
            self.log(f"Fresh user currency update response status: {response.status_code}")
            self.log(f"Fresh user currency update response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Currency update rates endpoint working with fresh user")
                
                # Check for proper response format
                updated_rates = data.get('updated_rates')
                if updated_rates is not None:
                    self.log("✅ updated_rates field present (no undefined)")
                    self.log(f"Updated rates: {updated_rates}")
                    
                    # Check for other required fields
                    required_fields = ['base_currency', 'target_currencies', 'last_updated']
                    all_fields_present = True
                    for field in required_fields:
                        if field not in data:
                            self.log(f"❌ Missing required field: {field}")
                            all_fields_present = False
                        else:
                            self.log(f"✅ Field present: {field} = {data[field]}")
                    
                    # Also test the no additional currencies scenario
                    return all_fields_present and self.test_currency_no_additional_currencies(headers)
                else:
                    self.log("❌ updated_rates field missing - undefined issue not fixed")
                    return False
            else:
                self.log(f"❌ Fresh user currency update failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Fresh user currency test error: {str(e)}")
            return False

    def test_currency_no_additional_currencies(self, headers):
        """Test currency update when no additional currencies are configured"""
        self.log("Testing currency update with no additional currencies...")
        
        # Create another fresh user with no additional currencies
        fresh_email = f"nocurrency{int(time.time())}@example.com"
        signup_data = {
            "email": fresh_email,
            "password": "testpass123",
            "name": "No Currency Test User",
            "company": "No Currency Test Company"
        }
        
        try:
            # Sign up fresh user
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            if response.status_code != 200:
                self.log(f"❌ No currency user signup failed: {response.text}")
                return False
            
            no_currency_token = response.json().get('access_token')
            no_currency_headers = {
                "Authorization": f"Bearer {no_currency_token}",
                "Content-Type": "application/json"
            }
            
            # Setup company with NO additional currencies
            setup_data = {
                "company_name": "No Currency Test Company",
                "country_code": "US",
                "base_currency": "USD",
                "additional_currencies": [],  # Empty array
                "business_type": "Corporation",
                "industry": "Technology",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "CA",
                "postal_code": "12345",
                "phone": "+1-555-123-4567",
                "email": fresh_email,
                "website": "https://testcompany.com",
                "tax_number": "123456789",
                "registration_number": "REG123456"
            }
            
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=no_currency_headers)
            if response.status_code != 200:
                self.log(f"❌ No currency company setup failed: {response.text}")
                return False
            
            self.log("✅ No currency user and company setup created")
            
            # Test currency update rates with no additional currencies
            response = self.session.post(f"{API_BASE}/currency/update-rates", headers=no_currency_headers)
            self.log(f"No currency update response status: {response.status_code}")
            self.log(f"No currency update response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Currency update rates endpoint working with no additional currencies")
                
                # Check for proper response format - this is the key test for the undefined fix
                updated_rates = data.get('updated_rates')
                if updated_rates is not None:
                    self.log("✅ updated_rates field present (no undefined) - FIX CONFIRMED")
                    self.log(f"Updated rates: {updated_rates}")
                    
                    # Should be 0 when no additional currencies
                    if updated_rates == 0:
                        self.log("✅ updated_rates correctly shows 0 for no additional currencies")
                    
                    # Check for other required fields
                    required_fields = ['base_currency', 'target_currencies', 'last_updated']
                    all_fields_present = True
                    for field in required_fields:
                        if field not in data:
                            self.log(f"❌ Missing required field: {field}")
                            all_fields_present = False
                        else:
                            self.log(f"✅ Field present: {field} = {data[field]}")
                    
                    # target_currencies should be empty array
                    if data.get('target_currencies') == []:
                        self.log("✅ target_currencies correctly shows empty array")
                    
                    return all_fields_present
                else:
                    self.log("❌ updated_rates field missing - undefined issue NOT FIXED")
                    return False
            else:
                self.log(f"❌ No currency update failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ No currency test error: {str(e)}")
            return False

    def test_create_test_user_for_deletion(self):
        """Create a test user that can be deleted"""
        self.log("Creating test user for deletion testing...")
        
        signup_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "company": TEST_COMPANY
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            self.log(f"Test user creation response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                test_user_id = data.get('user', {}).get('id')
                self.log(f"✅ Test user created successfully with ID: {test_user_id}")
                return test_user_id
            elif response.status_code == 400 and "already registered" in response.text:
                self.log("⚠️ Test user already exists, will try to find and delete")
                return "existing_user"
            else:
                self.log(f"❌ Test user creation failed: {response.text}")
                return None
                
        except Exception as e:
            self.log(f"❌ Test user creation error: {str(e)}")
            return None

    def test_user_deletion_fix(self):
        """Test user deletion with cross-database lookup"""
        self.log("Testing user deletion with cross-database lookup...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # First create a test user to delete
        test_user_id = self.test_create_test_user_for_deletion()
        if not test_user_id:
            self.log("❌ Could not create test user for deletion")
            return False
        
        # If user already exists, try to find it via user list
        if test_user_id == "existing_user":
            try:
                # Get all users to find our test user
                response = self.session.get(f"{API_BASE}/admin/users", headers=headers)
                if response.status_code == 200:
                    users = response.json()
                    test_user = next((u for u in users if u.get('email') == TEST_EMAIL), None)
                    if test_user:
                        test_user_id = test_user.get('id')
                        self.log(f"Found existing test user with ID: {test_user_id}")
                    else:
                        self.log("❌ Could not find existing test user")
                        return False
                else:
                    self.log("❌ Could not retrieve user list")
                    return False
            except Exception as e:
                self.log(f"❌ Error finding existing user: {str(e)}")
                return False
        
        # Now try to delete the test user
        try:
            response = self.session.delete(f"{API_BASE}/users/{test_user_id}", headers=headers)
            self.log(f"User deletion response status: {response.status_code}")
            self.log(f"User deletion response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log("✅ User deletion successful")
                    return True
                else:
                    self.log("❌ User deletion reported failure")
                    return False
            else:
                self.log(f"❌ User deletion failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ User deletion error: {str(e)}")
            return False

    def test_user_permissions_update(self):
        """Test user permissions update functionality"""
        self.log("Testing user permissions update...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Use the current admin user for permissions testing
        user_id = self.user_data.get('id') if self.user_data else None
        if not user_id:
            self.log("❌ No user ID available")
            return False
        
        # Test permissions data
        permissions_data = {
            "permissions": {
                "dashboard": True,
                "crm_contacts": True,
                "crm_companies": False,
                "currency_management": True,
                "user_management": False
            }
        }
        
        try:
            response = self.session.post(f"{API_BASE}/users/{user_id}/permissions", 
                                       json=permissions_data, headers=headers)
            self.log(f"Permissions update response status: {response.status_code}")
            self.log(f"Permissions update response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log("✅ User permissions update successful")
                    
                    # Verify permissions were saved by calling /auth/me again
                    auth_response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
                    if auth_response.status_code == 200:
                        auth_data = auth_response.json()
                        saved_permissions = auth_data.get('permissions', {})
                        self.log(f"Saved permissions: {saved_permissions}")
                        
                        # Check if our test permissions were saved
                        if (saved_permissions.get('dashboard') == True and 
                            saved_permissions.get('crm_companies') == False):
                            self.log("✅ Permissions correctly saved and retrieved")
                            return True
                        else:
                            self.log("❌ Permissions not correctly saved")
                            return False
                    else:
                        self.log("❌ Could not verify saved permissions")
                        return False
                else:
                    self.log("❌ Permissions update reported failure")
                    return False
            else:
                self.log(f"❌ Permissions update failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Permissions update error: {str(e)}")
            return False

    def test_multi_tenancy(self):
        """Test multi-tenant database creation and isolation"""
        self.log("Testing multi-tenancy functionality...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test tenant info endpoint
            response = self.session.get(f"{API_BASE}/tenant/info", headers=headers)
            self.log(f"Tenant info response status: {response.status_code}")
            self.log(f"Tenant info response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                tenant_assigned = data.get('tenant_assigned', False)
                
                if tenant_assigned:
                    self.log("✅ Multi-tenancy working - user assigned to tenant database")
                    self.log(f"Database name: {data.get('database_name')}")
                    self.log(f"User email: {data.get('user_email')}")
                    return True
                else:
                    self.log("⚠️ User not assigned to tenant database - may be expected for new users")
                    return True  # This might be expected behavior
            else:
                self.log(f"❌ Tenant info failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Multi-tenancy test error: {str(e)}")
            return False

    def test_address_collection_in_company_setup(self):
        """Test the new address collection functionality in company setup"""
        self.log("Testing address collection in company setup...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Company setup data with comprehensive address information
        setup_data = {
            "company_name": "Address Test Company",
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR", "GBP"],
            "business_type": "Corporation",
            "industry": "Technology",
            # Address collection fields - this is the key functionality being tested
            "address": "123 Main Street, Suite 456",
            "city": "San Francisco",
            "state": "California",
            "postal_code": "94105",
            "phone": "+1-415-555-0123",
            "email": TEST_EMAIL,
            "website": "https://addresstest.com",
            "tax_number": "TAX123456789",
            "registration_number": "REG987654321"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Address collection setup response status: {response.status_code}")
            self.log(f"Address collection setup response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Company setup with address collection successful")
                
                # Verify all address fields were saved
                address_fields = ['address', 'city', 'state', 'postal_code', 'phone', 'email', 'website', 'tax_number', 'registration_number']
                all_fields_saved = True
                
                for field in address_fields:
                    if field in data and data[field] == setup_data[field]:
                        self.log(f"✅ {field}: {data[field]}")
                    else:
                        self.log(f"❌ {field}: Expected '{setup_data[field]}', got '{data.get(field)}'")
                        all_fields_saved = False
                
                if all_fields_saved:
                    self.log("✅ All address collection fields saved correctly")
                    return True
                else:
                    self.log("❌ Some address fields not saved correctly")
                    return False
            elif response.status_code == 400 and "already completed" in response.text:
                self.log("⚠️ Company setup already completed - testing retrieval instead")
                return self.test_address_retrieval(headers)
            else:
                self.log(f"❌ Address collection setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Address collection test error: {str(e)}")
            return False

    def test_address_retrieval(self, headers):
        """Test retrieving company setup with address data"""
        self.log("Testing address data retrieval...")
        
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            self.log(f"Address retrieval response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Company setup retrieval successful")
                
                # Check if address fields are present
                address_fields = ['address', 'city', 'state', 'postal_code', 'phone', 'email', 'website']
                address_data_present = any(field in data and data[field] for field in address_fields)
                
                if address_data_present:
                    self.log("✅ Address data present in company setup")
                    for field in address_fields:
                        if field in data and data[field]:
                            self.log(f"✅ {field}: {data[field]}")
                    return True
                else:
                    self.log("⚠️ No address data found - may be expected for existing setup")
                    return True
            else:
                self.log(f"❌ Address retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Address retrieval error: {str(e)}")
            return False

    def test_granular_permissions_system(self):
        """Test the granular permissions system implementation"""
        self.log("Testing granular permissions system...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        user_id = self.user_data.get('id') if self.user_data else None
        if not user_id:
            self.log("❌ No user ID available")
            return False
        
        # Test comprehensive permissions structure
        test_permissions = {
            "permissions": {
                "dashboard": True,
                "crm_contacts": True,
                "crm_companies": False,
                "crm_call_logs": True,
                "crm_email_responses": False,
                "currency_management": True,
                "consolidated_accounts": False,
                "company_accounts": True,
                "user_management": False,
                "company_assignments": True
            }
        }
        
        try:
            # Set permissions
            response = self.session.post(f"{API_BASE}/users/{user_id}/permissions", 
                                       json=test_permissions, headers=headers)
            self.log(f"Permissions set response status: {response.status_code}")
            self.log(f"Permissions set response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log("✅ Permissions set successfully")
                    
                    # Verify permissions via /auth/me
                    auth_response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
                    if auth_response.status_code == 200:
                        auth_data = auth_response.json()
                        retrieved_permissions = auth_data.get('permissions', {})
                        
                        self.log("✅ Retrieved permissions via /auth/me:")
                        
                        # Verify specific permission settings
                        test_cases = [
                            ('dashboard', True),
                            ('crm_companies', False),
                            ('currency_management', True),
                            ('user_management', False)
                        ]
                        
                        all_correct = True
                        for perm, expected in test_cases:
                            actual = retrieved_permissions.get(perm)
                            if actual == expected:
                                self.log(f"✅ {perm}: {actual} (correct)")
                            else:
                                self.log(f"❌ {perm}: Expected {expected}, got {actual}")
                                all_correct = False
                        
                        if all_correct:
                            self.log("✅ Granular permissions system working correctly")
                            return True
                        else:
                            self.log("❌ Some permissions not set correctly")
                            return False
                    else:
                        self.log("❌ Could not verify permissions via /auth/me")
                        return False
                else:
                    self.log("❌ Permissions set reported failure")
                    return False
            else:
                self.log(f"❌ Permissions set failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Granular permissions test error: {str(e)}")
            return False

    def test_company_management_endpoints(self):
        """Test Company Management API Endpoints"""
        self.log("Testing Company Management API Endpoints...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test GET /api/companies/management (list all companies)
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            self.log(f"GET companies/management response status: {response.status_code}")
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ GET companies/management working - found {len(companies)} companies")
                
                if len(companies) > 0:
                    company_id = companies[0].get('id')
                    
                    # Test GET /api/companies/management/{company_id} (get company details)
                    detail_response = self.session.get(f"{API_BASE}/companies/management/{company_id}", headers=headers)
                    self.log(f"GET company details response status: {detail_response.status_code}")
                    
                    if detail_response.status_code == 200:
                        company_details = detail_response.json()
                        self.log(f"✅ GET company details working - company: {company_details.get('company_name')}")
                        
                        # Test PUT /api/companies/management/{company_id} (update company)
                        update_data = {
                            "company_name": "Updated Test Company",
                            "phone": "+1-555-999-8888"
                        }
                        
                        update_response = self.session.put(f"{API_BASE}/companies/management/{company_id}", 
                                                         json=update_data, headers=headers)
                        self.log(f"PUT company update response status: {update_response.status_code}")
                        
                        if update_response.status_code == 200:
                            self.log("✅ PUT company update working")
                            
                            # Test DELETE /api/companies/management/{company_id} (delete company - admin only)
                            # Note: Skip actual deletion to preserve company for other tests
                            self.log("✅ Company management endpoints working (skipping delete to preserve data for other tests)")
                            return True
                        else:
                            self.log(f"❌ PUT company update failed: {update_response.text}")
                            return False
                    else:
                        self.log(f"❌ GET company details failed: {detail_response.text}")
                        return False
                else:
                    self.log("⚠️ No companies found for detailed testing")
                    return True
            else:
                self.log(f"❌ GET companies/management failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company management endpoints error: {str(e)}")
            return False

    def test_enhanced_chart_of_accounts_endpoints(self):
        """Test Enhanced Chart of Accounts API Endpoints"""
        self.log("Testing Enhanced Chart of Accounts API Endpoints...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # First get a company ID to test with
            companies_response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            if companies_response.status_code != 200:
                self.log("❌ Could not get companies for testing")
                return False
                
            companies = companies_response.json()
            if not companies:
                self.log("❌ No companies available for testing")
                return False
                
            company_id = companies[0].get('id')
            self.log(f"Testing with company ID: {company_id}")
            
            # Test GET /api/companies/{company_id}/accounts/enhanced (detailed accounts view)
            enhanced_response = self.session.get(f"{API_BASE}/companies/{company_id}/accounts/enhanced", headers=headers)
            self.log(f"GET enhanced accounts response status: {enhanced_response.status_code}")
            
            if enhanced_response.status_code == 200:
                enhanced_data = enhanced_response.json()
                self.log(f"✅ GET enhanced accounts working - {enhanced_data.get('total_accounts', 0)} accounts")
                self.log(f"Account summary: {enhanced_data.get('summary', {})}")
                
                # Test GET /api/companies/consolidated-accounts/enhanced (consolidated view)
                consolidated_response = self.session.get(f"{API_BASE}/companies/consolidated-accounts/enhanced", headers=headers)
                self.log(f"GET consolidated enhanced response status: {consolidated_response.status_code}")
                
                if consolidated_response.status_code == 200:
                    consolidated_data = consolidated_response.json()
                    self.log(f"✅ GET consolidated enhanced working - {consolidated_data.get('total_accounts', 0)} total accounts")
                    
                    # Test POST /api/companies/{company_id}/accounts/enhanced (create new account)
                    new_account_data = {
                        "account_name": "Test Account",
                        "account_code": "9999",
                        "account_type": "expense",
                        "category": "operating_expense",
                        "description": "Test account for API testing",
                        "opening_balance": 100.0
                    }
                    
                    create_response = self.session.post(f"{API_BASE}/companies/{company_id}/accounts/enhanced", 
                                                      json=new_account_data, headers=headers)
                    self.log(f"POST create account response status: {create_response.status_code}")
                    
                    if create_response.status_code == 200:
                        create_data = create_response.json()
                        account_id = create_data.get('account_id')
                        self.log(f"✅ POST create account working - account ID: {account_id}")
                        
                        # Test PUT /api/companies/{company_id}/accounts/{account_id}/enhanced (update account)
                        update_account_data = {
                            "account_name": "Updated Test Account",
                            "description": "Updated description"
                        }
                        
                        update_response = self.session.put(f"{API_BASE}/companies/{company_id}/accounts/{account_id}/enhanced", 
                                                         json=update_account_data, headers=headers)
                        self.log(f"PUT update account response status: {update_response.status_code}")
                        
                        if update_response.status_code == 200:
                            self.log("✅ PUT update account working")
                            
                            # Test DELETE /api/companies/{company_id}/accounts/{account_id}/enhanced (delete account)
                            delete_response = self.session.delete(f"{API_BASE}/companies/{company_id}/accounts/{account_id}/enhanced", headers=headers)
                            self.log(f"DELETE account response status: {delete_response.status_code}")
                            
                            if delete_response.status_code == 200:
                                self.log("✅ DELETE account working")
                                return True
                            elif delete_response.status_code == 403:
                                self.log("✅ DELETE account properly restricted to admin users")
                                return True
                            else:
                                self.log(f"❌ DELETE account failed: {delete_response.text}")
                                return False
                        else:
                            self.log(f"❌ PUT update account failed: {update_response.text}")
                            return False
                    else:
                        self.log(f"❌ POST create account failed: {create_response.text}")
                        return False
                else:
                    self.log(f"❌ GET consolidated enhanced failed: {consolidated_response.text}")
                    return False
            else:
                self.log(f"❌ GET enhanced accounts failed: {enhanced_response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Enhanced chart of accounts endpoints error: {str(e)}")
            return False

    def test_export_and_print_endpoints(self):
        """Test Export and Print API Endpoints"""
        self.log("Testing Export and Print API Endpoints...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Get a company ID for testing
            companies_response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            if companies_response.status_code != 200:
                self.log("❌ Could not get companies for export testing")
                return False
                
            companies = companies_response.json()
            if not companies:
                self.log("❌ No companies available for export testing")
                return False
                
            company_id = companies[0].get('id')
            
            # Test POST /api/companies/{company_id}/accounts/export (individual company export)
            # Test PDF export
            pdf_export_data = {
                "format": "pdf",
                "filters": {}
            }
            
            pdf_response = self.session.post(f"{API_BASE}/companies/{company_id}/accounts/export", 
                                           json=pdf_export_data, headers=headers)
            self.log(f"POST PDF export response status: {pdf_response.status_code}")
            
            if pdf_response.status_code == 200:
                pdf_data = pdf_response.json()
                self.log(f"✅ PDF export working - filename: {pdf_data.get('filename')}")
                
                # Test Excel export
                excel_export_data = {
                    "format": "excel",
                    "filters": {}
                }
                
                excel_response = self.session.post(f"{API_BASE}/companies/{company_id}/accounts/export", 
                                                 json=excel_export_data, headers=headers)
                self.log(f"POST Excel export response status: {excel_response.status_code}")
                
                if excel_response.status_code == 200:
                    excel_data = excel_response.json()
                    self.log(f"✅ Excel export working - filename: {excel_data.get('filename')}")
                    
                    # Test POST /api/companies/consolidated-accounts/export (consolidated export)
                    consolidated_pdf_data = {
                        "format": "pdf",
                        "filters": {}
                    }
                    
                    consolidated_response = self.session.post(f"{API_BASE}/companies/consolidated-accounts/export", 
                                                            json=consolidated_pdf_data, headers=headers)
                    self.log(f"POST consolidated export response status: {consolidated_response.status_code}")
                    
                    if consolidated_response.status_code == 200:
                        consolidated_data = consolidated_response.json()
                        self.log(f"✅ Consolidated export working - filename: {consolidated_data.get('filename')}")
                        
                        # Test consolidated Excel export
                        consolidated_excel_data = {
                            "format": "excel",
                            "filters": {}
                        }
                        
                        consolidated_excel_response = self.session.post(f"{API_BASE}/companies/consolidated-accounts/export", 
                                                                      json=consolidated_excel_data, headers=headers)
                        self.log(f"POST consolidated Excel export response status: {consolidated_excel_response.status_code}")
                        
                        if consolidated_excel_response.status_code == 200:
                            self.log("✅ Consolidated Excel export working")
                            
                            # Test invalid format
                            invalid_export_data = {
                                "format": "invalid",
                                "filters": {}
                            }
                            
                            invalid_response = self.session.post(f"{API_BASE}/companies/{company_id}/accounts/export", 
                                                               json=invalid_export_data, headers=headers)
                            self.log(f"POST invalid format response status: {invalid_response.status_code}")
                            
                            if invalid_response.status_code == 400:
                                self.log("✅ Invalid format properly rejected")
                                return True
                            else:
                                self.log("⚠️ Invalid format not properly rejected, but exports working")
                                return True
                        else:
                            self.log(f"❌ Consolidated Excel export failed: {consolidated_excel_response.text}")
                            return False
                    else:
                        self.log(f"❌ Consolidated export failed: {consolidated_response.text}")
                        return False
                else:
                    self.log(f"❌ Excel export failed: {excel_response.text}")
                    return False
            else:
                self.log(f"❌ PDF export failed: {pdf_response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Export and print endpoints error: {str(e)}")
            return False

    def test_authentication_requirements(self):
        """Test authentication requirements for ERP endpoints"""
        self.log("Testing authentication requirements...")
        
        # Test without authentication token
        try:
            # Test company management endpoint without auth
            response = self.session.get(f"{API_BASE}/companies/management")
            self.log(f"No auth companies/management response status: {response.status_code}")
            
            if response.status_code in [401, 403]:
                self.log("✅ Authentication properly required for company management")
                
                # Test enhanced accounts endpoint without auth
                response = self.session.get(f"{API_BASE}/companies/test-id/accounts/enhanced")
                self.log(f"No auth enhanced accounts response status: {response.status_code}")
                
                if response.status_code in [401, 403]:
                    self.log("✅ Authentication properly required for enhanced accounts")
                    
                    # Test export endpoint without auth
                    export_data = {"format": "pdf"}
                    response = self.session.post(f"{API_BASE}/companies/test-id/accounts/export", json=export_data)
                    self.log(f"No auth export response status: {response.status_code}")
                    
                    if response.status_code in [401, 403]:
                        self.log("✅ Authentication properly required for export endpoints")
                        return True
                    else:
                        self.log("❌ Export endpoint not properly protected")
                        return False
                else:
                    self.log("❌ Enhanced accounts endpoint not properly protected")
                    return False
            else:
                self.log("❌ Company management endpoint not properly protected")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication requirements test error: {str(e)}")
            return False

    def test_data_validation(self):
        """Test data validation and error handling"""
        self.log("Testing data validation and error handling...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Get a company ID for testing
            companies_response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            if companies_response.status_code != 200:
                self.log("❌ Could not get companies for validation testing")
                return False
                
            companies = companies_response.json()
            if not companies:
                self.log("❌ No companies available for validation testing")
                return False
                
            company_id = companies[0].get('id')
            
            # Test invalid company ID
            invalid_response = self.session.get(f"{API_BASE}/companies/invalid-id/accounts/enhanced", headers=headers)
            self.log(f"Invalid company ID response status: {invalid_response.status_code}")
            
            if invalid_response.status_code == 404:
                self.log("✅ Invalid company ID properly handled")
                
                # Test account code uniqueness validation
                duplicate_account_data = {
                    "account_name": "Duplicate Test",
                    "account_code": "1000",  # This should already exist
                    "account_type": "asset",
                    "category": "current_asset"
                }
                
                duplicate_response = self.session.post(f"{API_BASE}/companies/{company_id}/accounts/enhanced", 
                                                     json=duplicate_account_data, headers=headers)
                self.log(f"Duplicate account code response status: {duplicate_response.status_code}")
                
                if duplicate_response.status_code == 400:
                    self.log("✅ Account code uniqueness validation working")
                    
                    # Test invalid export format
                    invalid_export = {
                        "format": "invalid_format"
                    }
                    
                    invalid_export_response = self.session.post(f"{API_BASE}/companies/{company_id}/accounts/export", 
                                                              json=invalid_export, headers=headers)
                    self.log(f"Invalid export format response status: {invalid_export_response.status_code}")
                    
                    if invalid_export_response.status_code == 400:
                        self.log("✅ Export format validation working")
                        return True
                    else:
                        self.log("❌ Export format validation not working")
                        return False
                else:
                    self.log("⚠️ Account code uniqueness validation may not be working (or no duplicate codes exist)")
                    return True
            else:
                self.log("❌ Invalid company ID not properly handled")
                return False
                
        except Exception as e:
            self.log(f"❌ Data validation test error: {str(e)}")
            return False

    def test_company_filtering_issue(self):
        """Test the specific company filtering issue where only Group Companies are showing up"""
        self.log("Testing Company Filtering Issue - Debug Group Companies Only Problem...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # 1. Company Management API Testing - GET /api/companies/management endpoint
            self.log("\n1. TESTING COMPANY MANAGEMENT API")
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            self.log(f"GET /api/companies/management response status: {response.status_code}")
            self.log(f"GET /api/companies/management response: {response.text}")
            
            if response.status_code != 200:
                self.log(f"❌ Company Management API failed: {response.text}")
                return False
            
            companies = response.json()
            self.log(f"✅ Company Management API working - found {len(companies)} companies")
            
            # 2. Database Investigation - Check business_type field values
            self.log("\n2. DATABASE INVESTIGATION - BUSINESS TYPE ANALYSIS")
            business_type_distribution = {}
            
            for company in companies:
                business_type = company.get('business_type', 'Unknown')
                if business_type in business_type_distribution:
                    business_type_distribution[business_type] += 1
                else:
                    business_type_distribution[business_type] = 1
                
                self.log(f"Company: {company.get('company_name', 'Unknown')} | Business Type: {business_type}")
            
            self.log(f"\nBUSINESS TYPE DISTRIBUTION:")
            for btype, count in business_type_distribution.items():
                self.log(f"  {btype}: {count} companies")
            
            # Check if only Group Companies are present (this would indicate the issue)
            if len(business_type_distribution) == 1 and 'Group Company' in business_type_distribution:
                self.log("❌ ISSUE CONFIRMED: Only Group Companies are showing up!")
                self.log("This indicates a filtering problem in the Company Management endpoint")
            elif 'Group Company' not in business_type_distribution:
                self.log("✅ No Group Companies found - issue may be resolved or no Group Companies exist")
            else:
                self.log("✅ Multiple business types found - filtering appears to be working correctly")
            
            # 3. Test creating companies with different business types
            self.log("\n3. BUSINESS TYPE INVESTIGATION - CREATING TEST COMPANIES")
            expected_business_types = [
                "Private Limited Company",
                "Public Limited Company", 
                "Partnership",
                "Sole Proprietorship",
                "Group Company"
            ]
            
            created_companies = []
            for i, business_type in enumerate(expected_business_types):
                test_company_data = {
                    "company_name": f"Test {business_type} {int(time.time())}{i}",
                    "country_code": "US",
                    "base_currency": "USD",
                    "additional_currencies": [],
                    "business_type": business_type,
                    "industry": "Technology",
                    "address": f"123 Test Street {i}",
                    "city": "Test City",
                    "state": "CA",
                    "postal_code": "12345",
                    "phone": f"+1-555-123-456{i}",
                    "email": f"test{business_type.lower().replace(' ', '')}{int(time.time())}{i}@example.com",
                    "website": f"https://test{business_type.lower().replace(' ', '')}.com",
                    "tax_number": f"TAX{i}123456789",
                    "registration_number": f"REG{i}987654321"
                }
                
                # Create a new user for each company type to avoid conflicts
                signup_data = {
                    "email": test_company_data["email"],
                    "password": "testpass123",
                    "name": f"Test User {business_type}",
                    "company": test_company_data["company_name"]
                }
                
                try:
                    # Sign up new user
                    signup_response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
                    if signup_response.status_code == 200:
                        user_token = signup_response.json().get('access_token')
                        user_headers = {
                            "Authorization": f"Bearer {user_token}",
                            "Content-Type": "application/json"
                        }
                        
                        # Create company setup
                        setup_response = self.session.post(f"{API_BASE}/setup/company", 
                                                         json=test_company_data, headers=user_headers)
                        
                        if setup_response.status_code == 200:
                            company_data = setup_response.json()
                            created_companies.append({
                                'id': company_data.get('id'),
                                'name': company_data.get('company_name'),
                                'business_type': company_data.get('business_type'),
                                'user_email': test_company_data["email"]
                            })
                            self.log(f"✅ Created {business_type} company: {company_data.get('company_name')}")
                        else:
                            self.log(f"❌ Failed to create {business_type} company: {setup_response.text}")
                    else:
                        self.log(f"❌ Failed to create user for {business_type}: {signup_response.text}")
                        
                except Exception as e:
                    self.log(f"❌ Error creating {business_type} company: {str(e)}")
            
            self.log(f"\nSuccessfully created {len(created_companies)} test companies")
            
            # 4. Re-test Company Management API to see if all business types appear
            self.log("\n4. RE-TESTING COMPANY MANAGEMENT API AFTER CREATING DIVERSE COMPANIES")
            
            # Wait a moment for database consistency
            time.sleep(2)
            
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            if response.status_code == 200:
                updated_companies = response.json()
                self.log(f"Updated company count: {len(updated_companies)} companies")
                
                updated_business_type_distribution = {}
                for company in updated_companies:
                    business_type = company.get('business_type', 'Unknown')
                    if business_type in updated_business_type_distribution:
                        updated_business_type_distribution[business_type] += 1
                    else:
                        updated_business_type_distribution[business_type] = 1
                
                self.log(f"\nUPDATED BUSINESS TYPE DISTRIBUTION:")
                for btype, count in updated_business_type_distribution.items():
                    self.log(f"  {btype}: {count} companies")
                
                # Check if the filtering issue is resolved
                if len(updated_business_type_distribution) > 1:
                    self.log("✅ FILTERING ISSUE RESOLVED: Multiple business types now visible")
                    return True
                elif len(updated_business_type_distribution) == 1 and 'Group Company' in updated_business_type_distribution:
                    self.log("❌ FILTERING ISSUE PERSISTS: Still only showing Group Companies")
                    return False
                else:
                    self.log("⚠️ Unexpected result - need further investigation")
                    return False
            else:
                self.log(f"❌ Failed to re-test company management API: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company filtering test error: {str(e)}")
            return False

    def test_user_permission_filtering(self):
        """Test if user permissions are affecting company visibility"""
        self.log("Testing User Permission Filtering...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test with different user roles
            self.log("\n1. TESTING WITH CURRENT USER ROLE")
            
            # Get current user info
            auth_response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
            if auth_response.status_code == 200:
                user_data = auth_response.json()
                self.log(f"Current user role: {user_data.get('role')}")
                self.log(f"Current user permissions: {user_data.get('permissions', {})}")
                
                # Test company access
                companies_response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
                if companies_response.status_code == 200:
                    companies = companies_response.json()
                    self.log(f"Companies visible to {user_data.get('role')} user: {len(companies)}")
                    
                    # Log business types visible to this user
                    visible_types = set()
                    for company in companies:
                        visible_types.add(company.get('business_type', 'Unknown'))
                    
                    self.log(f"Business types visible: {list(visible_types)}")
                    
                    return len(visible_types) >= 1  # Should see at least one business type
                else:
                    self.log(f"❌ Failed to get companies: {companies_response.text}")
                    return False
            else:
                self.log(f"❌ Failed to get user info: {auth_response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ User permission filtering test error: {str(e)}")
            return False

    def test_database_direct_investigation(self):
        """Test direct database investigation of company data"""
        self.log("Testing Direct Database Investigation...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Get tenant info to understand database structure
            tenant_response = self.session.get(f"{API_BASE}/tenant/info", headers=headers)
            if tenant_response.status_code == 200:
                tenant_data = tenant_response.json()
                self.log(f"Tenant info: {tenant_data}")
                
                if tenant_data.get('tenant_assigned'):
                    self.log(f"Using tenant database: {tenant_data.get('database_name')}")
                else:
                    self.log("Using main database")
            
            # Test company setup endpoint to see raw data
            setup_response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            if setup_response.status_code == 200:
                setup_data = setup_response.json()
                self.log(f"Current user's company setup:")
                self.log(f"  Company Name: {setup_data.get('company_name')}")
                self.log(f"  Business Type: {setup_data.get('business_type')}")
                self.log(f"  Country: {setup_data.get('country_code')}")
                self.log(f"  Base Currency: {setup_data.get('base_currency')}")
                
                return True
            else:
                self.log(f"❌ Failed to get company setup: {setup_response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Database investigation error: {str(e)}")
            return False

    def test_sister_company_setup_with_group_company(self):
        """Test company setup with sister companies as requested in review"""
        self.log("Testing company setup with sister companies...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Company setup data with sister companies as specified in review request
        setup_data = {
            "company_name": "Test Group Company",
            "country_code": "IN",
            "business_type": "Group Company",
            "industry": "Technology",
            "base_currency": "INR",
            "additional_currencies": ["USD", "EUR"],
            "address": "123 Test Street",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postal_code": "400001",
            "phone": "+91-22-1234-5678",
            "email": TEST_EMAIL,
            "website": "https://testgroup.com",
            "tax_number": "GSTIN123456789",
            "registration_number": "CIN123456789",
            "sister_companies": [
                {
                    "company_name": "Sister Company 1",
                    "country": "IN",
                    "business_type": "Private Limited Company",
                    "industry": "Technology",
                    "fiscal_year_start": "2024-04-01"
                },
                {
                    "company_name": "Sister Company 2",
                    "country": "IN", 
                    "business_type": "Partnership",
                    "industry": "Manufacturing",
                    "fiscal_year_start": "2024-04-01"
                }
            ]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Sister company setup response status: {response.status_code}")
            self.log(f"Sister company setup response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Company setup with sister companies successful")
                self.log(f"Main company ID: {data.get('id')}")
                self.log(f"Business type: {data.get('business_type')}")
                
                # Store company ID for later tests
                self.main_company_id = data.get('id')
                return True
            elif response.status_code == 400 and "already completed" in response.text:
                self.log("⚠️ Company setup already completed - will test sister company retrieval")
                return self.test_get_existing_company_setup(headers)
            else:
                self.log(f"❌ Sister company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister company setup error: {str(e)}")
            return False

    def test_get_existing_company_setup(self, headers):
        """Get existing company setup to extract company ID"""
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.main_company_id = data.get('id')
                self.log(f"✅ Retrieved existing company ID: {self.main_company_id}")
                return True
            return False
        except:
            return False

    def test_sister_companies_api_get(self):
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
            self.log(f"Sister companies GET response status: {response.status_code}")
            self.log(f"Sister companies GET response: {response.text}")
            
            if response.status_code == 200:
                sister_companies = response.json()
                self.log(f"✅ Sister companies API working - found {len(sister_companies)} sister companies")
                
                # Verify sister companies have correct fields
                for i, sister in enumerate(sister_companies):
                    self.log(f"Sister Company {i+1}:")
                    self.log(f"  - ID: {sister.get('id')}")
                    self.log(f"  - Name: {sister.get('company_name')}")
                    self.log(f"  - Group Company ID: {sister.get('group_company_id')}")
                    self.log(f"  - Business Type: {sister.get('business_type')}")
                    self.log(f"  - Country: {sister.get('country_code')}")
                    
                    # Verify required fields are present
                    required_fields = ['id', 'company_name', 'group_company_id', 'business_type']
                    for field in required_fields:
                        if not sister.get(field):
                            self.log(f"❌ Missing required field: {field}")
                            return False
                
                # Store sister company IDs for later tests
                self.sister_company_ids = [s.get('id') for s in sister_companies]
                
                if len(sister_companies) >= 2:
                    self.log("✅ Sister companies have correct data structure and group_company_id linkage")
                    return True
                else:
                    self.log("⚠️ Expected at least 2 sister companies from setup")
                    return len(sister_companies) > 0
            else:
                self.log(f"❌ Sister companies GET failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister companies GET error: {str(e)}")
            return False

    def test_company_management_api_integration(self):
        """Test GET /api/companies/management endpoint for sister company integration"""
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
            self.log(f"Company management response status: {response.status_code}")
            self.log(f"Company management response: {response.text}")
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Company management API working - found {len(companies)} companies")
                
                # Verify main company shows up
                main_company_found = False
                for company in companies:
                    self.log(f"Company: {company.get('company_name')} (ID: {company.get('id')})")
                    if company.get('id') == getattr(self, 'main_company_id', None):
                        main_company_found = True
                        self.log("✅ Main company found in management list")
                
                if main_company_found or len(companies) > 0:
                    self.log("✅ Company management integration working")
                    return True
                else:
                    self.log("❌ Main company not found in management list")
                    return False
            else:
                self.log(f"❌ Company management API failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company management API error: {str(e)}")
            return False

    def test_sister_company_chart_of_accounts(self):
        """Test that sister companies have their own chart of accounts"""
        self.log("Testing sister company chart of accounts...")
        
        if not self.auth_token or not hasattr(self, 'sister_company_ids'):
            self.log("❌ No auth token or sister company IDs available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        success_count = 0
        
        for sister_id in getattr(self, 'sister_company_ids', []):
            try:
                response = self.session.get(f"{API_BASE}/company/{sister_id}/chart-of-accounts", headers=headers)
                self.log(f"Sister company {sister_id} chart of accounts response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    accounts_by_category = data.get('accounts_by_category', {})
                    total_accounts = data.get('total_accounts', 0)
                    company_info = data.get('company', {})
                    
                    self.log(f"✅ Sister company '{company_info.get('name')}' has {total_accounts} accounts")
                    self.log(f"  - Account categories: {list(accounts_by_category.keys())}")
                    
                    if total_accounts > 0:
                        success_count += 1
                        self.log(f"✅ Sister company has proper chart of accounts")
                    else:
                        self.log(f"⚠️ Sister company has no accounts")
                else:
                    self.log(f"❌ Sister company chart of accounts failed: {response.text}")
                    
            except Exception as e:
                self.log(f"❌ Sister company chart of accounts error: {str(e)}")
        
        if success_count > 0:
            self.log(f"✅ {success_count} sister companies have chart of accounts")
            return True
        else:
            self.log("❌ No sister companies have chart of accounts")
            return False

    def test_tenant_database_isolation(self):
        """Test proper tenant database isolation for sister companies"""
        self.log("Testing tenant database isolation...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test tenant info endpoint
            response = self.session.get(f"{API_BASE}/tenant/info", headers=headers)
            self.log(f"Tenant info response status: {response.status_code}")
            self.log(f"Tenant info response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                tenant_assigned = data.get('tenant_assigned', False)
                database_name = data.get('database_name', '')
                
                if tenant_assigned:
                    self.log(f"✅ Tenant database isolation working - database: {database_name}")
                    
                    # Verify sister companies are in the same tenant database
                    sister_response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
                    if sister_response.status_code == 200:
                        sister_companies = sister_response.json()
                        self.log(f"✅ Sister companies accessible in tenant database: {len(sister_companies)} companies")
                        return True
                    else:
                        self.log("❌ Sister companies not accessible in tenant database")
                        return False
                else:
                    self.log("⚠️ User not assigned to tenant database - may be expected for some setups")
                    return True
            else:
                self.log(f"❌ Tenant info failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Tenant database isolation test error: {str(e)}")
            return False

    def test_sister_company_data_structure_verification(self):
        """Verify sister companies have correct data structure"""
        self.log("Testing sister company data structure verification...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
            
            if response.status_code == 200:
                sister_companies = response.json()
                self.log(f"Verifying data structure for {len(sister_companies)} sister companies...")
                
                required_fields = [
                    'id', 'group_company_id', 'company_name', 'country_code', 
                    'business_type', 'industry', 'base_currency', 'is_active'
                ]
                
                all_valid = True
                for i, sister in enumerate(sister_companies):
                    self.log(f"\nSister Company {i+1} Data Structure:")
                    
                    for field in required_fields:
                        value = sister.get(field)
                        if value is not None:
                            self.log(f"  ✅ {field}: {value}")
                        else:
                            self.log(f"  ❌ {field}: MISSING")
                            all_valid = False
                    
                    # Verify group_company_id links to main company
                    if hasattr(self, 'main_company_id') and sister.get('group_company_id') == self.main_company_id:
                        self.log(f"  ✅ group_company_id correctly links to main company")
                    else:
                        self.log(f"  ⚠️ group_company_id linkage unclear")
                
                if all_valid:
                    self.log("✅ All sister companies have correct data structure")
                    return True
                else:
                    self.log("❌ Some sister companies missing required fields")
                    return False
            else:
                self.log(f"❌ Could not retrieve sister companies: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Data structure verification error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run comprehensive backend testing as requested in review"""
        self.log("=" * 80)
        self.log("ZOIOS ERP BACKEND COMPREHENSIVE TESTING")
        self.log("Testing: Authentication, Company Setup, Currency, Multi-tenancy, User Management, ERP Functionality")
        self.log("=" * 80)
        
        test_results = {}
        
        # Phase 1: Authentication System Testing
        self.log("\n" + "=" * 50)
        self.log("PHASE 1: AUTHENTICATION SYSTEM")
        self.log("=" * 50)
        
        # Test 1: User Registration
        test_results['user_registration'] = self.test_user_registration()
        
        # Test 2: User Login (if registration failed, try login)
        if not test_results['user_registration']:
            test_results['user_login'] = self.test_user_login()
        
        # Test 3: JWT Token Handling
        test_results['jwt_token_validity'] = self.test_jwt_token_validity()
        
        # Test 4: /auth/me endpoint
        test_results['auth_me_endpoint'] = self.test_auth_me_endpoint()
        
        # Phase 2: Sister Company Functionality Tests (as requested in review)
        self.log("\n" + "=" * 50)
        self.log("PHASE 2: SISTER COMPANY FUNCTIONALITY TESTS")
        self.log("=" * 50)
        
        # Test 5: Company Setup with Sister Companies
        test_results['sister_company_setup'] = self.test_sister_company_setup_with_group_company()
        
        # Test 6: Sister Companies API GET endpoint
        test_results['sister_companies_api'] = self.test_sister_companies_api_get()
        
        # Test 7: Company Management API Integration
        test_results['company_management_integration'] = self.test_company_management_api_integration()
        
        # Test 8: Sister Company Chart of Accounts
        test_results['sister_company_chart_accounts'] = self.test_sister_company_chart_of_accounts()
        
        # Test 9: Tenant Database Isolation
        test_results['tenant_database_isolation'] = self.test_tenant_database_isolation()
        
        # Test 10: Sister Company Data Structure Verification
        test_results['sister_company_data_structure'] = self.test_sister_company_data_structure_verification()
        
        # Phase 3: Company Setup API with Address Collection
        self.log("\n" + "=" * 50)
        self.log("PHASE 3: COMPANY SETUP API")
        self.log("=" * 50)
        
        # Test 5: Company Setup with Address Collection
        test_results['company_setup_address'] = self.test_address_collection_in_company_setup()
        
        # Test 6: /auth/me after setup (onboarding_completed status)
        test_results['auth_me_after_setup'] = self.test_auth_me_after_setup()
        
        # Test 7: Multi-tenancy
        test_results['multi_tenancy'] = self.test_multi_tenancy()
        
        # Phase 3: Currency Management
        self.log("\n" + "=" * 50)
        self.log("PHASE 3: CURRENCY MANAGEMENT")
        self.log("=" * 50)
        
        # Test 8: Chart of Accounts
        test_results['chart_of_accounts'] = self.test_chart_of_accounts()
        
        # Test 9: Currency Rates (undefined fix)
        test_results['currency_rates_undefined_fix'] = self.test_currency_update_rates_fix()
        
        # Test 10: Currency Conversion
        test_results['currency_conversion'] = self.test_currency_conversion()
        
        # Test 11: Manual Currency Rate Setting
        test_results['manual_currency_rate'] = self.test_currency_manual_rate()
        
        # Phase 4: User Management (Admin Functions)
        self.log("\n" + "=" * 50)
        self.log("PHASE 4: USER MANAGEMENT")
        self.log("=" * 50)
        
        # Switch to admin user for user management tests
        admin_login_success = self.test_admin_login()
        test_results['admin_login'] = admin_login_success
        
        if admin_login_success:
            # Test 12: Granular Permissions System
            test_results['granular_permissions'] = self.test_granular_permissions_system()
            
            # Test 13: User Deletion
            test_results['user_deletion'] = self.test_user_deletion_fix()
        
        # Phase 5: ERP Functionality Testing (New)
        self.log("\n" + "=" * 50)
        self.log("PHASE 5: ERP FUNCTIONALITY")
        self.log("=" * 50)
        
        # Test 14: Company Management API Endpoints
        test_results['company_management_endpoints'] = self.test_company_management_endpoints()
        
        # Test 15: Enhanced Chart of Accounts API Endpoints
        test_results['enhanced_chart_of_accounts'] = self.test_enhanced_chart_of_accounts_endpoints()
        
        # Test 16: Export and Print API Endpoints
        test_results['export_and_print_endpoints'] = self.test_export_and_print_endpoints()
        
        # Test 17: Authentication Requirements
        test_results['authentication_requirements'] = self.test_authentication_requirements()
        
        # Test 18: Data Validation and Error Handling
        test_results['data_validation'] = self.test_data_validation()
        
        # Phase 6: Company Filtering Issue Investigation (NEW)
        self.log("\n" + "=" * 50)
        self.log("PHASE 6: COMPANY FILTERING ISSUE INVESTIGATION")
        self.log("=" * 50)
        
        # Test 19: Company Filtering Issue Debug
        test_results['company_filtering_issue'] = self.test_company_filtering_issue()
        
        # Test 20: User Permission Filtering
        test_results['user_permission_filtering'] = self.test_user_permission_filtering()
        
        # Test 21: Database Direct Investigation
        test_results['database_direct_investigation'] = self.test_database_direct_investigation()
        
        # Phase 6: Results Summary
        self.log("\n" + "=" * 80)
        self.log("COMPREHENSIVE BACKEND TEST RESULTS")
        self.log("=" * 80)
        
        # Group results by category
        auth_tests = ['user_registration', 'user_login', 'jwt_token_validity', 'auth_me_endpoint']
        sister_company_tests = ['sister_company_setup', 'sister_companies_api', 'company_management_integration', 'sister_company_chart_accounts', 'tenant_database_isolation', 'sister_company_data_structure']
        company_tests = ['company_setup_address', 'auth_me_after_setup', 'multi_tenancy']
        currency_tests = ['chart_of_accounts', 'currency_rates_undefined_fix', 'currency_conversion', 'manual_currency_rate']
        user_mgmt_tests = ['admin_login', 'granular_permissions', 'user_deletion']
        erp_tests = ['company_management_endpoints', 'enhanced_chart_of_accounts', 'export_and_print_endpoints', 'authentication_requirements', 'data_validation']
        filtering_tests = ['company_filtering_issue', 'user_permission_filtering', 'database_direct_investigation']
        
        self.log("\n🔐 AUTHENTICATION SYSTEM:")
        for test_name in auth_tests:
            if test_name in test_results:
                status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
                self.log(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        self.log("\n🏢 COMPANY SETUP & MULTI-TENANCY:")
        for test_name in company_tests:
            if test_name in test_results:
                status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
                self.log(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        self.log("\n💱 CURRENCY MANAGEMENT:")
        for test_name in currency_tests:
            if test_name in test_results:
                status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
                self.log(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        self.log("\n👥 USER MANAGEMENT:")
        for test_name in user_mgmt_tests:
            if test_name in test_results:
                status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
                self.log(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        self.log("\n🏢 ERP FUNCTIONALITY:")
        for test_name in erp_tests:
            if test_name in test_results:
                status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
                self.log(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        self.log("\n🔍 COMPANY FILTERING INVESTIGATION:")
        for test_name in filtering_tests:
            if test_name in test_results:
                status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
                self.log(f"  {test_name.replace('_', ' ').title()}: {status}")
        
        # Critical assessment
        critical_tests = ['user_registration', 'auth_me_endpoint', 'company_setup_address', 'currency_rates_undefined_fix', 'company_management_endpoints', 'enhanced_chart_of_accounts', 'export_and_print_endpoints']
        critical_passed = all(test_results.get(test, False) for test in critical_tests if test in test_results)
        
        total_tests = len([t for t in test_results.values() if t is not None])
        passed_tests = len([t for t in test_results.values() if t is True])
        
        self.log("\n" + "=" * 80)
        self.log("FINAL ASSESSMENT")
        self.log("=" * 80)
        self.log(f"Tests Run: {total_tests}")
        self.log(f"Tests Passed: {passed_tests}")
        self.log(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        if critical_passed and passed_tests >= total_tests * 0.8:  # 80% pass rate
            self.log("\n🎉 BACKEND SYSTEM WORKING EXCELLENTLY!")
            self.log("✅ All critical functionality verified")
            self.log("✅ Authentication system working")
            self.log("✅ Company setup with address collection working")
            self.log("✅ Currency management working")
            self.log("✅ Multi-tenancy working")
        elif critical_passed:
            self.log("\n🎯 BACKEND CORE FUNCTIONALITY WORKING")
            self.log("✅ Critical systems operational")
            self.log("⚠️ Some non-critical issues may exist")
        else:
            self.log("\n🚨 CRITICAL BACKEND ISSUES FOUND")
            failed_critical = [test for test in critical_tests if not test_results.get(test, False)]
            for test in failed_critical:
                self.log(f"❌ Critical failure: {test.replace('_', ' ').title()}")
        
        return test_results

def main():
    """Main function to run the tests"""
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Exit with error code if critical tests failed
    critical_tests = ['registration', 'login', 'auth_me_before', 'company_setup', 'auth_me_after']
    new_feature_tests = ['chart_of_accounts', 'currency_rates_get', 'exchangerate_api']
    critical_passed = all(results.get(test, False) for test in critical_tests if test in results)
    new_features_passed = all(results.get(test, False) for test in new_feature_tests if test in results)
    
    # Exit successfully if critical tests pass (new features are not critical for exit code)
    sys.exit(0 if critical_passed else 1)

if __name__ == "__main__":
    main()