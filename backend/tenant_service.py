"""
Multi-tenant database service for ZOIOS ERP
Each group company gets its own database for complete data isolation
"""

import re
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Optional
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class TenantService:
    """Service for managing multi-tenant database architecture"""
    
    def __init__(self, mongo_url: str):
        self.mongo_url = mongo_url
        self.client = AsyncIOMotorClient(mongo_url)
        self.databases: Dict[str, any] = {}  # Cache for database connections
        
    def get_tenant_db_name(self, company_id: str) -> str:
        """
        Generate database name for a tenant
        Format: zoios_tenant_[sanitized_company_id]
        """
        # Sanitize company_id for database name (only alphanumeric and underscores)
        sanitized_id = re.sub(r'[^a-zA-Z0-9_]', '_', company_id.lower())
        return f"zoios_tenant_{sanitized_id}"
    
    async def get_tenant_database(self, company_id: str):
        """
        Get or create tenant-specific database
        """
        if not company_id:
            raise ValueError("Company ID is required for tenant database access")
            
        db_name = self.get_tenant_db_name(company_id)
        
        # Return cached database connection if exists
        if db_name in self.databases:
            return self.databases[db_name]
        
        # Create new database connection
        database = self.client[db_name]
        self.databases[db_name] = database
        
        # Initialize tenant database with required collections and indexes
        await self._initialize_tenant_database(database)
        
        logger.info(f"Tenant database initialized: {db_name}")
        return database
    
    async def _initialize_tenant_database(self, database):
        """
        Initialize a new tenant database with required collections and indexes
        """
        try:
            # Create collections with indexes for better performance
            collections_to_create = [
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
            
            for collection_name in collections_to_create:
                collection = database[collection_name]
                
                # Create indexes based on collection type
                if collection_name == 'users':
                    await collection.create_index("email", unique=True)
                    await collection.create_index("id", unique=True)
                elif collection_name == 'company_setups':
                    await collection.create_index("user_id", unique=True)
                    await collection.create_index("id", unique=True)
                elif collection_name == 'sister_companies':
                    await collection.create_index("group_company_id")
                    await collection.create_index("id", unique=True)
                elif collection_name == 'chart_of_accounts':
                    await collection.create_index("company_id")
                    await collection.create_index([("company_id", 1), ("code", 1)], unique=True)
                elif collection_name == 'exchange_rates':
                    await collection.create_index("company_id")
                    await collection.create_index([("company_id", 1), ("base_currency", 1), ("target_currency", 1)], unique=True)
                else:
                    # Default indexes for other collections
                    await collection.create_index("id", unique=True)
                    if collection_name in ['contacts', 'companies', 'call_logs', 'email_responses']:
                        await collection.create_index("created_by")
            
            # Create tenant metadata collection
            metadata_collection = database['tenant_metadata']
            await metadata_collection.create_index("tenant_id", unique=True)
            
            # Insert tenant initialization metadata
            await metadata_collection.update_one(
                {"tenant_id": database.name},
                {
                    "$set": {
                        "initialized_at": datetime.now(timezone.utc),
                        "version": "1.0",
                        "collections_created": collections_to_create
                    }
                },
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error initializing tenant database: {e}")
            raise
    
    async def get_user_tenant_database(self, user_email: str):
        """
        Get tenant database for a specific user by finding their company
        """
        try:
            # First, check the main database to find which tenant the user belongs to
            main_db = self.client['zoios_main']
            user_tenant_mapping = await main_db.user_tenant_mappings.find_one(
                {"user_email": user_email}
            )
            
            if not user_tenant_mapping:
                # User not found in any tenant, they might be new
                return None
                
            company_id = user_tenant_mapping['company_id']
            return await self.get_tenant_database(company_id)
            
        except Exception as e:
            logger.error(f"Error getting user tenant database: {e}")
            return None
    
    async def assign_user_to_tenant(self, user_email: str, company_id: str):
        """
        Assign a user to a specific tenant (company database)
        """
        try:
            main_db = self.client['zoios_main']
            await main_db.user_tenant_mappings.update_one(
                {"user_email": user_email},
                {
                    "$set": {
                        "user_email": user_email,
                        "company_id": company_id,
                        "assigned_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            
            logger.info(f"User {user_email} assigned to tenant {company_id}")
            
        except Exception as e:
            logger.error(f"Error assigning user to tenant: {e}")
            raise
    
    async def list_tenant_databases(self):
        """
        List all tenant databases
        """
        database_names = await self.client.list_database_names()
        tenant_dbs = [name for name in database_names if name.startswith('zoios_tenant_')]
        return tenant_dbs
    
    async def get_tenant_stats(self, company_id: str):
        """
        Get statistics for a specific tenant
        """
        database = await self.get_tenant_database(company_id)
        
        stats = {
            "database_name": database.name,
            "collections": {},
            "total_documents": 0
        }
        
        collection_names = await database.list_collection_names()
        
        for collection_name in collection_names:
            if collection_name != 'tenant_metadata':
                collection = database[collection_name]
                count = await collection.count_documents({})
                stats["collections"][collection_name] = count
                stats["total_documents"] += count
        
        return stats

# Global tenant service instance
tenant_service = None

async def get_tenant_service(mongo_url: str) -> TenantService:
    """Get or create tenant service instance"""
    global tenant_service
    if tenant_service is None:
        tenant_service = TenantService(mongo_url)
    return tenant_service

async def get_tenant_database_for_user(user_email: str, mongo_url: str):
    """Helper function to get tenant database for a user"""
    service = await get_tenant_service(mongo_url)
    return await service.get_user_tenant_database(user_email)