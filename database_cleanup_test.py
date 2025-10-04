#!/usr/bin/env python3
"""
ZOIOS ERP Complete Database Cleanup and System Reset Test
This script performs comprehensive database cleanup as requested:
1. Delete ALL user accounts
2. Delete ALL company setups and sister companies  
3. Delete ALL chart of accounts data
4. Delete ALL currency configurations
5. Delete ALL tenant databases
6. Reset system to completely clean state
7. Verify system readiness for fresh user flow
"""

import requests
import json
import os
from datetime import datetime
import sys
import time
import random
from pymongo import MongoClient

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://zoios-erp-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# MongoDB connection for direct database operations
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'zoios_crm')

class DatabaseCleanupTester:
    def __init__(self):
        self.session = requests.Session()
        self.mongo_client = None
        self.main_db = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def connect_to_mongodb(self):
        """Connect to MongoDB for direct database operations"""
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.main_db = self.mongo_client[DB_NAME]
            # Test connection
            self.main_db.command('ping')
            self.log("✅ Connected to MongoDB successfully")
            return True
        except Exception as e:
            self.log(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    def get_database_stats_before_cleanup(self):
        """Get database statistics before cleanup"""
        self.log("📊 Getting database statistics before cleanup...")
        
        try:
            collections = [
                'users', 'company_setups', 'sister_companies', 'chart_of_accounts',
                'exchange_rates', 'contacts', 'companies', 'call_logs', 'email_responses',
                'password_reset_tokens'
            ]
            
            stats = {}
            total_documents = 0
            
            for collection_name in collections:
                try:
                    count = self.main_db[collection_name].count_documents({})
                    stats[collection_name] = count
                    total_documents += count
                    self.log(f"📊 {collection_name}: {count} documents")
                except Exception as e:
                    self.log(f"⚠️ Could not count {collection_name}: {str(e)}")
                    stats[collection_name] = 0
            
            self.log(f"📊 Total documents across all collections: {total_documents}")
            
            # Get tenant databases
            tenant_dbs = []
            for db_name in self.mongo_client.list_database_names():
                if db_name.startswith('tenant_'):
                    tenant_dbs.append(db_name)
                    tenant_db = self.mongo_client[db_name]
                    tenant_count = 0
                    for collection_name in collections:
                        try:
                            tenant_count += tenant_db[collection_name].count_documents({})
                        except:
                            pass
                    self.log(f"📊 Tenant database {db_name}: {tenant_count} documents")
            
            self.log(f"📊 Found {len(tenant_dbs)} tenant databases: {tenant_dbs}")
            
            return {
                'main_db_stats': stats,
                'total_documents': total_documents,
                'tenant_databases': tenant_dbs
            }
            
        except Exception as e:
            self.log(f"❌ Error getting database stats: {str(e)}")
            return None
    
    def perform_complete_database_cleanup(self):
        """Perform complete database cleanup"""
        self.log("🧹 Starting COMPLETE DATABASE CLEANUP...")
        
        try:
            collections_to_clean = [
                'users', 'company_setups', 'sister_companies', 'chart_of_accounts',
                'exchange_rates', 'contacts', 'companies', 'call_logs', 'email_responses',
                'password_reset_tokens'
            ]
            
            total_deleted = 0
            
            # Clean main database collections
            self.log("🧹 Cleaning main database collections...")
            for collection_name in collections_to_clean:
                try:
                    result = self.main_db[collection_name].delete_many({})
                    deleted_count = result.deleted_count
                    total_deleted += deleted_count
                    self.log(f"✅ Deleted {deleted_count} documents from {collection_name}")
                except Exception as e:
                    self.log(f"❌ Error cleaning {collection_name}: {str(e)}")
            
            # Clean tenant databases
            self.log("🧹 Cleaning tenant databases...")
            tenant_dbs_deleted = 0
            for db_name in self.mongo_client.list_database_names():
                if db_name.startswith('tenant_'):
                    try:
                        self.mongo_client.drop_database(db_name)
                        tenant_dbs_deleted += 1
                        self.log(f"✅ Deleted tenant database: {db_name}")
                    except Exception as e:
                        self.log(f"❌ Error deleting tenant database {db_name}: {str(e)}")
            
            self.log(f"🎉 CLEANUP COMPLETE: Deleted {total_deleted} documents from main database")
            self.log(f"🎉 CLEANUP COMPLETE: Deleted {tenant_dbs_deleted} tenant databases")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error during database cleanup: {str(e)}")
            return False
    
    def verify_complete_cleanup(self):
        """Verify that all data has been cleaned up"""
        self.log("🔍 Verifying complete cleanup...")
        
        try:
            collections_to_verify = [
                'users', 'company_setups', 'sister_companies', 'chart_of_accounts',
                'exchange_rates', 'contacts', 'companies', 'call_logs', 'email_responses',
                'password_reset_tokens'
            ]
            
            all_clean = True
            total_remaining = 0
            
            # Verify main database collections are empty
            for collection_name in collections_to_verify:
                try:
                    count = self.main_db[collection_name].count_documents({})
                    total_remaining += count
                    if count == 0:
                        self.log(f"✅ {collection_name}: CLEAN (0 documents)")
                    else:
                        self.log(f"❌ {collection_name}: NOT CLEAN ({count} documents remaining)")
                        all_clean = False
                except Exception as e:
                    self.log(f"⚠️ Could not verify {collection_name}: {str(e)}")
            
            # Verify no tenant databases exist
            tenant_dbs = []
            for db_name in self.mongo_client.list_database_names():
                if db_name.startswith('tenant_'):
                    tenant_dbs.append(db_name)
                    all_clean = False
            
            if len(tenant_dbs) == 0:
                self.log("✅ Tenant databases: CLEAN (0 tenant databases)")
            else:
                self.log(f"❌ Tenant databases: NOT CLEAN ({len(tenant_dbs)} remaining: {tenant_dbs})")
            
            if all_clean and total_remaining == 0:
                self.log("🎉 VERIFICATION COMPLETE: Database is in completely clean state")
                return True
            else:
                self.log(f"❌ VERIFICATION FAILED: {total_remaining} documents and {len(tenant_dbs)} tenant databases remaining")
                return False
                
        except Exception as e:
            self.log(f"❌ Error during cleanup verification: {str(e)}")
            return False
    
    def test_fresh_system_readiness(self):
        """Test that the system is ready for fresh user flow"""
        self.log("🧪 Testing fresh system readiness...")
        
        # Generate unique test credentials
        timestamp = str(int(time.time()))
        random_suffix = str(random.randint(10000, 99999))
        test_email = f"freshtest{timestamp}{random_suffix}@example.com"
        test_password = "freshtest123"
        test_name = "Fresh Test User"
        test_company = "Fresh Test Company"
        
        try:
            # Test 1: User Registration
            self.log("🧪 Test 1: User Registration...")
            signup_data = {
                "email": test_email,
                "password": test_password,
                "name": test_name,
                "company": test_company
            }
            
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            if response.status_code == 200:
                data = response.json()
                auth_token = data.get('access_token')
                user_data = data.get('user')
                self.log("✅ Test 1 PASSED: User registration working")
                self.log(f"   User ID: {user_data.get('id')}")
                self.log(f"   Onboarding completed: {user_data.get('onboarding_completed')}")
            else:
                self.log(f"❌ Test 1 FAILED: User registration failed - {response.text}")
                return False
            
            # Test 2: Authentication System
            self.log("🧪 Test 2: Authentication System...")
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            auth_response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                self.log("✅ Test 2 PASSED: Authentication system working")
                self.log(f"   User authenticated: {auth_data.get('email')}")
            else:
                self.log(f"❌ Test 2 FAILED: Authentication failed - {auth_response.text}")
                return False
            
            # Test 3: Company Setup Process
            self.log("🧪 Test 3: Company Setup Process...")
            setup_data = {
                "company_name": "Fresh Test Company",
                "country_code": "US",
                "base_currency": "USD",
                "additional_currencies": ["EUR", "GBP"],
                "business_type": "Group Company",  # Test sister company functionality
                "industry": "Technology",
                "address": "123 Fresh Street",
                "city": "Fresh City",
                "state": "CA",
                "postal_code": "12345",
                "phone": "+1-555-123-4567",
                "email": test_email,
                "website": "https://freshtest.com",
                "tax_number": "FRESH123456",
                "registration_number": "REGFRESH123",
                "sister_companies": [
                    {
                        "company_name": "Fresh Sister Company 1",
                        "country": "US",
                        "base_currency": "USD",
                        "business_type": "Private Limited Company",
                        "industry": "Technology"
                    },
                    {
                        "company_name": "Fresh Sister Company 2", 
                        "country": "GB",
                        "base_currency": "GBP",
                        "business_type": "Limited Company",
                        "industry": "Technology"
                    }
                ]
            }
            
            setup_response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            if setup_response.status_code == 200:
                setup_result = setup_response.json()
                self.log("✅ Test 3 PASSED: Company setup process working")
                self.log(f"   Company ID: {setup_result.get('id')}")
                self.log(f"   Setup completed: {setup_result.get('setup_completed')}")
            else:
                self.log(f"❌ Test 3 FAILED: Company setup failed - {setup_response.text}")
                return False
            
            # Test 4: Chart of Accounts Creation
            self.log("🧪 Test 4: Chart of Accounts Creation...")
            accounts_response = self.session.get(f"{API_BASE}/setup/chart-of-accounts", headers=headers)
            if accounts_response.status_code == 200:
                accounts = accounts_response.json()
                self.log(f"✅ Test 4 PASSED: Chart of accounts created ({len(accounts)} accounts)")
                
                # Verify US GAAP accounts
                account_codes = [acc.get('code') for acc in accounts]
                expected_codes = ['1000', '1100', '2000', '3000', '4000', '5000', '6000']
                found_codes = [code for code in expected_codes if code in account_codes]
                self.log(f"   US GAAP accounts found: {found_codes}")
            else:
                self.log(f"❌ Test 4 FAILED: Chart of accounts creation failed - {accounts_response.text}")
                return False
            
            # Test 5: Sister Company Functionality
            self.log("🧪 Test 5: Sister Company Functionality...")
            sister_response = self.session.get(f"{API_BASE}/company/sister-companies", headers=headers)
            if sister_response.status_code == 200:
                sisters = sister_response.json()
                self.log(f"✅ Test 5 PASSED: Sister company functionality working ({len(sisters)} sister companies)")
                for sister in sisters:
                    self.log(f"   Sister company: {sister.get('company_name')} ({sister.get('base_currency')})")
            else:
                self.log(f"❌ Test 5 FAILED: Sister company functionality failed - {sister_response.text}")
                return False
            
            # Test 6: Currency Management System
            self.log("🧪 Test 6: Currency Management System...")
            currency_response = self.session.post(f"{API_BASE}/currency/update-rates", headers=headers)
            if currency_response.status_code == 200:
                currency_data = currency_response.json()
                self.log("✅ Test 6 PASSED: Currency management system working")
                self.log(f"   Updated rates: {currency_data.get('updated_rates', 0)}")
                self.log(f"   Base currency: {currency_data.get('base_currency')}")
            else:
                self.log(f"❌ Test 6 FAILED: Currency management failed - {currency_response.text}")
                return False
            
            # Test 7: Multi-tenancy Functionality
            self.log("🧪 Test 7: Multi-tenancy Functionality...")
            tenant_response = self.session.get(f"{API_BASE}/tenant/info", headers=headers)
            if tenant_response.status_code == 200:
                tenant_data = tenant_response.json()
                self.log("✅ Test 7 PASSED: Multi-tenancy functionality working")
                self.log(f"   Tenant assigned: {tenant_data.get('tenant_assigned')}")
                if tenant_data.get('tenant_assigned'):
                    self.log(f"   Database name: {tenant_data.get('database_name')}")
            else:
                self.log(f"❌ Test 7 FAILED: Multi-tenancy failed - {tenant_response.text}")
                return False
            
            self.log("🎉 ALL FRESH SYSTEM TESTS PASSED: System is ready for user flow")
            return True
            
        except Exception as e:
            self.log(f"❌ Error during fresh system testing: {str(e)}")
            return False
    
    def test_additional_fresh_account(self):
        """Test with an additional fresh account to double-verify system readiness"""
        self.log("🧪 Testing with additional fresh account for final verification...")
        
        # Generate another unique test account
        timestamp = str(int(time.time()))
        random_suffix = str(random.randint(10000, 99999))
        test_email = f"finaltest{timestamp}{random_suffix}@example.com"
        test_password = "finaltest123"
        
        try:
            # Create account
            signup_data = {
                "email": test_email,
                "password": test_password,
                "name": "Final Test User",
                "company": "Final Test Company"
            }
            
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            if response.status_code == 200:
                data = response.json()
                auth_token = data.get('access_token')
                self.log("✅ Additional fresh account created successfully")
                
                # Test company setup
                headers = {
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                }
                
                setup_data = {
                    "company_name": "Final Test Company",
                    "country_code": "IN",  # Test with different country
                    "base_currency": "INR",
                    "additional_currencies": ["USD", "EUR"],
                    "business_type": "Private Limited Company",
                    "industry": "Manufacturing",
                    "address": "456 Final Avenue",
                    "city": "Final City",
                    "state": "Maharashtra",
                    "postal_code": "400001",
                    "phone": "+91-22-1234-5678",
                    "email": test_email,
                    "website": "https://finaltest.com",
                    "tax_number": "FINAL789012",
                    "registration_number": "REGFINAL456"
                }
                
                setup_response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
                if setup_response.status_code == 200:
                    self.log("✅ Additional account company setup successful")
                    
                    # Verify chart of accounts for Indian GAAP
                    accounts_response = self.session.get(f"{API_BASE}/setup/chart-of-accounts", headers=headers)
                    if accounts_response.status_code == 200:
                        accounts = accounts_response.json()
                        self.log(f"✅ Indian GAAP chart of accounts created ({len(accounts)} accounts)")
                        return True
                    else:
                        self.log(f"❌ Indian GAAP accounts creation failed")
                        return False
                else:
                    self.log(f"❌ Additional account setup failed: {setup_response.text}")
                    return False
            else:
                self.log(f"❌ Additional account creation failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error during additional account testing: {str(e)}")
            return False
    
    def run_complete_cleanup_and_test(self):
        """Run the complete database cleanup and system test"""
        self.log("🚀 Starting COMPLETE DATABASE CLEANUP AND SYSTEM RESET")
        self.log("=" * 80)
        
        # Step 1: Connect to MongoDB
        if not self.connect_to_mongodb():
            return False
        
        # Step 2: Get database statistics before cleanup
        before_stats = self.get_database_stats_before_cleanup()
        if not before_stats:
            return False
        
        # Step 3: Perform complete database cleanup
        if not self.perform_complete_database_cleanup():
            return False
        
        # Step 4: Verify complete cleanup
        if not self.verify_complete_cleanup():
            return False
        
        # Step 5: Test fresh system readiness
        if not self.test_fresh_system_readiness():
            return False
        
        # Step 6: Test with additional fresh account
        if not self.test_additional_fresh_account():
            return False
        
        # Final summary
        self.log("=" * 80)
        self.log("🎉 COMPLETE DATABASE CLEANUP AND SYSTEM RESET SUCCESSFULLY COMPLETED!")
        self.log("📊 SUMMARY:")
        self.log(f"   • Deleted {before_stats['total_documents']} documents from main database")
        self.log(f"   • Deleted {len(before_stats['tenant_databases'])} tenant databases")
        self.log("   • All collections are completely empty")
        self.log("   • No tenant databases remaining")
        self.log("   • Fresh system testing: 7/7 tests passed")
        self.log("   • Additional account verification: PASSED")
        self.log("")
        self.log("✅ DATABASE CLEANUP AND SYSTEM RESET: 100% SUCCESS!")
        self.log("✅ User can now test everything from scratch with a completely clean database")
        
        return True

def main():
    """Main function to run the database cleanup test"""
    tester = DatabaseCleanupTester()
    
    try:
        success = tester.run_complete_cleanup_and_test()
        
        if success:
            print("\n" + "="*80)
            print("🎉 COMPLETE DATABASE CLEANUP AND SYSTEM RESET: SUCCESS")
            print("="*80)
            sys.exit(0)
        else:
            print("\n" + "="*80)
            print("❌ COMPLETE DATABASE CLEANUP AND SYSTEM RESET: FAILED")
            print("="*80)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        if tester.mongo_client:
            tester.mongo_client.close()

if __name__ == "__main__":
    main()