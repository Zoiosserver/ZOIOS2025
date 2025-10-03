from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from auth import (
    get_current_active_user, get_admin_user, create_access_token, 
    authenticate_user, hash_password, set_database, create_default_admin,
    User, UserCreate, UserSignup, UserLogin, Token, UserInDB, prepare_user_for_mongo, parse_user_from_mongo,
    PasswordReset, create_password_reset_token, verify_reset_token, use_reset_token,
    CompanySetup, CompanySetupCreate, ChartOfAccount, SisterCompany, SisterCompanyCreate, ConsolidatedAccount
)
from email_service import send_password_reset_email, send_welcome_email
from accounting_systems import (
    get_accounting_system, get_chart_of_accounts, get_currency_info, 
    get_country_info, get_available_countries, get_available_currencies
)
from currency_service import (
    CurrencyService, ExchangeRate, CurrencyRateUpdate, 
    get_currency_service, format_currency_amount
)
from tenant_service import get_tenant_service, TenantService
from tenant_middleware import get_tenant_middleware

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Set database for auth module
set_database(db)

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class ContactStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    OPPORTUNITY = "opportunity"
    CUSTOMER = "customer"
    CLOSED = "closed"

class CallDisposition(str, Enum):
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    CALLBACK = "callback"
    FOLLOW_UP = "follow_up"
    BUSY = "busy"
    VOICEMAIL = "voicemail"

class EmailStatus(str, Enum):
    SENT = "sent"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    NO_RESPONSE = "no_response"

# Models
class Contact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Add user_id for data isolation
    name: str
    email: str
    phone: Optional[str] = None
    company: str
    position: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    lead_source: Optional[str] = None
    status: ContactStatus = ContactStatus.NEW
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContactCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: str
    position: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    lead_source: Optional[str] = None
    status: ContactStatus = ContactStatus.NEW
    notes: Optional[str] = None

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    lead_source: Optional[str] = None
    status: Optional[ContactStatus] = None
    notes: Optional[str] = None

class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Add user_id for data isolation
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    contacts_count: int = 0
    engagement_score: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

class CallLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Add user_id for data isolation
    contact_id: str
    contact_name: str
    date: datetime
    duration: int  # in minutes
    outcome: str
    notes: Optional[str] = None
    disposition: CallDisposition
    follow_up_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CallLogCreate(BaseModel):
    contact_id: str
    contact_name: str
    date: datetime
    duration: int
    outcome: str
    notes: Optional[str] = None
    disposition: CallDisposition
    follow_up_date: Optional[datetime] = None

class EmailResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Add user_id for data isolation
    contact_id: str
    contact_name: str
    email_type: str  # "outreach", "follow_up", "proposal", etc.
    subject: str
    date: datetime
    status: EmailStatus
    response_type: Optional[str] = None  # "positive", "negative", "neutral"
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EmailResponseCreate(BaseModel):
    contact_id: str
    contact_name: str
    email_type: str
    subject: str
    date: datetime
    status: EmailStatus
    response_type: Optional[str] = None
    notes: Optional[str] = None

