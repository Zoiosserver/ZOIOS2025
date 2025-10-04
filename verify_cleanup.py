#!/usr/bin/env python3
"""
Simple verification script to confirm database cleanup was successful
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'zoios_crm')

async def verify_cleanup():
    """Verify that database cleanup was successful"""
    client = AsyncIOMotorClient(mongo_url)
    main_db = client[db_name]
    
    print("🔍 Verifying database cleanup...")
    
    # Check main database collections
    main_collections = [
        'users', 'company_setups', 'sister_companies', 'chart_of_accounts',
        'exchange_rates', 'contacts', 'companies', 'call_logs', 'email_responses'
    ]
    
    all_empty = True
    total_documents = 0
    
    for collection_name in main_collections:
        count = await main_db[collection_name].count_documents({})
        total_documents += count
        if count > 0:
            print(f"❌ Collection {collection_name} still has {count} documents")
            all_empty = False
        else:
            print(f"✅ Collection {collection_name} is empty")
    
    # Check for remaining tenant databases
    db_list = await client.list_database_names()
    tenant_dbs = [db for db in db_list if 'tenant' in db.lower() or (db.startswith('zoios_crm_') and db != 'zoios_crm')]
    
    if tenant_dbs:
        print(f"❌ {len(tenant_dbs)} tenant databases still exist: {tenant_dbs}")
        all_empty = False
    else:
        print("✅ No tenant databases remaining")
    
    client.close()
    
    if all_empty:
        print("🎉 DATABASE CLEANUP VERIFICATION SUCCESSFUL!")
        print(f"📊 Total documents in main database: {total_documents}")
        print(f"📊 Tenant databases remaining: {len(tenant_dbs)}")
        print("🎯 System is ready for fresh user testing of sister company functionality")
        return True
    else:
        print("❌ DATABASE CLEANUP VERIFICATION FAILED")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_cleanup())
    exit(0 if success else 1)