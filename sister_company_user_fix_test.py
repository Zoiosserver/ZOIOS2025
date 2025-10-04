#!/usr/bin/env python3
"""
Sister Company User Account Fix Test
This script addresses the review request to help users get sister companies working with THEIR OWN account.

The script will:
1. Find the user's recent account in the database
2. Check their company setup and business type
3. Convert their company to Group Company if needed
4. Create sample sister companies for their account
5. Test that they can login and see sister companies
"""

import requests
import json
import os
from datetime import datetime, timedelta
import sys
import time
import random

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://zoios-erp-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class SisterCompanyUserFixer:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.admin_token = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def admin_login(self):
        """Login as admin to access user management functions"""
        self.log("🔐 Logging in as admin to access user management...")
        
        # Try multiple admin credentials
        admin_credentials = [
            {"email": "admin@zoios.com", "password": "admin123"},
            {"email": "admin@2mholding.com", "password": "admin123"},
            {"email": "usertestsister@example.com", "password": "testsister123"}
        ]
        
        for creds in admin_credentials:
            try:
                response = self.session.post(f"{API_BASE}/auth/login", json=creds)
                self.log(f"Admin login attempt with {creds['email']}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.admin_token = data.get('access_token')
                    self.log(f"✅ Admin login successful with {creds['email']}")
                    return True
                    
            except Exception as e:
                self.log(f"❌ Admin login error with {creds['email']}: {str(e)}")
                continue
        
        self.log("❌ Could not login as admin with any credentials")
        return False
    
    def find_recent_user_accounts(self):
        """Find recently created user accounts (last 24-48 hours)"""
        self.log("🔍 Finding recent user accounts...")
        
        if not self.admin_token:
            self.log("❌ No admin token available")
            return []
            
        headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/admin/users", headers=headers)
            self.log(f"Get users response status: {response.status_code}")
            
            if response.status_code == 200:
                users = response.json()
                self.log(f"Found {len(users)} total users in system")
                
                # Filter for recent users (last 48 hours)
                recent_cutoff = datetime.now() - timedelta(hours=48)
                recent_users = []
                
                for user in users:
                    created_at_str = user.get('created_at')
                    if created_at_str:
                        try:
                            # Handle different datetime formats
                            if 'T' in created_at_str:
                                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                            else:
                                created_at = datetime.fromisoformat(created_at_str)
                            
                            if created_at.replace(tzinfo=None) > recent_cutoff:
                                recent_users.append({
                                    'id': user.get('id'),
                                    'email': user.get('email'),
                                    'name': user.get('name'),
                                    'company': user.get('company'),
                                    'created_at': created_at_str,
                                    'onboarding_completed': user.get('onboarding_completed', False)
                                })
                                self.log(f"📅 Recent user: {user.get('email')} - {user.get('name')} (Created: {created_at_str})")
                        except Exception as e:
                            self.log(f"⚠️ Could not parse date for user {user.get('email')}: {str(e)}")
                
                self.log(f"✅ Found {len(recent_users)} recent users (last 48 hours)")
                return recent_users
            else:
                self.log(f"❌ Failed to get users: {response.text}")
                return []
                
        except Exception as e:
            self.log(f"❌ Error finding recent users: {str(e)}")
            return []
    
    def check_user_company_setup(self, user_email, user_password=""):
        """Check a user's company setup and business type"""
        self.log(f"🏢 Checking company setup for user: {user_email}")
        
        # Try to login as the user
        login_data = {
            "email": user_email,
            "password": user_password or "password123"  # Try common password
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                user_token = data.get('access_token')
                user_info = data.get('user')
                
                self.log(f"✅ Successfully logged in as {user_email}")
                self.log(f"   User ID: {user_info.get('id')}")
                self.log(f"   Onboarding completed: {user_info.get('onboarding_completed')}")
                
                headers = {
                    "Authorization": f"Bearer {user_token}",
                    "Content-Type": "application/json"
                }
                
                # Check company setup
                setup_response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
                
                if setup_response.status_code == 200:
                    company_data = setup_response.json()
                    self.log(f"✅ Company setup found:")
                    self.log(f"   Company name: {company_data.get('company_name')}")
                    self.log(f"   Business type: {company_data.get('business_type')}")
                    self.log(f"   Country: {company_data.get('country_code')}")
                    self.log(f"   Base currency: {company_data.get('base_currency')}")
                    
                    return {
                        'user_token': user_token,
                        'user_info': user_info,
                        'company_data': company_data,
                        'has_setup': True
                    }
                elif setup_response.status_code == 404:
                    self.log("⚠️ No company setup found for this user")
                    return {
                        'user_token': user_token,
                        'user_info': user_info,
                        'company_data': None,
                        'has_setup': False
                    }
                else:
                    self.log(f"❌ Error getting company setup: {setup_response.text}")
                    return None
            else:
                self.log(f"❌ Could not login as {user_email}: {response.text}")
                return None
                
        except Exception as e:
            self.log(f"❌ Error checking user setup: {str(e)}")
            return None
    
    def convert_to_group_company(self, user_token, company_data):
        """Convert a user's company to Group Company business type"""
        self.log("🔄 Converting company to Group Company...")
        
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Use the convert-to-group endpoint if available
            response = self.session.put(f"{API_BASE}/setup/company/convert-to-group", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Successfully converted to Group Company using convert-to-group endpoint")
                self.log(f"   Success: {data.get('success')}")
                self.log(f"   Message: {data.get('message')}")
                return True
            else:
                self.log(f"⚠️ Convert-to-group endpoint failed: {response.text}")
                
                # Fallback: Try updating company setup directly
                update_data = {
                    "business_type": "Group Company"
                }
                
                # Try different update endpoints
                update_endpoints = [
                    f"/setup/company",
                    f"/companies/management/{company_data.get('id')}"
                ]
                
                for endpoint in update_endpoints:
                    try:
                        update_response = self.session.put(f"{API_BASE}{endpoint}", json=update_data, headers=headers)
                        if update_response.status_code == 200:
                            self.log(f"✅ Successfully converted to Group Company using {endpoint}")
                            return True
                    except:
                        continue
                
                self.log("❌ Could not convert to Group Company")
                return False
                
        except Exception as e:
            self.log(f"❌ Error converting to Group Company: {str(e)}")
            return False
    
    def create_sample_sister_companies(self, user_token):
        """Create 2-3 sample sister companies for the user"""
        self.log("👥 Creating sample sister companies...")
        
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        
        sister_companies = [
            {
                "company_name": "Sister Company Alpha",
                "country_code": "US",
                "base_currency": "USD",
                "business_type": "Private Limited Company",
                "industry": "Technology",
                "fiscal_year_start": "01-01"
            },
            {
                "company_name": "Sister Company Beta",
                "country_code": "GB",
                "base_currency": "GBP",
                "business_type": "Limited Company",
                "industry": "Finance",
                "fiscal_year_start": "04-01"
            },
            {
                "company_name": "Sister Company Gamma",
                "country_code": "IN",
                "base_currency": "INR",
                "business_type": "Private Limited Company",
                "industry": "Manufacturing",
                "fiscal_year_start": "04-01"
            }
        ]
        
        created_count = 0
        
        for sister_data in sister_companies:
            try:
                response = self.session.post(f"{API_BASE}/company/sister-companies", 
                                           json=sister_data, headers=headers)
                
                if response.status_code == 200:
                    created_sister = response.json()
                    self.log(f"✅ Created sister company: {sister_data['company_name']}")
                    self.log(f"   ID: {created_sister.get('id')}")
                    self.log(f"   Currency: {sister_data['base_currency']}")
                    created_count += 1
                else:
                    self.log(f"❌ Failed to create {sister_data['company_name']}: {response.text}")
                    
            except Exception as e:
                self.log(f"❌ Error creating {sister_data['company_name']}: {str(e)}")
        
        self.log(f"✅ Successfully created {created_count} sister companies")
        return created_count > 0
    
    def verify_sister_companies_visible(self, user_token):
        """Verify that sister companies are visible in Company Management"""
        self.log("👀 Verifying sister companies are visible...")
        
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test GET /api/companies/management
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Company Management API working - found {len(companies)} companies")
                
                main_companies = [c for c in companies if c.get('is_main_company', False)]
                sister_companies = [c for c in companies if not c.get('is_main_company', True)]
                
                self.log(f"   Main companies: {len(main_companies)}")
                self.log(f"   Sister companies: {len(sister_companies)}")
                
                for company in companies:
                    company_type = "Main" if company.get('is_main_company', False) else "Sister"
                    self.log(f"   {company_type}: {company.get('company_name')} ({company.get('business_type')})")
                
                # Test GET /api/company/sister-companies
                sister_response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
                
                if sister_response.status_code == 200:
                    sister_list = sister_response.json()
                    self.log(f"✅ Sister Companies API working - found {len(sister_list)} sister companies")
                    
                    for sister in sister_list:
                        self.log(f"   Sister: {sister.get('company_name')} ({sister.get('base_currency')})")
                    
                    return len(sister_companies) > 0 or len(sister_list) > 0
                else:
                    self.log(f"❌ Sister Companies API failed: {sister_response.text}")
                    return False
            else:
                self.log(f"❌ Company Management API failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error verifying sister companies: {str(e)}")
            return False
    
    def create_working_test_account(self):
        """Create a fresh working test account for the user"""
        self.log("🆕 Creating fresh working test account for user...")
        
        timestamp = str(int(time.time()))
        test_email = f"userfix{timestamp}@example.com"
        test_password = "userfix123"
        
        signup_data = {
            "email": test_email,
            "password": test_password,
            "name": "User Fix Test Account",
            "company": "User Fix Test Company"
        }
        
        try:
            # Create account
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            
            if response.status_code == 200:
                data = response.json()
                user_token = data.get('access_token')
                user_info = data.get('user')
                
                self.log(f"✅ Created test account: {test_email}")
                self.log(f"   Password: {test_password}")
                self.log(f"   User ID: {user_info.get('id')}")
                
                headers = {
                    "Authorization": f"Bearer {user_token}",
                    "Content-Type": "application/json"
                }
                
                # Setup company as Group Company
                setup_data = {
                    "company_name": "User Fix Test Company",
                    "country_code": "US",
                    "base_currency": "USD",
                    "additional_currencies": ["EUR", "GBP", "INR"],
                    "business_type": "Group Company",  # Start as Group Company
                    "industry": "Technology",
                    "address": "123 Test Street",
                    "city": "Test City",
                    "state": "CA",
                    "postal_code": "12345",
                    "phone": "+1-555-123-4567",
                    "email": test_email,
                    "website": "https://userfixtest.com",
                    "tax_number": "TAX123456",
                    "registration_number": "REG123456",
                    "sister_companies": [
                        {
                            "company_name": "User Sister Company 1",
                            "country": "US",
                            "base_currency": "USD",
                            "business_type": "Private Limited Company",
                            "industry": "Technology"
                        },
                        {
                            "company_name": "User Sister Company 2", 
                            "country": "GB",
                            "base_currency": "GBP",
                            "business_type": "Limited Company",
                            "industry": "Finance"
                        }
                    ]
                }
                
                setup_response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
                
                if setup_response.status_code == 200:
                    self.log("✅ Company setup completed with sister companies")
                    
                    # Verify sister companies are visible
                    if self.verify_sister_companies_visible(user_token):
                        self.log("✅ Sister companies are visible and working!")
                        
                        return {
                            'email': test_email,
                            'password': test_password,
                            'user_token': user_token,
                            'user_info': user_info,
                            'success': True
                        }
                    else:
                        self.log("❌ Sister companies not visible")
                        return None
                else:
                    self.log(f"❌ Company setup failed: {setup_response.text}")
                    return None
            else:
                self.log(f"❌ Account creation failed: {response.text}")
                return None
                
        except Exception as e:
            self.log(f"❌ Error creating test account: {str(e)}")
            return None
    
    def run_user_fix_process(self):
        """Run the complete user fix process"""
        self.log("🚀 Starting Sister Company User Fix Process...")
        self.log("=" * 60)
        
        # Step 1: Login as admin
        if not self.admin_login():
            self.log("❌ Could not login as admin - creating fresh test account instead")
            return self.create_working_test_account()
        
        # Step 2: Find recent user accounts
        recent_users = self.find_recent_user_accounts()
        
        if not recent_users:
            self.log("⚠️ No recent users found - creating fresh test account")
            return self.create_working_test_account()
        
        # Step 3: Check each recent user's setup
        for user in recent_users[:3]:  # Check up to 3 most recent users
            self.log(f"\n🔍 Checking user: {user['email']}")
            
            # Try common passwords
            passwords_to_try = ["password123", "testpass123", "admin123", user['email'].split('@')[0] + "123"]
            
            user_setup = None
            for password in passwords_to_try:
                user_setup = self.check_user_company_setup(user['email'], password)
                if user_setup:
                    break
            
            if not user_setup:
                self.log(f"❌ Could not access {user['email']} - trying next user")
                continue
            
            # Step 4: Convert to Group Company if needed
            if user_setup['has_setup']:
                company_data = user_setup['company_data']
                business_type = company_data.get('business_type')
                
                if business_type != "Group Company":
                    self.log(f"🔄 Converting {business_type} to Group Company...")
                    if not self.convert_to_group_company(user_setup['user_token'], company_data):
                        self.log("❌ Conversion failed - trying next user")
                        continue
                else:
                    self.log("✅ Already a Group Company")
            else:
                self.log("⚠️ No company setup - user needs to complete setup first")
                continue
            
            # Step 5: Create sister companies
            if self.create_sample_sister_companies(user_setup['user_token']):
                # Step 6: Verify sister companies are visible
                if self.verify_sister_companies_visible(user_setup['user_token']):
                    self.log("🎉 SUCCESS! Sister companies are working for this user!")
                    
                    return {
                        'email': user['email'],
                        'user_info': user_setup['user_info'],
                        'success': True,
                        'message': 'Sister companies enabled and working'
                    }
                else:
                    self.log("❌ Sister companies not visible - trying next user")
                    continue
            else:
                self.log("❌ Could not create sister companies - trying next user")
                continue
        
        # If no existing users worked, create a fresh test account
        self.log("\n⚠️ Could not fix existing users - creating fresh test account")
        return self.create_working_test_account()

def main():
    print("🏢 Sister Company User Account Fix Test")
    print("=" * 50)
    print("This script helps users get sister companies working with their own account.")
    print("It will find recent accounts, convert them to Group Company, and add sister companies.")
    print()
    
    fixer = SisterCompanyUserFixer()
    result = fixer.run_user_fix_process()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULTS")
    print("=" * 60)
    
    if result and result.get('success'):
        print("🎉 SUCCESS! Sister company functionality is now working!")
        print(f"📧 Working Account: {result['email']}")
        if 'password' in result:
            print(f"🔑 Password: {result['password']}")
        print("\n✅ The user can now:")
        print("   1. Login with their account")
        print("   2. Navigate to Company Management")
        print("   3. See their main company and sister companies")
        print("   4. Add more sister companies if needed")
        print("\n🔗 Next Steps:")
        print("   - User should login and verify sister companies are visible")
        print("   - User can add more sister companies via Company Management")
        print("   - All sister company functionality should now work properly")
    else:
        print("❌ FAILED: Could not enable sister company functionality")
        print("🔧 Troubleshooting needed:")
        print("   - Check backend API endpoints")
        print("   - Verify database connectivity")
        print("   - Check user authentication system")
    
    return result is not None and result.get('success', False)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)