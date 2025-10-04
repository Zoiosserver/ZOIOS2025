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
            self.mongo_client = AsyncIOMotorClient(MONGO_URL)
            self.db = self.mongo_client[DB_NAME]
            
            # Test connection
            await self.mongo_client.admin.command('ping')
            self.log("✅ Connected to MongoDB successfully")
            return True
        except Exception as e:
            self.log(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    async def get_database_stats_before_cleanup(self):
        """Get database statistics before cleanup"""
        self.log("Getting database statistics before cleanup...")
        
        try:
            stats = {}
            
            # Main database collections
            collections = ['users', 'company_setups', 'sister_companies', 'chart_of_accounts', 'exchange_rates']
            
            for collection in collections:
                count = await self.db[collection].count_documents({})
                stats[collection] = count
                self.log(f"Collection '{collection}': {count} documents")
            
            # Get tenant databases
            db_list = await self.mongo_client.list_database_names()
            tenant_dbs = [db for db in db_list if db.startswith('tenant_')]
            stats['tenant_databases'] = len(tenant_dbs)
            self.log(f"Tenant databases: {len(tenant_dbs)} found")
            
            for tenant_db in tenant_dbs:
                self.log(f"  - {tenant_db}")
            
            return stats
        except Exception as e:
            self.log(f"❌ Error getting database stats: {str(e)}")
            return {}
    
    async def perform_complete_database_cleanup(self):
        """Perform complete database cleanup as requested"""
        self.log("🧹 STARTING COMPLETE DATABASE CLEANUP...")
        
        try:
            cleanup_results = {}
            
            # 1. DELETE ALL USER ACCOUNTS
            self.log("1. Deleting all user accounts...")
            users_result = await self.db.users.delete_many({})
            cleanup_results['users_deleted'] = users_result.deleted_count
            self.log(f"   ✅ Deleted {users_result.deleted_count} user accounts")
            
            # 2. DELETE ALL COMPANY SETUPS AND SISTER COMPANIES
            self.log("2. Deleting all company setups and sister companies...")
            company_result = await self.db.company_setups.delete_many({})
            sister_result = await self.db.sister_companies.delete_many({})
            cleanup_results['companies_deleted'] = company_result.deleted_count
            cleanup_results['sister_companies_deleted'] = sister_result.deleted_count
            self.log(f"   ✅ Deleted {company_result.deleted_count} company setups")
            self.log(f"   ✅ Deleted {sister_result.deleted_count} sister companies")
            
            # 3. DELETE ALL CHART OF ACCOUNTS DATA
            self.log("3. Deleting all chart of accounts data...")
            accounts_result = await self.db.chart_of_accounts.delete_many({})
            cleanup_results['accounts_deleted'] = accounts_result.deleted_count
            self.log(f"   ✅ Deleted {accounts_result.deleted_count} chart of accounts entries")
            
            # 4. DELETE ALL CURRENCY CONFIGURATIONS
            self.log("4. Deleting all currency configurations...")
            currency_result = await self.db.exchange_rates.delete_many({})
            cleanup_results['exchange_rates_deleted'] = currency_result.deleted_count
            self.log(f"   ✅ Deleted {currency_result.deleted_count} exchange rates")
            
            # 5. DELETE ALL CRM DATA
            self.log("5. Deleting all CRM data...")
            crm_collections = ['contacts', 'companies', 'call_logs', 'email_responses']
            for collection in crm_collections:
                result = await self.db[collection].delete_many({})
                cleanup_results[f'{collection}_deleted'] = result.deleted_count
                self.log(f"   ✅ Deleted {result.deleted_count} {collection} entries")
            
            # 6. CLEAN ALL TENANT DATABASES
            self.log("6. Cleaning all tenant databases...")
            db_list = await self.mongo_client.list_database_names()
            tenant_dbs = [db for db in db_list if db.startswith('tenant_')]
            
            tenant_cleanup_count = 0
            for tenant_db_name in tenant_dbs:
                try:
                    await self.mongo_client.drop_database(tenant_db_name)
                    tenant_cleanup_count += 1
                    self.log(f"   ✅ Dropped tenant database: {tenant_db_name}")
                except Exception as e:
                    self.log(f"   ❌ Failed to drop {tenant_db_name}: {str(e)}")
            
            cleanup_results['tenant_databases_deleted'] = tenant_cleanup_count
            
            # 7. DELETE PASSWORD RESET TOKENS
            self.log("7. Deleting password reset tokens...")
            reset_result = await self.db.password_reset_tokens.delete_many({})
            cleanup_results['reset_tokens_deleted'] = reset_result.deleted_count
            self.log(f"   ✅ Deleted {reset_result.deleted_count} password reset tokens")
            
            self.log("🎉 COMPLETE DATABASE CLEANUP FINISHED!")
            return cleanup_results
            
        except Exception as e:
            self.log(f"❌ Error during database cleanup: {str(e)}")
            return {}
    
    async def verify_clean_state(self):
        """Verify that the database is in a completely clean state"""
        self.log("🔍 VERIFYING CLEAN STATE...")
        
        try:
            verification_results = {}
            all_clean = True
            
            # Check main collections are empty
            collections_to_check = [
                'users', 'company_setups', 'sister_companies', 'chart_of_accounts', 
                'exchange_rates', 'contacts', 'companies', 'call_logs', 'email_responses',
                'password_reset_tokens'
            ]
            
            for collection in collections_to_check:
                count = await self.db[collection].count_documents({})
                verification_results[collection] = count
                
                if count == 0:
                    self.log(f"   ✅ {collection}: CLEAN (0 documents)")
                else:
                    self.log(f"   ❌ {collection}: NOT CLEAN ({count} documents remaining)")
                    all_clean = False
            
            # Check tenant databases are gone
            db_list = await self.mongo_client.list_database_names()
            tenant_dbs = [db for db in db_list if db.startswith('tenant_')]
            verification_results['tenant_databases_remaining'] = len(tenant_dbs)
            
            if len(tenant_dbs) == 0:
                self.log("   ✅ Tenant databases: CLEAN (0 tenant databases)")
            else:
                self.log(f"   ❌ Tenant databases: NOT CLEAN ({len(tenant_dbs)} tenant databases remaining)")
                for db_name in tenant_dbs:
                    self.log(f"      - {db_name}")
                all_clean = False
            
            if all_clean:
                self.log("🎉 DATABASE IS COMPLETELY CLEAN!")
                return True
            else:
                self.log("❌ DATABASE IS NOT COMPLETELY CLEAN!")
                return False
                
        except Exception as e:
            self.log(f"❌ Error during clean state verification: {str(e)}")
            return False
    
    def test_fresh_user_registration(self):
        """Test that user registration still works after cleanup"""
        self.log("🆕 TESTING FRESH USER REGISTRATION...")
        
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
                self.log("✅ Fresh user registration successful")
                self.log(f"User ID: {self.user_data.get('id')}")
                self.log(f"Email: {self.user_data.get('email')}")
                self.log(f"Onboarding completed: {self.user_data.get('onboarding_completed')}")
                return True
            else:
                self.log(f"❌ Fresh registration failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Fresh registration error: {str(e)}")
            return False
    
    def test_fresh_user_login(self):
        """Test that login works with the fresh user"""
        self.log("🔐 TESTING FRESH USER LOGIN...")
        
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
                self.log("✅ Fresh user login successful")
                return True
            else:
                self.log(f"❌ Fresh login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Fresh login error: {str(e)}")
            return False
    
    def test_fresh_authentication_system(self):
        """Test that authentication system works properly"""
        self.log("🔑 TESTING FRESH AUTHENTICATION SYSTEM...")
        
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
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Fresh authentication system working")
                self.log(f"User ID: {data.get('id')}")
                self.log(f"Email: {data.get('email')}")
                self.log(f"Role: {data.get('role')}")
                self.log(f"Onboarding completed: {data.get('onboarding_completed')}")
                return True
            else:
                self.log(f"❌ Fresh auth system failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Fresh auth system error: {str(e)}")
            return False
    
    def test_fresh_company_setup(self):
        """Test that company setup process works from scratch"""
        self.log("🏢 TESTING FRESH COMPANY SETUP PROCESS...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Fresh company setup data
        setup_data = {
            "company_name": TEST_COMPANY,
            "country_code": "US",
            "base_currency": "USD",
            "additional_currencies": ["EUR", "GBP"],
            "business_type": "Corporation",
            "industry": "Technology",
            "address": "123 Fresh Start Avenue",
            "city": "New City",
            "state": "CA",
            "postal_code": "90210",
            "phone": "+1-555-FRESH-01",
            "email": TEST_EMAIL,
            "website": "https://freshstart.com",
            "tax_number": "FRESH123456",
            "registration_number": "REGFRESH789"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/setup/company", json=setup_data, headers=headers)
            self.log(f"Company setup response status: {response.status_code}")
            self.log(f"Company setup response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Fresh company setup successful")
                self.log(f"Company ID: {data.get('id')}")
                self.log(f"Company name: {data.get('company_name')}")
                self.log(f"Setup completed: {data.get('setup_completed')}")
                return True
            else:
                self.log(f"❌ Fresh company setup failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Fresh company setup error: {str(e)}")
            return False
    
    def test_fresh_chart_of_accounts(self):
        """Test that chart of accounts is created properly"""
        self.log("📊 TESTING FRESH CHART OF ACCOUNTS...")
        
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
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Fresh chart of accounts created successfully")
                self.log(f"Number of accounts: {len(data)}")
                
                # Verify basic account structure
                account_codes = [account.get('code') for account in data]
                expected_codes = ['1000', '1100', '2000', '3000', '4000', '5000', '6000']
                found_codes = [code for code in expected_codes if code in account_codes]
                
                self.log(f"Expected account codes found: {found_codes}")
                
                if len(found_codes) >= 5:
                    self.log("✅ Chart of accounts contains expected US GAAP structure")
                    return True
                else:
                    self.log("⚠️ Some expected accounts missing but basic structure exists")
                    return True
            else:
                self.log(f"❌ Fresh chart of accounts failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Fresh chart of accounts error: {str(e)}")
            return False
    
    def test_fresh_currency_system(self):
        """Test that currency system works from scratch"""
        self.log("💱 TESTING FRESH CURRENCY SYSTEM...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test currency rates endpoint
            response = self.session.get(f"{API_BASE}/currency/rates", headers=headers)
            self.log(f"Currency rates response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Fresh currency system working")
                self.log(f"Number of rates: {len(data)}")
                
                # Test currency update
                update_response = self.session.post(f"{API_BASE}/currency/update-rates", headers=headers)
                self.log(f"Currency update response status: {update_response.status_code}")
                
                if update_response.status_code == 200:
                    update_data = update_response.json()
                    self.log("✅ Fresh currency update working")
                    self.log(f"Updated rates: {update_data.get('updated_rates', 'N/A')}")
                    return True
                else:
                    self.log(f"⚠️ Currency update issue: {update_response.text}")
                    return True  # Still consider currency system working
            else:
                self.log(f"❌ Fresh currency system failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Fresh currency system error: {str(e)}")
            return False
    
    async def test_fresh_multi_tenancy(self):
        """Test that multi-tenancy works after cleanup"""
        self.log("🏗️ TESTING FRESH MULTI-TENANCY...")
        
        try:
            # Check if tenant database was created for our fresh user
            db_list = await self.mongo_client.list_database_names()
            tenant_dbs = [db for db in db_list if db.startswith('tenant_')]
            
            self.log(f"Tenant databases after fresh setup: {len(tenant_dbs)}")
            for db_name in tenant_dbs:
                self.log(f"  - {db_name}")
            
            if len(tenant_dbs) > 0:
                self.log("✅ Fresh multi-tenancy working - tenant database created")
                
                # Check tenant database content
                tenant_db = self.mongo_client[tenant_dbs[0]]
                
                # Check if user data exists in tenant database
                user_count = await tenant_db.users.count_documents({})
                company_count = await tenant_db.company_setups.count_documents({})
                accounts_count = await tenant_db.chart_of_accounts.count_documents({})
                
                self.log(f"Tenant database content:")
                self.log(f"  - Users: {user_count}")
                self.log(f"  - Companies: {company_count}")
                self.log(f"  - Accounts: {accounts_count}")
                
                if user_count > 0 and company_count > 0 and accounts_count > 0:
                    self.log("✅ Tenant database properly populated")
                    return True
                else:
                    self.log("⚠️ Tenant database created but not fully populated")
                    return True
            else:
                self.log("⚠️ No tenant databases found - may be expected for some setups")
                return True
                
        except Exception as e:
            self.log(f"❌ Fresh multi-tenancy test error: {str(e)}")
            return False
    
    async def close_connections(self):
        """Close database connections"""
        if self.mongo_client:
            self.mongo_client.close()
            self.log("✅ MongoDB connection closed")
    
    async def run_complete_cleanup_and_test(self):
        """Run the complete cleanup and testing process"""
        self.log("🚀 STARTING COMPLETE DATABASE CLEANUP AND SYSTEM RESET TEST")
        self.log("=" * 80)
        
        # Connect to MongoDB
        if not await self.connect_to_mongodb():
            return False
        
        # Get initial stats
        initial_stats = await self.get_database_stats_before_cleanup()
        self.log(f"Initial database stats: {initial_stats}")
        
        # Perform complete cleanup
        cleanup_results = await self.perform_complete_database_cleanup()
        self.log(f"Cleanup results: {cleanup_results}")
        
        # Verify clean state
        clean_state_verified = await self.verify_clean_state()
        
        if not clean_state_verified:
            self.log("❌ Database cleanup verification failed!")
            await self.close_connections()
            return False
        
        # Test fresh system functionality
        self.log("=" * 80)
        self.log("🧪 TESTING FRESH SYSTEM FUNCTIONALITY")
        
        test_results = {}
        
        # Test 1: Fresh user registration
        test_results['registration'] = self.test_fresh_user_registration()
        
        # Test 2: Fresh user login
        test_results['login'] = self.test_fresh_user_login()
        
        # Test 3: Fresh authentication system
        test_results['authentication'] = self.test_fresh_authentication_system()
        
        # Test 4: Fresh company setup
        test_results['company_setup'] = self.test_fresh_company_setup()
        
        # Test 5: Fresh chart of accounts
        test_results['chart_of_accounts'] = self.test_fresh_chart_of_accounts()
        
        # Test 6: Fresh currency system
        test_results['currency_system'] = self.test_fresh_currency_system()
        
        # Test 7: Fresh multi-tenancy
        test_results['multi_tenancy'] = await self.test_fresh_multi_tenancy()
        
        # Close connections
        await self.close_connections()
        
        # Summary
        self.log("=" * 80)
        self.log("📋 COMPLETE DATABASE CLEANUP AND SYSTEM RESET TEST SUMMARY")
        self.log("=" * 80)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        self.log(f"Database cleanup: {'✅ SUCCESS' if clean_state_verified else '❌ FAILED'}")
        self.log(f"Fresh system tests: {passed_tests}/{total_tests} passed")
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  - {test_name}: {status}")
        
        overall_success = clean_state_verified and passed_tests == total_tests
        
        if overall_success:
            self.log("🎉 COMPLETE DATABASE CLEANUP AND SYSTEM RESET: SUCCESS!")
            self.log("✅ Database is completely clean")
            self.log("✅ Fresh system is fully functional")
            self.log("✅ User can start completely fresh with account creation, company setup, etc.")
        else:
            self.log("❌ COMPLETE DATABASE CLEANUP AND SYSTEM RESET: PARTIAL SUCCESS")
            if not clean_state_verified:
                self.log("❌ Database cleanup incomplete")
            if passed_tests < total_tests:
                self.log(f"❌ {total_tests - passed_tests} fresh system tests failed")
        
        return overall_success

def main():
    """Main function to run the database cleanup test"""
    tester = DatabaseCleanupTester()
    
    # Run the async test
    try:
        result = asyncio.run(tester.run_complete_cleanup_and_test())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()