# Helper functions
def prepare_for_mongo(data):
    """Convert datetime objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, dict):
                data[key] = prepare_for_mongo(value)
    return data

def parse_from_mongo(item):
    """Convert ISO strings back to datetime objects"""
    if isinstance(item, dict):
        for key, value in item.items():
            if key in ['created_at', 'updated_at', 'date', 'follow_up_date'] and isinstance(value, str):
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    pass  # Keep original value if parsing fails
    return item

# Helper function to get data filter based on user role
def get_user_filter(current_user: UserInDB):
    """Returns MongoDB filter based on user role"""
    if current_user.role == "admin":
        return {}  # Admin sees all data
    else:
        return {"user_id": current_user.id}  # Regular user sees only their data

# Authentication Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, current_user: UserInDB = Depends(get_admin_user)):
    """Admin-only endpoint to create new users"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    user = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "hashed_password": hashed_password,
        "name": user_data.name,
        "company": user_data.company,
        "role": user_data.role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
    
    prepared_user = prepare_user_for_mongo(user)
    await db.users.insert_one(prepared_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    user_response = User(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        company=user["company"],
        role=user["role"],
        is_active=user["is_active"],
        onboarding_completed=user["onboarding_completed"],
        created_at=user["created_at"]
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@api_router.post("/auth/signup", response_model=Token)
async def public_signup(user_data: UserSignup):
    """Public signup endpoint for new users"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user with 'user' role (not admin)
    hashed_password = hash_password(user_data.password)
    user = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "hashed_password": hashed_password,
        "name": user_data.name,
        "company": user_data.company,
        "role": "user",  # Always create as regular user
        "is_active": True,
        "onboarding_completed": False,  # Require company setup
        "created_at": datetime.now(timezone.utc)
    }
    
    prepared_user = prepare_user_for_mongo(user)
    await db.users.insert_one(prepared_user)
    
    # Send welcome email
    try:
        base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        email_sent = await send_welcome_email(
            email=user["email"],
            user_name=user["name"],
            user_company=user["company"],
            user_role=user["role"],
            base_url=base_url
        )
        if email_sent:
            print(f"✅ Welcome email sent to {user['email']}")
        else:
            print(f"❌ Failed to send welcome email to {user['email']}")
    except Exception as e:
        print(f"❌ Error sending welcome email: {str(e)}")
        # Don't fail signup if email fails
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    user_response = User(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        company=user["company"],
        role=user["role"],
        is_active=user["is_active"],
        onboarding_completed=user["onboarding_completed"],
        created_at=user["created_at"]
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@api_router.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """User login endpoint"""
    user = await authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    user_response = User(
        id=user.id,
        email=user.email,
        name=user.name,
        company=user.company,
        role=user.role,
        is_active=user.is_active,
        onboarding_completed=user.onboarding_completed,
        created_at=user.created_at
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@api_router.post("/auth/forgot-password")
async def forgot_password(email: str):
    """Forgot password endpoint - sends reset instructions via email"""
    try:
        # Check if user exists
        user = await db.users.find_one({"email": email})
        if user:
            # Generate reset token
            reset_token = await create_password_reset_token(user["id"])
            
            # Get base URL for reset link (you might want to make this configurable)
            base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            
            # Send reset email
            email_sent = await send_password_reset_email(
                email=email,
                user_name=user["name"],
                reset_token=reset_token,
                base_url=base_url
            )
            
            if email_sent:
                print(f"✅ Password reset email sent to {email}")
            else:
                print(f"❌ Failed to send password reset email to {email}")
        
        # Always return success message for security (don't reveal if email exists)
        return {"message": "If the email exists, password reset instructions have been sent"}
        
    except Exception as e:
        print(f"❌ Error in forgot password: {str(e)}")
        return {"message": "If the email exists, password reset instructions have been sent"}

@api_router.post("/auth/reset-password")
async def reset_password(password_reset: PasswordReset):
    """Reset password using the reset token"""
    try:
        # Verify the reset token
        reset_token = await verify_reset_token(password_reset.token)
        if not reset_token:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired reset token"
            )
        
        # Get the user
        user = await db.users.find_one({"id": reset_token["user_id"]})
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        # Update the password
        new_hashed_password = hash_password(password_reset.new_password)
        await db.users.update_one(
            {"id": reset_token["user_id"]},
            {"$set": {
                "hashed_password": new_hashed_password,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Mark the token as used
        await use_reset_token(password_reset.token)
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in reset password: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to reset password"
        )

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user information"""
    return User(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        company=current_user.company,
        role=current_user.role,
        is_active=current_user.is_active,
        onboarding_completed=current_user.onboarding_completed,
        created_at=current_user.created_at
    )

# Admin Routes
@api_router.get("/admin/users", response_model=List[User])
async def get_all_users(current_user: UserInDB = Depends(get_admin_user)):
    """Admin-only endpoint to get all users"""
    users = await db.users.find().to_list(length=None)
    return [User(**parse_user_from_mongo(user)) for user in users]

@api_router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, current_user: UserInDB = Depends(get_admin_user)):
    """Admin-only endpoint to delete a user"""
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# Company Setup Routes
@api_router.get("/setup/countries")
async def get_countries():
    """Get available countries with accounting systems"""
    return get_available_countries()

@api_router.get("/setup/currencies") 
async def get_currencies():
    """Get available currencies"""
    return get_available_currencies()

@api_router.get("/setup/accounting-system/{country_code}")
async def get_country_accounting_system(country_code: str):
    """Get accounting system details for a country"""
    accounting_system = get_accounting_system(country_code)
    if not accounting_system:
        raise HTTPException(status_code=404, detail="Country not supported")
    return accounting_system

@api_router.post("/setup/company", response_model=CompanySetup)
async def setup_company(
    company_data: CompanySetupCreate, 
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Setup company details and accounting system with multi-tenant support"""
    # Check if user already has completed setup
    if current_user.onboarding_completed:
        raise HTTPException(status_code=400, detail="Company setup already completed")
    
    # Get accounting system details
    accounting_system = get_accounting_system(company_data.country_code)
    
    # Create company setup
    company_setup = CompanySetup(
        user_id=current_user.id,
        company_name=company_data.company_name,
        country_code=company_data.country_code,
        accounting_system=accounting_system["name"],
        base_currency=company_data.base_currency,
        additional_currencies=company_data.additional_currencies,
        fiscal_year_start=company_data.fiscal_year_start or accounting_system["fiscal_year_start"],
        business_type=company_data.business_type,
        industry=company_data.industry,
        address=company_data.address,
        city=company_data.city,
        state=company_data.state,
        postal_code=company_data.postal_code,
        phone=company_data.phone,
        email=company_data.email,
        website=company_data.website,
        tax_number=company_data.tax_number,
        registration_number=company_data.registration_number,
        setup_completed=True
    )
    
    # Initialize multi-tenant architecture
    tenant_service = await get_tenant_service(mongo_url)
    
    # Create tenant database for this company
    tenant_db = await tenant_service.get_tenant_database(company_setup.id)
    
    # Assign user to this tenant
    await tenant_service.assign_user_to_tenant(current_user.email, company_setup.id)
    
    # Save company setup to tenant database
    prepared_company = prepare_for_mongo(company_setup.dict())
    await tenant_db.company_setups.insert_one(prepared_company)
    
    # Also save user to tenant database
    prepared_user = prepare_user_for_mongo(current_user.dict())
    await tenant_db.users.insert_one(prepared_user)
    
    # Create chart of accounts based on accounting system in tenant database
    chart_template = get_chart_of_accounts(accounting_system["chart_of_accounts"])
    accounts_to_create = []
    
    for category, accounts in chart_template.items():
        for account in accounts:
            chart_account = ChartOfAccount(
                company_id=company_setup.id,
                code=account["code"],
                name=account["name"],
                account_type=account["type"],
                category=account["category"]
            )
            accounts_to_create.append(prepare_for_mongo(chart_account.dict()))
    
    if accounts_to_create:
        await tenant_db.chart_of_accounts.insert_many(accounts_to_create)
    
    # Set up initial currency exchange rates if additional currencies are configured
    if company_data.additional_currencies:
        try:
            currency_service = await get_currency_service(tenant_db)
            await currency_service.update_company_rates(
                company_id=company_setup.id,
                base_currency=company_data.base_currency,
                target_currencies=company_data.additional_currencies,
                source="online"
            )
        except Exception as e:
            # Log error but don't fail the setup process
            logger.warning(f"Failed to fetch initial currency rates: {e}")
    
    # Update user onboarding status in both main database and tenant database
    update_data = {
        "onboarding_completed": True,
        "company_id": company_setup.id,  # Link user to company
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Update in main database for authentication
    await db.users.update_one({"id": current_user.id}, {"$set": update_data})
    
    # Update in tenant database
    await tenant_db.users.update_one({"id": current_user.id}, {"$set": update_data})
    
    return company_setup

@api_router.get("/tenant/info")
async def get_tenant_info(current_user: UserInDB = Depends(get_current_active_user)):
    """Get tenant information for current user"""
    try:
        tenant_service = await get_tenant_service(mongo_url)
        tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
        
        if tenant_db is None:
            return {
                "tenant_assigned": False,
                "message": "User not assigned to any tenant database"
            }
        
        stats = await tenant_service.get_tenant_stats(current_user.company_id if hasattr(current_user, 'company_id') else 'unknown')
        
        return {
            "tenant_assigned": True,
            "database_name": tenant_db.name,
            "user_email": current_user.email,
            "stats": stats
        }
        
    except Exception as e:
        return {
            "tenant_assigned": False,
            "error": str(e)
        }

@api_router.get("/setup/company", response_model=CompanySetup)
async def get_company_setup(current_user: UserInDB = Depends(get_current_active_user)):
    """Get user's company setup"""
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        # Fallback to main database for users without tenant setup
        company_setup = await db.company_setups.find_one({"user_id": current_user.id})
    else:
        company_setup = await tenant_db.company_setups.find_one({"user_id": current_user.id})
    
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    return CompanySetup(**parse_from_mongo(company_setup))

@api_router.get("/setup/chart-of-accounts")
async def get_user_chart_of_accounts(current_user: UserInDB = Depends(get_current_active_user)):
    """Get user's chart of accounts"""
    # Get user's company setup
    company_setup = await db.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    # Get chart of accounts
    accounts = await db.chart_of_accounts.find(
        {"company_id": company_setup["id"], "is_active": True}
    ).to_list(length=None)
    
    return [ChartOfAccount(**parse_from_mongo(account)) for account in accounts]

# Currency Management Routes
@api_router.get("/currency/rates", response_model=List[ExchangeRate])
async def get_company_exchange_rates(current_user: UserInDB = Depends(get_current_active_user)):
    """Get all exchange rates for the current user's company"""
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        # Fallback to main database
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    # Get company setup to find company_id
    company_setup = await db_to_use.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    currency_service = await get_currency_service(db_to_use)
    rates = await currency_service.get_company_rates(
        company_id=company_setup["id"],
        base_currency=company_setup.get("base_currency")
    )
    
    return rates

@api_router.post("/currency/update-rates")
async def update_exchange_rates(current_user: UserInDB = Depends(get_current_active_user)):
    """Update exchange rates from online sources"""
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        # Fallback to main database
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    # Get company setup
    company_setup = await db_to_use.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    base_currency = company_setup.get("base_currency")
    additional_currencies = company_setup.get("additional_currencies", [])
    
    if not additional_currencies:
        return {"success": True, "message": "No additional currencies configured"}
    
    currency_service = await get_currency_service(db_to_use)
    result = await currency_service.update_company_rates(
        company_id=company_setup["id"],
        base_currency=base_currency,
        target_currencies=additional_currencies,
        source="online"
    )
    
    return result

@api_router.post("/currency/set-manual-rate")
async def set_manual_exchange_rate(
    rate_update: CurrencyRateUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Set a manual exchange rate"""
    # Get company setup
    company_setup = await db.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    currency_service = await get_currency_service(db)
    rate = await currency_service.set_manual_rate(
        company_id=company_setup["id"],
        base_currency=rate_update.base_currency,
        target_currency=rate_update.target_currency,
        rate=rate_update.rate
    )
    
    return rate

@api_router.post("/currency/convert")
async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Convert amount between currencies"""
    # Get company setup
    company_setup = await db.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    currency_service = await get_currency_service(db)
    
    try:
        result = await currency_service.convert_amount(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            company_id=company_setup["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Sister Company Management Routes
@api_router.post("/company/sister-companies", response_model=SisterCompany)
async def add_sister_company(
    sister_company: SisterCompanyCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Add a sister company to the group"""
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        # Fallback to main database
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    # Get company setup to verify it's a group company
    company_setup = await db_to_use.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(
            status_code=404, 
            detail="Please complete your main company setup before adding sister companies"
        )
    
    if company_setup.get("business_type") != "Group Company":
        raise HTTPException(
            status_code=400, 
            detail="Only group companies can add sister companies. Your business type is: " + company_setup.get("business_type", "Unknown")
        )
    
    # Create sister company
    sister_company_data = SisterCompany(
        group_company_id=company_setup["id"],
        **sister_company.dict()
    )
    
    # Save to database
    prepared_company = prepare_for_mongo(sister_company_data.dict())
    await db_to_use.sister_companies.insert_one(prepared_company)
    
    # Create chart of accounts for sister company
    from accounting_systems import get_accounting_system, get_chart_of_accounts
    accounting_system = get_accounting_system(sister_company.country_code)
    chart_template = get_chart_of_accounts(accounting_system["chart_of_accounts"])
    
    accounts_to_create = []
    for category, accounts in chart_template.items():
        for account in accounts:
            chart_account = ChartOfAccount(
                company_id=sister_company_data.id,
                code=account["code"],
                name=account["name"],
                account_type=account["type"],
                category=account["category"]
            )
            accounts_to_create.append(prepare_for_mongo(chart_account.dict()))
    
    if accounts_to_create:
        await db_to_use.chart_of_accounts.insert_many(accounts_to_create)
    
    return sister_company_data

@api_router.get("/company/sister-companies", response_model=List[SisterCompany])
async def get_sister_companies(current_user: UserInDB = Depends(get_current_active_user)):
    """Get all sister companies for the group"""
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        # Fallback to main database
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    company_setup = await db_to_use.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    sister_companies = await db_to_use.sister_companies.find({
        "group_company_id": company_setup["id"],
        "is_active": True
    }).to_list(length=None)
    
    return [SisterCompany(**parse_from_mongo(company)) for company in sister_companies]

@api_router.delete("/company/sister-companies/{sister_company_id}")
async def delete_sister_company(
    sister_company_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Delete a sister company"""
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        # Fallback to main database
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    company_setup = await db_to_use.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    # Verify the sister company belongs to this group
    sister_company = await db_to_use.sister_companies.find_one({
        "id": sister_company_id,
        "group_company_id": company_setup["id"]
    })
    
    if not sister_company:
        raise HTTPException(status_code=404, detail="Sister company not found")
    
    # Soft delete
    await db_to_use.sister_companies.update_one(
        {"id": sister_company_id},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Sister company deleted successfully"}

@api_router.get("/company/consolidated-accounts", response_model=List[ConsolidatedAccount])
async def get_consolidated_accounts(current_user: UserInDB = Depends(get_current_active_user)):
    """Get consolidated accounts for group company"""
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        # Fallback to main database
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    company_setup = await db_to_use.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    if company_setup.get("business_type") != "Group Company":
        raise HTTPException(status_code=400, detail="Only group companies have consolidated accounts")
    
    # Get all sister companies
    sister_companies = await db_to_use.sister_companies.find({
        "group_company_id": company_setup["id"],
        "is_active": True
    }).to_list(length=None)
    
    # Get parent company chart of accounts
    parent_accounts = await db_to_use.chart_of_accounts.find({
        "company_id": company_setup["id"],
        "is_active": True
    }).to_list(length=None)
    
    consolidated_accounts = []
    
    for parent_account in parent_accounts:
        consolidated_account = ConsolidatedAccount(
            group_company_id=company_setup["id"],
            account_code=parent_account["code"],
            account_name=parent_account["name"],
            account_type=parent_account["account_type"],
            category=parent_account["category"],
            consolidated_balance=0.0,
            sister_companies_data=[]
        )
        
        # Add main company data
        main_company_data = {
            "company_id": company_setup["id"],
            "company_name": company_setup["company_name"],
            "balance": parent_account.get("current_balance", 0.0),
            "ownership_percentage": 100.0
        }
        consolidated_account.sister_companies_data.append(main_company_data)
        consolidated_account.consolidated_balance += main_company_data["balance"]
        
        # Find matching accounts in sister companies
        for sister_company in sister_companies:
            sister_account = await db_to_use.chart_of_accounts.find_one({
                "company_id": sister_company["id"],
                "code": parent_account["code"],
                "is_active": True
            })
            
            if sister_account:
                sister_data = {
                    "company_id": sister_company["id"],
                    "company_name": sister_company["company_name"],
                    "balance": sister_account.get("current_balance", 0.0),
                    "ownership_percentage": sister_company.get("ownership_percentage", 100.0)
                }
                consolidated_account.sister_companies_data.append(sister_data)
                # Add weighted balance based on ownership percentage
                weighted_balance = sister_data["balance"] * (sister_data["ownership_percentage"] / 100.0)
                consolidated_account.consolidated_balance += weighted_balance
        
        consolidated_accounts.append(consolidated_account)
    
    return consolidated_accounts

@api_router.get("/company/{company_id}/chart-of-accounts")
async def get_company_chart_of_accounts(
    company_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get chart of accounts for a specific company"""
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        # Fallback to main database
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    # Verify user has access to this company
    company_setup = await db_to_use.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    # Check if this is the main company or a sister company
    if company_id == company_setup["id"]:
        # Main company
        company_name = company_setup["company_name"]
        company_info = {
            "id": company_setup["id"],
            "name": company_setup["company_name"],
            "business_type": company_setup["business_type"],
            "country_code": company_setup["country_code"],
            "base_currency": company_setup["base_currency"],
            "is_main_company": True
        }
    else:
        # Check if it's a sister company
        sister_company = await db_to_use.sister_companies.find_one({
            "id": company_id,
            "group_company_id": company_setup["id"],
            "is_active": True
        })
        
        if not sister_company:
            raise HTTPException(status_code=403, detail="Access denied to this company")
        
        company_info = {
            "id": sister_company["id"],
            "name": sister_company["company_name"],
            "business_type": sister_company["business_type"],
            "country_code": sister_company["country_code"],
            "base_currency": sister_company["base_currency"],
            "is_main_company": False,
            "ownership_percentage": sister_company.get("ownership_percentage", 100.0)
        }
    
    # Get chart of accounts for this company
    chart_accounts = await db_to_use.chart_of_accounts.find({
        "company_id": company_id,
        "is_active": True
    }).to_list(length=None)
    
    # Group accounts by category
    accounts_by_category = {}
    for account in chart_accounts:
        category = account.get("category", "Other")
        if category not in accounts_by_category:
            accounts_by_category[category] = []
        accounts_by_category[category].append({
            "id": account["id"],
            "code": account["code"],
            "name": account["name"],
            "account_type": account["account_type"],
            "category": account["category"],
            "balance": 0.0  # This would come from actual transactions
        })
    
    return {
        "company": company_info,
        "accounts_by_category": accounts_by_category,
        "total_accounts": len(chart_accounts)
    }

@api_router.get("/company/list")
async def get_accessible_companies(current_user: UserInDB = Depends(get_current_active_user)):
    """Get list of companies user can access"""
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        # Fallback to main database
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    # Get main company
    company_setup = await db_to_use.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    companies = [{
        "id": company_setup["id"],
        "name": company_setup["company_name"],
        "business_type": company_setup["business_type"],
        "country_code": company_setup["country_code"],
        "base_currency": company_setup["base_currency"],
        "is_main_company": True
    }]
    
    # Get sister companies if this is a group company
    if company_setup.get("business_type") == "Group Company":
        sister_companies = await db_to_use.sister_companies.find({
            "group_company_id": company_setup["id"],
            "is_active": True
        }).to_list(length=None)
        
        for sister_company in sister_companies:
            companies.append({
                "id": sister_company["id"],
                "name": sister_company["company_name"],
                "business_type": sister_company["business_type"],
                "country_code": sister_company["country_code"],
                "base_currency": sister_company["base_currency"],
                "is_main_company": False,
                "ownership_percentage": sister_company.get("ownership_percentage", 100.0)
            })
    
    return companies

@api_router.post("/company/{company_id}/accounts")
async def add_account_to_company(
    company_id: str,
    account_data: dict,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Add a new account to company's chart of accounts"""
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    # Verify user has access to this company
    company_setup = await db_to_use.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    # Check if this is the main company or a sister company
    if company_id == company_setup["id"]:
        # Main company - user has access
        pass
    else:
        # Check if it's a sister company
        sister_company = await db_to_use.sister_companies.find_one({
            "id": company_id,
            "group_company_id": company_setup["id"],
            "is_active": True
        })
        
        if not sister_company:
            raise HTTPException(status_code=403, detail="Access denied to this company")
    
    # Create new account
    from uuid import uuid4
    account_id = str(uuid4())
    
    new_account = {
        "id": account_id,
        "company_id": company_id,
        "code": account_data.get("code"),
        "name": account_data.get("name"),
        "account_type": account_data.get("account_type"),
        "category": account_data.get("category"),
        "opening_balance": account_data.get("opening_balance", 0.0),
        "current_balance": account_data.get("opening_balance", 0.0),
        "balance": account_data.get("opening_balance", 0.0),  # Add balance field for compatibility
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": current_user.id
    }
    
    # Check if account code already exists
    existing_account = await db_to_use.chart_of_accounts.find_one({
        "company_id": company_id,
        "code": account_data.get("code"),
        "is_active": True
    })
    
    if existing_account:
        raise HTTPException(status_code=400, detail=f"Account code {account_data.get('code')} already exists")
    
    await db_to_use.chart_of_accounts.insert_one(prepare_for_mongo(new_account))
    
    return {"success": True, "account": new_account}

@api_router.put("/company/{company_id}/accounts/{account_id}/opening-balance")
async def update_account_opening_balance(
    company_id: str,
    account_id: str,
    balance_data: dict,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Update opening balance for an account"""
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    # Verify user has access to this company
    company_setup = await db_to_use.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    # Check access to company
    if company_id != company_setup["id"]:
        sister_company = await db_to_use.sister_companies.find_one({
            "id": company_id,
            "group_company_id": company_setup["id"],
            "is_active": True
        })
        
        if not sister_company:
            raise HTTPException(status_code=403, detail="Access denied to this company")
    
    # Update account opening balance
    opening_balance = balance_data.get("opening_balance", 0.0)
    
    result = await db_to_use.chart_of_accounts.update_one(
        {"id": account_id, "company_id": company_id, "is_active": True},
        {
            "$set": {
                "opening_balance": opening_balance,
                "current_balance": opening_balance,  # Reset current balance to opening balance
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": current_user.id
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {"success": True, "message": "Opening balance updated successfully"}

@api_router.get("/users/company-assignments")
async def get_user_company_assignments(current_user: UserInDB = Depends(get_current_active_user)):
    """Get user company assignments and roles"""
    # Only admin users can access this endpoint
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admin role required.")
    
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    # Get all users in this tenant
    users = await db_to_use.users.find({}).to_list(length=None)
    
    # Get company setup
    company_setup = await db_to_use.company_setups.find_one({"user_id": current_user.id})
    if not company_setup:
        raise HTTPException(status_code=404, detail="Company setup not found")
    
    # Get sister companies
    sister_companies = await db_to_use.sister_companies.find({
        "group_company_id": company_setup["id"],
        "is_active": True
    }).to_list(length=None)
    
    companies = [company_setup] + sister_companies
    
    user_assignments = []
    for user in users:
        user_data = {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user.get("role", "user"),
            "is_active": user.get("is_active", True),
            "company_assignments": []
        }
        
        # Check which companies this user has access to
        for company in companies:
            # For now, all users in tenant have access to all companies
            # This can be enhanced with specific role-based access
            user_data["company_assignments"].append({
                "company_id": company["id"],
                "company_name": company.get("company_name", "Unknown"),
                "role": "viewer" if user.get("role") != "admin" else "admin",
                "can_edit": user.get("role") == "admin"
            })
        
        user_assignments.append(user_data)
    
    return {
        "users": user_assignments,
        "companies": companies
    }

@api_router.post("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_data: dict,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Update user role"""
    # Only admin users can update roles
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admin role required.")
    
    # Get tenant database for user
    tenant_service = await get_tenant_service(mongo_url)
    tenant_db = await tenant_service.get_user_tenant_database(current_user.email)
    
    if tenant_db is None:
        db_to_use = db
    else:
        db_to_use = tenant_db
    
    new_role = role_data.get("role")
    if new_role not in ["admin", "user", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    result = await db_to_use.users.update_one(
        {"id": user_id},
        {"$set": {"role": new_role, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "message": "User role updated successfully"}

# Dashboard and Analytics
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: UserInDB = Depends(get_current_active_user)):
    """Get key statistics for the dashboard"""
    # Get user filter
    user_filter = get_user_filter(current_user)
    
    # Count totals
    total_contacts = await db.contacts.count_documents(user_filter)
    total_companies = await db.companies.count_documents(user_filter)
    total_calls = await db.call_logs.count_documents(user_filter)
    total_emails = await db.email_responses.count_documents(user_filter)
    
    # Contact status distribution
    contact_pipeline = [
        {"$match": user_filter},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    contact_status_data = await db.contacts.aggregate(contact_pipeline).to_list(length=None)
    
    # Call disposition distribution
    call_pipeline = [
        {"$match": user_filter},
        {"$group": {"_id": "$disposition", "count": {"$sum": 1}}}
    ]
    call_disposition_data = await db.call_logs.aggregate(call_pipeline).to_list(length=None)
    
    # Email status distribution
    email_pipeline = [
        {"$match": user_filter},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    email_status_data = await db.email_responses.aggregate(email_pipeline).to_list(length=None)
    
    # Recent activity (contacts added per day for last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    activity_pipeline = [
        {"$match": {**user_filter, "created_at": {"$gte": thirty_days_ago.isoformat()}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": {"$dateFromString": {"dateString": "$created_at"}}}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    activity_data = await db.contacts.aggregate(activity_pipeline).to_list(length=None)
    
    return {
        "totals": {
            "contacts": total_contacts,
            "companies": total_companies,
            "calls": total_calls,
            "emails": total_emails
        },
        "contact_status": contact_status_data,
        "call_disposition": call_disposition_data,
        "email_status": email_status_data,
        "activity_trend": activity_data
    }

# Contact Routes
@api_router.post("/contacts", response_model=Contact)
async def create_contact(contact: ContactCreate, current_user: UserInDB = Depends(get_current_active_user)):
    contact_dict = contact.dict()
    contact_dict['user_id'] = current_user.id  # Add user_id
    contact_obj = Contact(**contact_dict)
    prepared_data = prepare_for_mongo(contact_obj.dict())
    await db.contacts.insert_one(prepared_data)
    return contact_obj

@api_router.get("/contacts", response_model=List[Contact])
async def get_contacts(current_user: UserInDB = Depends(get_current_active_user), skip: int = 0, limit: int = 100):
    user_filter = get_user_filter(current_user)
    contacts = await db.contacts.find(user_filter).skip(skip).limit(limit).to_list(length=None)
    return [Contact(**parse_from_mongo(contact)) for contact in contacts]

@api_router.get("/contacts/{contact_id}", response_model=Contact)
async def get_contact(contact_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    user_filter = get_user_filter(current_user)
    contact = await db.contacts.find_one({**user_filter, "id": contact_id})
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return Contact(**parse_from_mongo(contact))

@api_router.put("/contacts/{contact_id}", response_model=Contact)
async def update_contact(contact_id: str, contact_update: ContactUpdate, current_user: UserInDB = Depends(get_current_active_user)):
    user_filter = get_user_filter(current_user)
    update_data = {k: v for k, v in contact_update.dict().items() if v is not None}
    update_data['updated_at'] = datetime.now(timezone.utc)
    prepared_data = prepare_for_mongo(update_data)
    
    result = await db.contacts.update_one(
        {**user_filter, "id": contact_id}, 
        {"$set": prepared_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    updated_contact = await db.contacts.find_one({**user_filter, "id": contact_id})
    return Contact(**parse_from_mongo(updated_contact))

@api_router.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    user_filter = get_user_filter(current_user)
    result = await db.contacts.delete_one({**user_filter, "id": contact_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted successfully"}

# Company Routes
@api_router.post("/companies", response_model=Company)
async def create_company(company: CompanyCreate, current_user: UserInDB = Depends(get_current_active_user)):
    company_dict = company.dict()
    company_dict['user_id'] = current_user.id  # Add user_id
    company_obj = Company(**company_dict)
    prepared_data = prepare_for_mongo(company_obj.dict())
    await db.companies.insert_one(prepared_data)
    return company_obj

@api_router.get("/companies", response_model=List[Company])
async def get_companies(current_user: UserInDB = Depends(get_current_active_user), skip: int = 0, limit: int = 100):
    user_filter = get_user_filter(current_user)
    companies = await db.companies.find(user_filter).skip(skip).limit(limit).to_list(length=None)
    return [Company(**parse_from_mongo(company)) for company in companies]

@api_router.get("/companies/{company_id}", response_model=Company)
async def get_company(company_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    user_filter = get_user_filter(current_user)
    company = await db.companies.find_one({**user_filter, "id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return Company(**parse_from_mongo(company))

# Call Log Routes
@api_router.post("/call-logs", response_model=CallLog)
async def create_call_log(call_log: CallLogCreate, current_user: UserInDB = Depends(get_current_active_user)):
    call_dict = call_log.dict()
    call_dict['user_id'] = current_user.id  # Add user_id
    call_obj = CallLog(**call_dict)
    prepared_data = prepare_for_mongo(call_obj.dict())
    await db.call_logs.insert_one(prepared_data)
    return call_obj

@api_router.get("/call-logs", response_model=List[CallLog])
async def get_call_logs(current_user: UserInDB = Depends(get_current_active_user), skip: int = 0, limit: int = 100):
    user_filter = get_user_filter(current_user)
    call_logs = await db.call_logs.find(user_filter).sort("date", -1).skip(skip).limit(limit).to_list(length=None)
    return [CallLog(**parse_from_mongo(call_log)) for call_log in call_logs]

@api_router.get("/call-logs/contact/{contact_id}", response_model=List[CallLog])
async def get_contact_call_logs(contact_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    user_filter = get_user_filter(current_user)
    call_logs = await db.call_logs.find({**user_filter, "contact_id": contact_id}).sort("date", -1).to_list(length=None)
    return [CallLog(**parse_from_mongo(call_log)) for call_log in call_logs]

# Email Response Routes
@api_router.post("/email-responses", response_model=EmailResponse)
async def create_email_response(email_response: EmailResponseCreate, current_user: UserInDB = Depends(get_current_active_user)):
    email_dict = email_response.dict()
    email_dict['user_id'] = current_user.id  # Add user_id
    email_obj = EmailResponse(**email_dict)
    prepared_data = prepare_for_mongo(email_obj.dict())
    await db.email_responses.insert_one(prepared_data)
    return email_obj

@api_router.get("/email-responses", response_model=List[EmailResponse])
async def get_email_responses(current_user: UserInDB = Depends(get_current_active_user), skip: int = 0, limit: int = 100):
    user_filter = get_user_filter(current_user)
    email_responses = await db.email_responses.find(user_filter).sort("date", -1).skip(skip).limit(limit).to_list(length=None)
    return [EmailResponse(**parse_from_mongo(email_response)) for email_response in email_responses]

@api_router.get("/email-responses/contact/{contact_id}", response_model=List[EmailResponse])
async def get_contact_email_responses(contact_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    user_filter = get_user_filter(current_user)
    email_responses = await db.email_responses.find({**user_filter, "contact_id": contact_id}).sort("date", -1).to_list(length=None)
    return [EmailResponse(**parse_from_mongo(email_response)) for email_response in email_responses]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Create default admin user
    await create_default_admin()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
