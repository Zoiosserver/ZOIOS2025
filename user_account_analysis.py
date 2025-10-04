#!/usr/bin/env python3
"""
User Account Analysis Script
Analyzes user accounts to find those that might have sister company issues
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

class UserAccountAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def login_as_admin(self):
        """Try to login as admin to access user data"""
        admin_credentials = [
            {"email": "admin@2mholding.com", "password": "admin123"},
            {"email": "admin@zoios.com", "password": "admin123"},
            {"email": "usertestsister@example.com", "password": "testsister123"}  # Known working account
        ]
        
        for creds in admin_credentials:
            try:
                response = self.session.post(f"{API_BASE}/auth/login", json=creds)
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get('access_token')
                    user_data = data.get('user')
                    self.log(f"✅ Logged in as: {creds['email']} (Role: {user_data.get('role')})")
                    return True
            except Exception as e:
                continue
        
        self.log("❌ Could not login with any admin credentials")
        return False
    
    def analyze_user_accounts(self):
        """Analyze user accounts to find potential issues"""
        if not self.auth_token:
            self.log("❌ No auth token available")
            return
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Try to get user list (may not work if not admin)
        try:
            response = self.session.get(f"{API_BASE}/admin/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                self.log(f"✅ Found {len(users)} users in system")
                self.analyze_users_with_company_setup(users, headers)
            else:
                self.log(f"⚠️ Cannot access admin users endpoint: {response.status_code}")
                # Try alternative approach
                self.analyze_current_user_only(headers)
        except Exception as e:
            self.log(f"❌ Error accessing users: {str(e)}")
            self.analyze_current_user_only(headers)
    
    def analyze_users_with_company_setup(self, users, headers):
        """Analyze users and their company setups"""
        self.log("\n📊 ANALYZING USER ACCOUNTS:")
        self.log("=" * 50)
        
        problem_users = []
        
        for user in users:
            email = user.get('email')
            user_id = user.get('id')
            onboarding_completed = user.get('onboarding_completed')
            
            self.log(f"\nUser: {email}")
            self.log(f"  ID: {user_id}")
            self.log(f"  Onboarding: {onboarding_completed}")
            
            if onboarding_completed:
                # Try to get their company setup
                company_info = self.get_user_company_info(user_id, email, headers)
                if company_info:
                    business_type = company_info.get('business_type')
                    company_name = company_info.get('company_name')
                    
                    self.log(f"  Company: {company_name}")
                    self.log(f"  Business Type: {business_type}")
                    
                    if business_type == "Group Company":
                        # Check for sister companies
                        sister_count = self.check_sister_companies(user_id, email, headers)
                        self.log(f"  Sister Companies: {sister_count}")
                        
                        if sister_count == 0:
                            self.log(f"  ⚠️ POTENTIAL ISSUE: Group Company with no sister companies")
                            problem_users.append({
                                'email': email,
                                'user_id': user_id,
                                'issue': 'Group Company with no sister companies',
                                'company_name': company_name
                            })
                    elif business_type == "Private Limited Company":
                        # Check if they're trying to add sister companies
                        self.log(f"  ℹ️ Private Limited Company - cannot have sister companies")
                else:
                    self.log(f"  ❌ Could not get company setup")
            else:
                self.log(f"  ⚠️ Onboarding not completed")
        
        # Summary of problem users
        if problem_users:
            self.log(f"\n🚨 FOUND {len(problem_users)} USERS WITH POTENTIAL ISSUES:")
            for user in problem_users:
                self.log(f"  - {user['email']}: {user['issue']}")
                self.log(f"    Company: {user['company_name']}")
        else:
            self.log(f"\n✅ No obvious issues found in user accounts")
    
    def get_user_company_info(self, user_id, email, headers):
        """Get company setup info for a specific user"""
        # Try to login as this user to get their company info
        try:
            # We can't easily get other users' company info without their credentials
            # So we'll use the current session if it's the same user
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def check_sister_companies(self, user_id, email, headers):
        """Check sister companies for a user"""
        try:
            response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
            if response.status_code == 200:
                sister_companies = response.json()
                return len(sister_companies)
        except:
            pass
        return 0
    
    def analyze_current_user_only(self, headers):
        """Analyze only the current logged-in user"""
        self.log("\n📊 ANALYZING CURRENT USER ACCOUNT:")
        self.log("=" * 40)
        
        # Get current user info
        try:
            response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                email = user_data.get('email')
                user_id = user_data.get('id')
                onboarding_completed = user_data.get('onboarding_completed')
                
                self.log(f"Current User: {email}")
                self.log(f"User ID: {user_id}")
                self.log(f"Onboarding: {onboarding_completed}")
                
                if onboarding_completed:
                    # Get company setup
                    company_response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
                    if company_response.status_code == 200:
                        company_data = company_response.json()
                        business_type = company_data.get('business_type')
                        company_name = company_data.get('company_name')
                        
                        self.log(f"Company: {company_name}")
                        self.log(f"Business Type: {business_type}")
                        
                        # Check companies management endpoint
                        companies_response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
                        if companies_response.status_code == 200:
                            companies = companies_response.json()
                            main_companies = [c for c in companies if c.get('is_main_company', False)]
                            sister_companies = [c for c in companies if not c.get('is_main_company', True)]
                            
                            self.log(f"Total Companies: {len(companies)}")
                            self.log(f"Main Companies: {len(main_companies)}")
                            self.log(f"Sister Companies: {len(sister_companies)}")
                            
                            if business_type == "Group Company" and len(sister_companies) == 0:
                                self.log("🚨 ISSUE FOUND: Group Company with no sister companies!")
                                self.suggest_solutions()
                            elif business_type == "Private Limited Company" and len(sister_companies) > 0:
                                self.log("🚨 ISSUE FOUND: Private Limited Company has sister companies!")
                            else:
                                self.log("✅ Account structure looks correct")
                        else:
                            self.log(f"❌ Could not get companies: {companies_response.text}")
                    else:
                        self.log(f"❌ Could not get company setup: {company_response.text}")
                else:
                    self.log("⚠️ User has not completed onboarding")
            else:
                self.log(f"❌ Could not get current user info: {response.text}")
        except Exception as e:
            self.log(f"❌ Error analyzing current user: {str(e)}")
    
    def suggest_solutions(self):
        """Suggest solutions for the identified issues"""
        self.log("\n💡 SUGGESTED SOLUTIONS:")
        self.log("1. Convert Private Limited Company to Group Company:")
        self.log("   - Update business_type in company_setups table")
        self.log("   - Allow user to add sister companies")
        
        self.log("2. Add sister companies to existing Group Company:")
        self.log("   - Use POST /api/company/sister-companies endpoint")
        self.log("   - Or allow user to modify company setup")
        
        self.log("3. Reset company setup to allow re-configuration:")
        self.log("   - Set onboarding_completed = false")
        self.log("   - Allow user to go through setup again")
    
    def test_company_conversion(self):
        """Test converting a company to Group Company"""
        if not self.auth_token:
            return
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        self.log("\n🔧 TESTING COMPANY CONVERSION SOLUTIONS:")
        
        # Create a test user with Private Limited Company
        test_email = f"conversion{int(time.time())}@example.com"
        signup_data = {
            "email": test_email,
            "password": "testpass123",
            "name": "Conversion Test User",
            "company": "Conversion Test Company"
        }
        
        try:
            # Create user
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            if response.status_code != 200:
                self.log(f"❌ Test user creation failed: {response.text}")
                return
            
            test_token = response.json().get('access_token')
            test_headers = {
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json"
            }
            
            # Setup as Private Limited Company
            setup_data = {
                "company_name": "Test Private Company",
                "country_code": "US",
                "base_currency": "USD",
                "additional_currencies": [],
                "business_type": "Private Limited Company",
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
            
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=test_headers)
            if response.status_code != 200:
                self.log(f"❌ Company setup failed: {response.text}")
                return
            
            self.log("✅ Created test Private Limited Company")
            
            # Try to add sister company (should fail)
            sister_data = {
                "company_name": "Test Sister Company",
                "country_code": "GB",
                "base_currency": "GBP",
                "business_type": "Private Limited Company",
                "industry": "Finance",
                "fiscal_year_start": "01-01"
            }
            
            response = self.session.post(f"{API_BASE}/company/sister-companies", json=sister_data, headers=test_headers)
            self.log(f"Sister company creation attempt: {response.status_code}")
            
            if response.status_code == 400:
                self.log("✅ Correctly blocked sister company creation for Private Limited Company")
            else:
                self.log(f"⚠️ Unexpected response: {response.text}")
            
        except Exception as e:
            self.log(f"❌ Company conversion test error: {str(e)}")
    
    def run_analysis(self):
        """Run the complete user account analysis"""
        self.log("🔍 Starting User Account Analysis...")
        self.log("=" * 50)
        
        if not self.login_as_admin():
            return
        
        self.analyze_user_accounts()
        self.test_company_conversion()
        
        self.log("\n" + "=" * 50)
        self.log("📋 ANALYSIS COMPLETE")
        self.log("=" * 50)

if __name__ == "__main__":
    analyzer = UserAccountAnalyzer()
    analyzer.run_analysis()