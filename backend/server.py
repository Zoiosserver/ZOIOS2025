from fastapi import FastAPI, APIRouter, HTTPException, Depends
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
    authenticate_user, get_password_hash, set_database, create_default_admin,
    User, UserCreate, UserLogin, Token, UserInDB, prepare_user_for_mongo, parse_user_from_mongo
)

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
    hashed_password = get_password_hash(user_data.password)
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
        created_at=user.created_at
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
