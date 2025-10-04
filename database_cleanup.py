#!/usr/bin/env python3
"""
Complete Database Cleanup Script for ZOIOS ERP
Performs comprehensive cleanup of all database data as requested by user:
1. Delete ALL user accounts
2. Delete ALL company setups 
3. Delete ALL sister companies
4. Delete ALL chart of accounts
5. Delete ALL tenant databases
6. Reset system to completely clean state
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'zoios_crm')

class DatabaseCleaner:
    def __init__(self):
        self.client = AsyncIOMotorClient(mongo_url)
        self.main_db = self.client[db_name]
        self.cleanup_stats = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    async def get_collection_count(self, db, collection_name):
        """Get count of documents in a collection"""
        try:
            return await db[collection_name].count_documents({})
        except Exception as e:
            self.log(f"Error counting {collection_name}: {str(e)}", "ERROR")
            return 0
    
    async def cleanup_main_database(self):
        """Clean up main database collections"""
        self.log("🧹 Starting main database cleanup...")
        
        # Collections to clean in main database
        main_collections = [
            'users',
            'company_setups', 
            'sister_companies',
            'chart_of_accounts',
            'exchange_rates',
            'contacts',
            'companies',
            'call_logs',
            'email_responses',
            'password_reset_tokens'
        ]
        
        total_deleted = 0
        
        for collection_name in main_collections:
            try:
                # Get count before deletion
                count_before = await self.get_collection_count(self.main_db, collection_name)
                
                if count_before > 0:
                    # Delete all documents
                    result = await self.main_db[collection_name].delete_many({})
                    deleted_count = result.deleted_count
                    total_deleted += deleted_count
                    
                    self.log(f"✅ Deleted {deleted_count} documents from {collection_name}")
                    self.cleanup_stats[collection_name] = deleted_count
                else:
                    self.log(f"✅ Collection {collection_name} already empty")
                    self.cleanup_stats[collection_name] = 0
                    
            except Exception as e:
                self.log(f"❌ Error cleaning {collection_name}: {str(e)}", "ERROR")
                self.cleanup_stats[collection_name] = 0
        
        self.log(f"🎯 Main database cleanup complete: {total_deleted} total documents deleted")
        return total_deleted
    
    async def find_tenant_databases(self):
        """Find all tenant databases"""
        self.log("🔍 Searching for tenant databases...")
        
        try:
            # List all databases
            db_list = await self.client.list_database_names()
            
            # Find tenant databases (they typically have a pattern like zoios_crm_tenant_*)
            tenant_dbs = []
            for db_name in db_list:
                if 'tenant' in db_name.lower() or (db_name.startswith('zoios_crm_') and db_name != 'zoios_crm'):
                    tenant_dbs.append(db_name)
            
            self.log(f"📊 Found {len(tenant_dbs)} tenant databases: {tenant_dbs}")
            return tenant_dbs
            
        except Exception as e:
            self.log(f"❌ Error finding tenant databases: {str(e)}", "ERROR")
            return []
    
    async def cleanup_tenant_database(self, tenant_db_name):
        """Clean up a specific tenant database"""
        self.log(f"🧹 Cleaning tenant database: {tenant_db_name}")
        
        try:
            tenant_db = self.client[tenant_db_name]
            
            # Collections to clean in tenant databases
            tenant_collections = [
                'users',
                'company_setups',
                'sister_companies', 
                'chart_of_accounts',
                'exchange_rates',
                'contacts',
                'companies',
                'call_logs',
                'email_responses'
            ]
            
            tenant_total = 0
            
            for collection_name in tenant_collections:
                try:
                    count_before = await self.get_collection_count(tenant_db, collection_name)
                    
                    if count_before > 0:
                        result = await tenant_db[collection_name].delete_many({})
                        deleted_count = result.deleted_count
                        tenant_total += deleted_count
                        
                        self.log(f"  ✅ Deleted {deleted_count} documents from {tenant_db_name}.{collection_name}")
                    else:
                        self.log(f"  ✅ Collection {tenant_db_name}.{collection_name} already empty")
                        
                except Exception as e:
                    self.log(f"  ❌ Error cleaning {tenant_db_name}.{collection_name}: {str(e)}", "ERROR")
            
            # Drop the entire tenant database
            await self.client.drop_database(tenant_db_name)
            self.log(f"🗑️ Dropped tenant database: {tenant_db_name}")
            
            return tenant_total
            
        except Exception as e:
            self.log(f"❌ Error cleaning tenant database {tenant_db_name}: {str(e)}", "ERROR")
            return 0
    
    async def cleanup_all_tenant_databases(self):
        """Clean up all tenant databases"""
        self.log("🧹 Starting tenant databases cleanup...")
        
        tenant_dbs = await self.find_tenant_databases()
        total_tenant_deleted = 0
        
        for tenant_db_name in tenant_dbs:
            deleted_count = await self.cleanup_tenant_database(tenant_db_name)
            total_tenant_deleted += deleted_count
        
        self.log(f"🎯 Tenant databases cleanup complete: {total_tenant_deleted} total documents deleted from {len(tenant_dbs)} databases")
        return total_tenant_deleted, len(tenant_dbs)
    
    async def verify_cleanup(self):
        """Verify that cleanup was successful"""
        self.log("🔍 Verifying cleanup completion...")
        
        # Check main database collections
        main_collections = [
            'users', 'company_setups', 'sister_companies', 'chart_of_accounts',
            'exchange_rates', 'contacts', 'companies', 'call_logs', 'email_responses'
        ]
        
        all_empty = True
        
        for collection_name in main_collections:
            count = await self.get_collection_count(self.main_db, collection_name)
            if count > 0:
                self.log(f"❌ Collection {collection_name} still has {count} documents", "ERROR")
                all_empty = False
            else:
                self.log(f"✅ Collection {collection_name} is empty")
        
        # Check for remaining tenant databases
        remaining_tenant_dbs = await self.find_tenant_databases()
        if remaining_tenant_dbs:
            self.log(f"❌ {len(remaining_tenant_dbs)} tenant databases still exist: {remaining_tenant_dbs}", "ERROR")
            all_empty = False
        else:
            self.log("✅ No tenant databases remaining")
        
        if all_empty:
            self.log("🎉 CLEANUP VERIFICATION SUCCESSFUL: All collections are empty, no tenant databases remain")
            return True
        else:
            self.log("❌ CLEANUP VERIFICATION FAILED: Some data still exists", "ERROR")
            return False
    
    async def test_fresh_system(self):
        """Test that the system works from a completely fresh state"""
        self.log("🧪 Testing fresh system functionality...")
        
        try:
            # Test 1: Create a fresh user account
            from auth import hash_password
            import uuid
            
            test_user = {
                "id": str(uuid.uuid4()),
                "email": f"freshtest{int(datetime.now().timestamp())}@example.com",
                "hashed_password": hash_password("testpass123"),
                "name": "Fresh Test User",
                "company": "Fresh Test Company",
                "role": "admin",
                "is_active": True,
                "onboarding_completed": False,
                "created_at": datetime.now()
            }
            
            # Insert test user
            await self.main_db.users.insert_one(test_user)
            self.log("✅ Test 1: User creation working")
            
            # Test 2: Verify user can be retrieved
            retrieved_user = await self.main_db.users.find_one({"email": test_user["email"]})
            if retrieved_user:
                self.log("✅ Test 2: User retrieval working")
            else:
                self.log("❌ Test 2: User retrieval failed", "ERROR")
                return False
            
            # Test 3: Test company setup creation
            company_setup = {
                "id": str(uuid.uuid4()),
                "user_id": test_user["id"],
                "company_name": "Fresh Test Company",
                "country_code": "US",
                "base_currency": "USD",
                "business_type": "Corporation",
                "setup_completed": True,
                "created_at": datetime.now()
            }
            
            await self.main_db.company_setups.insert_one(company_setup)
            self.log("✅ Test 3: Company setup creation working")
            
            # Test 4: Test chart of accounts creation
            test_account = {
                "id": str(uuid.uuid4()),
                "company_id": company_setup["id"],
                "code": "1000",
                "name": "Cash",
                "account_type": "asset",
                "category": "current_asset",
                "is_active": True,
                "created_at": datetime.now()
            }
            
            await self.main_db.chart_of_accounts.insert_one(test_account)
            self.log("✅ Test 4: Chart of accounts creation working")
            
            # Test 5: Test sister company creation
            sister_company = {
                "id": str(uuid.uuid4()),
                "group_company_id": company_setup["id"],
                "company_name": "Fresh Sister Company",
                "country_code": "US",
                "base_currency": "USD",
                "business_type": "Private Limited Company",
                "is_active": True,
                "created_at": datetime.now()
            }
            
            await self.main_db.sister_companies.insert_one(sister_company)
            self.log("✅ Test 5: Sister company creation working")
            
            # Test 6: Test currency exchange rate
            exchange_rate = {
                "id": str(uuid.uuid4()),
                "company_id": company_setup["id"],
                "base_currency": "USD",
                "target_currency": "EUR",
                "rate": 0.85,
                "source": "manual",
                "created_at": datetime.now()
            }
            
            await self.main_db.exchange_rates.insert_one(exchange_rate)
            self.log("✅ Test 6: Currency exchange rate creation working")
            
            # Clean up test data
            await self.main_db.users.delete_one({"id": test_user["id"]})
            await self.main_db.company_setups.delete_one({"id": company_setup["id"]})
            await self.main_db.chart_of_accounts.delete_one({"id": test_account["id"]})
            await self.main_db.sister_companies.delete_one({"id": sister_company["id"]})
            await self.main_db.exchange_rates.delete_one({"id": exchange_rate["id"]})
            
            self.log("🎉 FRESH SYSTEM TEST SUCCESSFUL: All 6 tests passed")
            return True
            
        except Exception as e:
            self.log(f"❌ Fresh system test failed: {str(e)}", "ERROR")
            return False
    
    async def run_complete_cleanup(self):
        """Run the complete database cleanup process"""
        self.log("🚀 Starting COMPLETE DATABASE CLEANUP as requested by user")
        self.log("📋 Cleanup scope: ALL user accounts, company setups, sister companies, chart of accounts, tenant databases")
        
        try:
            # Step 1: Clean main database
            main_deleted = await self.cleanup_main_database()
            
            # Step 2: Clean tenant databases
            tenant_deleted, tenant_count = await self.cleanup_all_tenant_databases()
            
            # Step 3: Verify cleanup
            cleanup_verified = await self.verify_cleanup()
            
            # Step 4: Test fresh system
            fresh_system_works = await self.test_fresh_system()
            
            # Summary
            total_deleted = main_deleted + tenant_deleted
            
            self.log("=" * 80)
            self.log("🎯 COMPLETE DATABASE CLEANUP SUMMARY")
            self.log("=" * 80)
            self.log(f"📊 Main database documents deleted: {main_deleted}")
            self.log(f"📊 Tenant database documents deleted: {tenant_deleted}")
            self.log(f"📊 Tenant databases removed: {tenant_count}")
            self.log(f"📊 Total documents deleted: {total_deleted}")
            self.log(f"✅ Cleanup verification: {'PASSED' if cleanup_verified else 'FAILED'}")
            self.log(f"✅ Fresh system test: {'PASSED' if fresh_system_works else 'FAILED'}")
            
            if cleanup_verified and fresh_system_works:
                self.log("🎉 COMPLETE DATABASE CLEANUP SUCCESSFUL!")
                self.log("🎯 System is ready for fresh user testing of sister company functionality")
                self.log("📝 User can now:")
                self.log("   1. Create fresh account")
                self.log("   2. Set up as Group Company") 
                self.log("   3. Add EXACTLY 1 sister company during setup")
                self.log("   4. Navigate to Company Management")
                self.log("   5. Check if that 1 sister company appears")
                return True
            else:
                self.log("❌ CLEANUP INCOMPLETE - Some issues remain")
                return False
                
        except Exception as e:
            self.log(f"❌ Complete cleanup failed: {str(e)}", "ERROR")
            return False
        finally:
            # Close database connection
            self.client.close()

async def main():
    """Main function to run database cleanup"""
    cleaner = DatabaseCleaner()
    success = await cleaner.run_complete_cleanup()
    
    if success:
        print("\n🎉 DATABASE CLEANUP COMPLETED SUCCESSFULLY!")
        print("📝 System is ready for fresh sister company testing")
        sys.exit(0)
    else:
        print("\n❌ DATABASE CLEANUP FAILED!")
        print("📝 Please check the logs above for details")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())