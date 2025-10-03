from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import hashlib
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uuid

# Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Simple password hashing using hashlib (for demo purposes)
def hash_password(password: str) -> str:
    return hashlib.sha256(f"{password}salt_zoios".encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

# OAuth2 scheme
security = HTTPBearer()

# Database connection (will be set from main app)
db = None

def set_database(database):
    global db
    db = database

# Models
class User(BaseModel):
    id: str
    email: str
    name: str
    company: str
    role: str  # "admin" or "user"
    is_active: bool = True
    onboarding_completed: bool = False
    created_at: datetime

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    company: str
    role: str = "user"

class UserSignup(BaseModel):
    email: str
    password: str
    name: str
    company: str

class CompanySetup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    company_name: str
    country_code: str
    accounting_system: str
    base_currency: str
    additional_currencies: List[str] = []
    fiscal_year_start: str  # MM-DD format
    business_type: str
    industry: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    tax_number: Optional[str] = None
    registration_number: Optional[str] = None
    setup_completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CompanySetupCreate(BaseModel):
    company_name: str
    country_code: str
    base_currency: str
    additional_currencies: List[str] = []
    business_type: str
    industry: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    tax_number: Optional[str] = None
    registration_number: Optional[str] = None

class ChartOfAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    code: str
    name: str
    account_type: str  # asset, liability, equity, revenue, expense
    category: str  # current_asset, fixed_asset, etc.
    parent_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SisterCompany(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_company_id: str  # Reference to the parent group company
    company_name: str
    country_code: str
    base_currency: str
    accounting_system: Optional[str] = None
    business_type: str
    industry: str
    incorporation_date: Optional[str] = None
    ownership_percentage: Optional[float] = 100.0  # Percentage owned by group
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SisterCompanyCreate(BaseModel):
    company_name: str
    country_code: str
    base_currency: str
    accounting_system: Optional[str] = None
    business_type: str
    industry: str
    incorporation_date: Optional[str] = None
    ownership_percentage: Optional[float] = 100.0

class ConsolidatedAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_company_id: str
    account_code: str
    account_name: str
    account_type: str
    category: str
    consolidated_balance: float = 0.0
    sister_companies_data: List[Dict] = []  # Individual company balances
    consolidation_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PasswordResetToken(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PasswordReset(BaseModel):
    token: str
    new_password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Password utilities (using the functions defined above)

# JWT utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_by_email(email: str):
    user = await db.users.find_one({"email": email})
    if user:
        return UserInDB(**user)
    return None

async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_admin_user(current_user: UserInDB = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Helper function to prepare user data for MongoDB
def prepare_user_for_mongo(user_data):
    if isinstance(user_data.get('created_at'), datetime):
        user_data['created_at'] = user_data['created_at'].isoformat()
    return user_data

def parse_user_from_mongo(user):
    if isinstance(user.get('created_at'), str):
        try:
            user['created_at'] = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
        except ValueError:
            pass
    return user

# Create default admin user
async def create_default_admin():
    """Create default admin user if none exists"""
    admin_exists = await db.users.find_one({"role": "admin"})
    if not admin_exists:
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": "admin@zoios.com",
            "hashed_password": hash_password("admin123"),
            "name": "Admin User",
            "company": "ZOIOS",
            "role": "admin",
            "is_active": True,
            "onboarding_completed": True,  # Admin doesn't need onboarding
            "created_at": datetime.now(timezone.utc)
        }
        prepared_admin = prepare_user_for_mongo(admin_user)
        await db.users.insert_one(prepared_admin)
        print("✅ Default admin user created: admin@zoios.com / admin123")

# Password reset token utilities
def generate_reset_token():
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)

async def create_password_reset_token(user_id: str):
    """Create and store a password reset token"""
    token = generate_reset_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)  # 24 hours expiry
    
    reset_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    prepared_token = prepare_user_for_mongo(reset_token.dict())
    await db.password_reset_tokens.insert_one(prepared_token)
    
    return token

async def verify_reset_token(token: str):
    """Verify and return the reset token if valid"""
    reset_token = await db.password_reset_tokens.find_one({
        "token": token,
        "used": False,
        "expires_at": {"$gt": datetime.now(timezone.utc).isoformat()}
    })
    
    if not reset_token:
        return None
    
    return parse_user_from_mongo(reset_token)

async def use_reset_token(token: str):
    """Mark a reset token as used"""
    await db.password_reset_tokens.update_one(
        {"token": token},
        {"$set": {"used": True}}
    )