#!/usr/bin/env python3
"""
Super Admin Functionality Testing Script
Tests the specific super admin functionality as requested in the review
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://zoios-erp-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class SuperAdminTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_super_admin_check(self):
        """Test GET /api/admin/check-super-admin endpoint"""
        self.log("Testing super admin check endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/admin/check-super-admin")
            self.log(f"Super admin check response status: {response.status_code}")
            self.log(f"Super admin check response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                exists = data.get('exists', False)
                email = data.get('email')
                
                if exists and email == "admin@2mholding.com":
                    self.log("✅ Super admin exists and is properly configured")
                    return True
                elif exists:
                    self.log(f"⚠️ Super admin exists but with unexpected email: {email}")
                    return False
                else:
                    self.log("❌ Super admin does not exist")
                    return False
            else:
                self.log(f"❌ Super admin check failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Super admin check error: {str(e)}")
            return False

    def test_super_admin_initialization(self):
        """Test POST /api/admin/init-super-admin endpoint"""
        self.log("Testing super admin initialization...")
        
        try:
            response = self.session.post(f"{API_BASE}/admin/init-super-admin")
            self.log(f"Super admin init response status: {response.status_code}")
            self.log(f"Super admin init response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log("✅ Super admin initialization successful")
                    return True
                else:
                    self.log("❌ Super admin initialization reported failure")
                    return False
            else:
                self.log(f"❌ Super admin initialization failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Super admin initialization error: {str(e)}")
            return False

    def test_super_admin_login(self):
        """Test super admin login with admin@2mholding.com credentials"""
        self.log("Testing super admin login with admin@2mholding.com...")
        
        login_data = {
            "email": "admin@2mholding.com",
            "password": "admin123"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            self.log(f"Super admin login response status: {response.status_code}")
            self.log(f"Super admin login response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                
                # Verify super admin role and permissions
                if self.user_data.get('role') == 'super_admin':
                    self.log("✅ Super admin login successful with correct role")
                    self.log(f"User ID: {self.user_data.get('id')}")
                    self.log(f"Role: {self.user_data.get('role')}")
                    self.log(f"Email: {self.user_data.get('email')}")
                    return True
                else:
                    self.log(f"❌ Super admin login successful but role is: {self.user_data.get('role')}")
                    return False
            else:
                self.log(f"❌ Super admin login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Super admin login error: {str(e)}")
            return False

    def test_super_admin_permissions(self):
        """Test super admin permissions via /auth/me endpoint"""
        self.log("Testing super admin permissions...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
            self.log(f"Super admin /auth/me response status: {response.status_code}")
            self.log(f"Super admin /auth/me response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                permissions = data.get('permissions', {})
                
                # Check for key super admin permissions
                required_permissions = [
                    'view_all_companies',
                    'manage_all_companies',
                    'create_companies',
                    'delete_companies',
                    'manage_users'
                ]
                
                all_permissions_correct = True
                for perm in required_permissions:
                    if permissions.get(perm) == True:
                        self.log(f"✅ {perm}: True")
                    else:
                        self.log(f"❌ {perm}: {permissions.get(perm)} (should be True)")
                        all_permissions_correct = False
                
                if all_permissions_correct:
                    self.log("✅ Super admin has all required permissions")
                    return True
                else:
                    self.log("❌ Super admin missing some required permissions")
                    return False
            else:
                self.log(f"❌ Super admin /auth/me failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Super admin permissions test error: {str(e)}")
            return False

    def test_company_management_with_super_admin(self):
        """Test GET /api/companies/management with super admin token"""
        self.log("Testing company management API with super admin...")
        
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
                
                # Verify response format
                if isinstance(companies, list):
                    self.log("✅ Response format is correct (array)")
                    
                    if len(companies) > 0:
                        company = companies[0]
                        required_fields = ['id', 'company_name', 'business_type', 'country_code', 'base_currency']
                        
                        all_fields_present = True
                        for field in required_fields:
                            if field in company:
                                self.log(f"✅ Field present: {field} = {company[field]}")
                            else:
                                self.log(f"❌ Missing field: {field}")
                                all_fields_present = False
                        
                        if all_fields_present:
                            self.log("✅ Company data structure is correct")
                            return True
                        else:
                            self.log("❌ Company data structure incomplete")
                            return False
                    else:
                        self.log("⚠️ No companies found - this might be expected for fresh system")
                        return True
                else:
                    self.log("❌ Response format incorrect - expected array")
                    return False
            elif response.status_code == 403:
                self.log("❌ Access denied - super admin permissions not working")
                return False
            elif response.status_code == 401:
                self.log("❌ Authentication failed - token invalid")
                return False
            else:
                self.log(f"❌ Company management API failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company management API test error: {str(e)}")
            return False

    def test_jwt_token_validation_super_admin(self):
        """Test JWT token validation with super admin token"""
        self.log("Testing JWT token validation for super admin...")
        
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
            "/companies/management",
            "/setup/countries",
            "/setup/currencies"
        ]
        
        all_passed = True
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}", headers=headers)
                if response.status_code in [200, 404]:  # 404 is acceptable for some endpoints
                    self.log(f"✅ JWT token valid for {endpoint} (status: {response.status_code})")
                else:
                    self.log(f"❌ JWT token invalid for {endpoint}: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log(f"❌ JWT token test error for {endpoint}: {str(e)}")
                all_passed = False
        
        return all_passed

    def run_super_admin_tests(self):
        """Run all super admin tests"""
        self.log("=" * 80)
        self.log("SUPER ADMIN FUNCTIONALITY TESTING")
        self.log("=" * 80)
        
        test_results = {}
        
        # Test 1: Super Admin Check
        test_results['super_admin_check'] = self.test_super_admin_check()
        
        # Test 2: Super Admin Initialization
        test_results['super_admin_initialization'] = self.test_super_admin_initialization()
        
        # Test 3: Super Admin Login
        test_results['super_admin_login'] = self.test_super_admin_login()
        
        # Test 4: Super Admin Permissions
        test_results['super_admin_permissions'] = self.test_super_admin_permissions()
        
        # Test 5: Company Management with Super Admin
        test_results['company_management_super_admin'] = self.test_company_management_with_super_admin()
        
        # Test 6: JWT Token Validation for Super Admin
        test_results['jwt_token_validation_super_admin'] = self.test_jwt_token_validation_super_admin()
        
        # Print summary
        self.log("\n" + "=" * 80)
        self.log("SUPER ADMIN TEST RESULTS")
        self.log("=" * 80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name}: {status}")
            if result:
                passed += 1
        
        self.log(f"\nTests Passed: {passed}/{total}")
        self.log(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            self.log("🎉 ALL SUPER ADMIN TESTS PASSED!")
        else:
            self.log("⚠️ Some super admin tests failed - check logs above")
        
        return test_results

if __name__ == "__main__":
    tester = SuperAdminTester()
    tester.run_super_admin_tests()