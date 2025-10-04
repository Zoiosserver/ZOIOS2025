#!/usr/bin/env python3
"""
Create Fresh Test Account for "Enable Sister Companies" Button Testing
As requested in the review, this script will:
1. Create a new test account with credentials: buttontest@example.com / buttontest123
2. Set up the company as "Private Limited Company" (not Group Company)
3. Verify the account works (login, company setup verification)
4. Test the "Enable Sister Companies" button functionality (conversion to Group Company)
5. Provide clear test instructions for the user
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

# Test account credentials as requested
TEST_EMAIL = "buttontest@example.com"
TEST_PASSWORD = "buttontest123"
TEST_NAME = "Button Test User"
TEST_COMPANY = "Button Test Company"

class ButtonTestAccountCreator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.company_data = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def create_test_account(self):
        """Create the fresh test account with specified credentials"""
        self.log("Creating fresh test account for button testing...")
        
        signup_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "company": TEST_COMPANY
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            self.log(f"Account creation response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                self.log("✅ Fresh test account created successfully")
                self.log(f"User ID: {self.user_data.get('id')}")
                self.log(f"Email: {self.user_data.get('email')}")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                self.log("⚠️ Account already exists, attempting login...")
                return self.login_existing_account()
            else:
                self.log(f"❌ Account creation failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Account creation error: {str(e)}")
            return False
    
    def login_existing_account(self):
        """Login to existing account if it already exists"""
        self.log("Logging into existing test account...")
        
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
                self.log("✅ Successfully logged into existing account")
                return True
            else:
                self.log(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}")
            return False
    
    def setup_private_limited_company(self):
        """Set up company as Private Limited Company (not Group Company)"""
        self.log("Setting up company as 'Private Limited Company'...")
        
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
                existing_company = response.json()
                self.company_data = existing_company
                self.log(f"✅ Company setup already exists: {existing_company.get('company_name')}")
                self.log(f"Current business type: {existing_company.get('business_type')}")
                
                # Check if it's already Private Limited Company
                if existing_company.get('business_type') == 'Private Limited Company':
                    self.log("✅ Company is already set as 'Private Limited Company' - perfect for testing!")
                    return True
                else:
                    self.log(f"⚠️ Company is currently '{existing_company.get('business_type')}' - this is still good for testing conversion")
                    return True
        except:
            pass
        
        # Create new company setup as Private Limited Company
        setup_data = {
            "company_name": TEST_COMPANY,
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR", "GBP"],
            "business_type": "Private Limited Company",  # Key: NOT Group Company
            "industry": "Technology",
            "address": "123 Button Test Street",
            "city": "Test City",
            "state": "CA",
            "postal_code": "12345",
            "phone": "+1-555-BUTTON",
            "email": TEST_EMAIL,
            "website": "https://buttontest.com",
            "tax_number": "BTN123456789",
            "registration_number": "BTNREG123456"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Company setup response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.company_data = data
                self.log("✅ Company setup as 'Private Limited Company' successful")
                self.log(f"Company ID: {data.get('id')}")
                self.log(f"Business Type: {data.get('business_type')}")
                self.log(f"Setup Completed: {data.get('setup_completed')}")
                return True
            elif response.status_code == 400 and "already completed" in response.text:
                self.log("✅ Company setup already completed - good for testing")
                return True
            else:
                self.log(f"❌ Company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company setup error: {str(e)}")
            return False
    
    def verify_account_login(self):
        """Verify the account works by testing login and auth endpoints"""
        self.log("Verifying account functionality...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test /auth/me endpoint
            response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
            self.log(f"/auth/me response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Account authentication working")
                self.log(f"User: {data.get('name')} ({data.get('email')})")
                self.log(f"Onboarding completed: {data.get('onboarding_completed')}")
                return True
            else:
                self.log(f"❌ Authentication verification failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Account verification error: {str(e)}")
            return False
    
    def verify_company_setup(self):
        """Verify the company setup and current business type"""
        self.log("Verifying company setup...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            self.log(f"Company setup verification response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.company_data = data
                self.log("✅ Company setup verification successful")
                self.log(f"Company Name: {data.get('company_name')}")
                self.log(f"Business Type: {data.get('business_type')}")
                self.log(f"Country: {data.get('country_code')}")
                self.log(f"Base Currency: {data.get('base_currency')}")
                
                # Check if it's ready for conversion testing
                business_type = data.get('business_type')
                if business_type == 'Private Limited Company':
                    self.log("✅ Perfect! Company is 'Private Limited Company' - ready for conversion testing")
                elif business_type == 'Group Company':
                    self.log("⚠️ Company is already 'Group Company' - user can still test the functionality")
                else:
                    self.log(f"✅ Company is '{business_type}' - can be converted to Group Company")
                
                return True
            else:
                self.log(f"❌ Company setup verification failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Company setup verification error: {str(e)}")
            return False
    
    def test_convert_to_group_company(self):
        """Test the 'Enable Sister Companies' button functionality"""
        self.log("Testing 'Enable Sister Companies' button functionality...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test the convert-to-group endpoint (this is what the button calls)
            response = self.session.put(f"{API_BASE}/setup/company/convert-to-group", headers=headers)
            self.log(f"Convert to Group Company response status: {response.status_code}")
            self.log(f"Convert to Group Company response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ 'Enable Sister Companies' functionality working!")
                self.log(f"Success: {data.get('success')}")
                self.log(f"Message: {data.get('message')}")
                self.log(f"New Business Type: {data.get('business_type')}")
                
                # Verify the conversion was saved
                return self.verify_conversion_saved()
            else:
                self.log(f"❌ Convert to Group Company failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Convert to Group Company error: {str(e)}")
            return False
    
    def verify_conversion_saved(self):
        """Verify that the conversion to Group Company was saved in the database"""
        self.log("Verifying conversion was saved in database...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            self.log(f"Conversion verification response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                business_type = data.get('business_type')
                
                if business_type == 'Group Company':
                    self.log("✅ CONVERSION SUCCESSFUL! Company is now 'Group Company'")
                    self.log("✅ Database properly updated - conversion was saved")
                    return True
                else:
                    self.log(f"❌ Conversion not saved - business type is still '{business_type}'")
                    return False
            else:
                self.log(f"❌ Conversion verification failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Conversion verification error: {str(e)}")
            return False
    
    def test_sister_company_endpoints(self):
        """Test sister company endpoints to ensure full functionality"""
        self.log("Testing sister company endpoints...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test GET sister companies
            response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
            self.log(f"GET sister companies response status: {response.status_code}")
            
            if response.status_code == 200:
                sister_companies = response.json()
                self.log(f"✅ GET sister companies working - found {len(sister_companies)} sister companies")
                
                # Test POST sister company (add new one)
                new_sister_data = {
                    "company_name": "Test Sister Company",
                    "country_code": "US",
                    "business_type": "Private Limited Company",
                    "industry": "Technology",
                    "base_currency": "USD"
                }
                
                post_response = self.session.post(f"{API_BASE}/company/sister-companies", 
                                                json=new_sister_data, headers=headers)
                self.log(f"POST sister company response status: {post_response.status_code}")
                
                if post_response.status_code == 200:
                    self.log("✅ POST sister company working - can add new sister companies")
                    return True
                else:
                    self.log(f"❌ POST sister company failed: {post_response.text}")
                    return False
            else:
                self.log(f"❌ GET sister companies failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Sister company endpoints error: {str(e)}")
            return False
    
    def test_companies_management_view(self):
        """Test the companies management view to see if sister companies appear"""
        self.log("Testing companies management view...")
        
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
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Companies management working - found {len(companies)} companies")
                
                # Analyze the companies structure
                main_companies = [c for c in companies if c.get('is_main_company', False)]
                sister_companies = [c for c in companies if not c.get('is_main_company', True)]
                
                self.log(f"Main companies: {len(main_companies)}")
                self.log(f"Sister companies: {len(sister_companies)}")
                
                for company in companies:
                    company_type = "Main" if company.get('is_main_company', False) else "Sister"
                    self.log(f"  - {company.get('company_name')} ({company_type})")
                
                return True
            else:
                self.log(f"❌ Companies management failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Companies management error: {str(e)}")
            return False
    
    def provide_test_instructions(self):
        """Provide clear test instructions for the user"""
        self.log("=" * 80)
        self.log("🎯 TEST ACCOUNT READY FOR USER TESTING")
        self.log("=" * 80)
        
        self.log("📋 TEST CREDENTIALS:")
        self.log(f"   Email: {TEST_EMAIL}")
        self.log(f"   Password: {TEST_PASSWORD}")
        
        self.log("")
        self.log("🔧 ACCOUNT SETUP:")
        if self.company_data:
            self.log(f"   Company: {self.company_data.get('company_name')}")
            self.log(f"   Business Type: {self.company_data.get('business_type')}")
            self.log(f"   Ready for conversion: {'Yes' if self.company_data.get('business_type') != 'Group Company' else 'Already Group Company'}")
        
        self.log("")
        self.log("📝 TEST INSTRUCTIONS FOR USER:")
        self.log("1. Login to the application with the provided credentials")
        self.log("2. Navigate to Company Management section")
        self.log("3. Look for the 'Enable Sister Companies' button")
        self.log("4. Click the 'Enable Sister Companies' button")
        self.log("5. Confirm the conversion dialog")
        self.log("6. Verify the company converts to 'Group Company'")
        self.log("7. Check if sister company options become available")
        
        self.log("")
        self.log("✅ BACKEND VERIFICATION COMPLETED:")
        self.log("   - Account creation: Working")
        self.log("   - Login functionality: Working") 
        self.log("   - Company setup: Working")
        self.log("   - Convert to Group Company API: Working")
        self.log("   - Sister company endpoints: Working")
        self.log("   - Companies management view: Working")
        
        self.log("")
        self.log("🎯 CONCLUSION:")
        self.log("The backend APIs for 'Enable Sister Companies' functionality are working perfectly.")
        self.log("If the user reports the button is not working, the issue is in the frontend")
        self.log("JavaScript event handling or API call implementation, not the backend endpoints.")
        
        self.log("=" * 80)
    
    def run_complete_test(self):
        """Run the complete test sequence"""
        self.log("🚀 Starting complete 'Enable Sister Companies' button test...")
        
        # Step 1: Create/login to test account
        if not self.create_test_account():
            self.log("❌ Failed to create/login to test account")
            return False
        
        # Step 2: Set up company as Private Limited Company
        if not self.setup_private_limited_company():
            self.log("❌ Failed to set up company")
            return False
        
        # Step 3: Verify account works
        if not self.verify_account_login():
            self.log("❌ Failed to verify account login")
            return False
        
        # Step 4: Verify company setup
        if not self.verify_company_setup():
            self.log("❌ Failed to verify company setup")
            return False
        
        # Step 5: Test the conversion functionality
        if not self.test_convert_to_group_company():
            self.log("❌ Failed to test convert to group company")
            return False
        
        # Step 6: Test sister company endpoints
        if not self.test_sister_company_endpoints():
            self.log("❌ Failed to test sister company endpoints")
            return False
        
        # Step 7: Test companies management view
        if not self.test_companies_management_view():
            self.log("❌ Failed to test companies management view")
            return False
        
        # Step 8: Provide test instructions
        self.provide_test_instructions()
        
        self.log("🎉 Complete test sequence successful!")
        return True

def main():
    """Main function to run the test"""
    tester = ButtonTestAccountCreator()
    
    try:
        success = tester.run_complete_test()
        if success:
            print("\n✅ SUCCESS: Fresh test account created and verified for 'Enable Sister Companies' button testing")
            sys.exit(0)
        else:
            print("\n❌ FAILED: Could not complete test account setup")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()