"""
Tenant middleware for multi-tenant database routing
"""

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from tenant_service import get_tenant_service, get_tenant_database_for_user
import logging

logger = logging.getLogger(__name__)

class TenantMiddleware:
    """Middleware to handle tenant database routing"""
    
    def __init__(self, mongo_url: str):
        self.mongo_url = mongo_url
        self.security = HTTPBearer()
    
    async def get_tenant_database_from_token(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        Extract user info from JWT token and return appropriate tenant database
        """
        try:
            token = credentials.credentials
            secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
            
            # Decode JWT token
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            user_email = payload.get("sub")
            
            if not user_email:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Get tenant database for user
            tenant_service = await get_tenant_service(self.mongo_url)
            tenant_db = await tenant_service.get_user_tenant_database(user_email)
            
            if not tenant_db:
                # User not assigned to any tenant, might be a new user
                # For new users, we'll handle this in the registration process
                raise HTTPException(status_code=404, detail="User tenant not found")
            
            return {
                "database": tenant_db,
                "user_email": user_email,
                "tenant_service": tenant_service
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Error in tenant middleware: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

# Global middleware instance
tenant_middleware = None

def get_tenant_middleware(mongo_url: str) -> TenantMiddleware:
    """Get or create tenant middleware instance"""
    global tenant_middleware
    if tenant_middleware is None:
        tenant_middleware = TenantMiddleware(mongo_url)
    return tenant_middleware