"""
Currency exchange rate service for multi-currency functionality
Supports both online rate fetching and manual rate management
"""

import asyncio
import aiohttp
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

# Helper function for MongoDB preparation
def prepare_for_mongo(data):
    """Prepare data for MongoDB storage"""
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if v is not None}
    return data

logger = logging.getLogger(__name__)

class ExchangeRate(BaseModel):
    id: str
    base_currency: str
    target_currency: str
    rate: float
    source: str  # "online", "manual", "system"
    last_updated: datetime
    is_active: bool = True
    company_id: Optional[str] = None

class CurrencyRateUpdate(BaseModel):
    base_currency: str
    target_currency: str
    rate: float
    source: str = "manual"

class CurrencyService:
    """Service for managing currency exchange rates"""
    
    def __init__(self, db):
        self.db = db
        self.online_providers = {
            "exchangerate-api": {
                "url": "https://v6.exchangerate-api.com/v6/latest/{base_currency}",
                "requires_key": False,  # They have a free tier
                "rate_limit": 1500,  # requests per month for free
            },
            "fixer": {
                "url": "http://data.fixer.io/api/latest?access_key={api_key}&base={base_currency}",
                "requires_key": True,
                "rate_limit": 1000,  # requests per month for free
            },
            "currencyapi": {
                "url": "https://api.currencyapi.com/v3/latest?apikey={api_key}&base_currency={base_currency}",
                "requires_key": True,
                "rate_limit": 300,  # requests per month for free
            }
        }
        
    async def fetch_online_rates(
        self, 
        base_currency: str, 
        target_currencies: List[str] = None,
        provider: str = "exchangerate-api"
    ) -> Dict[str, float]:
        """
        Fetch currency exchange rates from online providers
        """
        try:
            if provider not in self.online_providers:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Use different APIs based on provider
            if provider == "exchangerate-api":
                return await self._fetch_from_exchangerate_api(base_currency, target_currencies)
            elif provider == "fixer":
                # Would need API key for Fixer
                logger.warning("Fixer.io requires API key - falling back to exchangerate-api")
                return await self._fetch_from_exchangerate_api(base_currency, target_currencies)
            elif provider == "currencyapi":
                # Would need API key for CurrencyAPI
                logger.warning("CurrencyAPI requires API key - falling back to exchangerate-api")
                return await self._fetch_from_exchangerate_api(base_currency, target_currencies)
            
        except Exception as e:
            logger.error(f"Failed to fetch online rates: {e}")
            return {}
    
    async def _fetch_from_exchangerate_api(
        self, 
        base_currency: str, 
        target_currencies: List[str] = None
    ) -> Dict[str, float]:
        """Fetch rates from exchangerate-api.com (free tier)"""
        try:
            url = f"https://v6.exchangerate-api.com/v6/latest/{base_currency}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("result") == "success":
                            rates = data.get("conversion_rates", {})
                            
                            # Filter to target currencies if specified
                            if target_currencies:
                                rates = {
                                    currency: rate 
                                    for currency, rate in rates.items() 
                                    if currency in target_currencies
                                }
                            
                            return rates
                        else:
                            logger.error(f"API error: {data.get('error-type', 'Unknown error')}")
                            return {}
                    else:
                        logger.error(f"HTTP error: {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Error fetching from exchangerate-api: {e}")
            return {}
    
    async def update_company_rates(
        self,
        company_id: str,
        base_currency: str,
        target_currencies: List[str],
        source: str = "online"
    ) -> Dict[str, Any]:
        """Update exchange rates for a company"""
        try:
            if source == "online":
                # Try to fetch from online sources first
                try:
                    online_rates = await self.fetch_online_rates(base_currency, target_currencies)
                except Exception:
                    # If online fetch fails, use fallback mock rates
                    online_rates = await self._get_fallback_rates(base_currency, target_currencies)
                
                updated_count = 0
                for target_currency in target_currencies:
                    if target_currency in online_rates:
                        rate_data = ExchangeRate(
                            id=str(uuid.uuid4()),
                            base_currency=base_currency,
                            target_currency=target_currency,
                            rate=online_rates[target_currency],
                            source="online" if source == "online" else "fallback",
                            last_updated=datetime.now(timezone.utc),
                            company_id=company_id
                        )
                        
                        # Upsert rate (update if exists, insert if not)
                        await self.db.exchange_rates.update_one(
                            {
                                "base_currency": base_currency,
                                "target_currency": target_currency,
                                "company_id": company_id
                            },
                            {"$set": prepare_for_mongo(rate_data.dict())},
                            upsert=True
                        )
                        updated_count += 1
                
                return {
                    "success": True,
                    "updated_rates": updated_count,
                    "base_currency": base_currency,
                    "target_currencies": list(online_rates.keys()),
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            
            else:
                return {
                    "success": False,
                    "error": "Manual rate updates not implemented yet",
                    "failed_rates": target_currencies
                }
                
        except Exception as e:
            logger.error(f"Error updating company rates: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to update rates: {str(e)}",
                "updated_rates": 0,
                "failed_rates": target_currencies
            }
    
    async def _get_fallback_rates(self, base_currency: str, target_currencies: List[str]) -> Dict[str, float]:
        """Get fallback exchange rates when online APIs fail"""
        # Mock/fallback rates - in production, these could come from a backup source
        fallback_rates = {
            "INR": {
                "USD": 0.012,
                "EUR": 0.011,
                "GBP": 0.0095,
                "JPY": 1.85,
                "AUD": 0.018
            },
            "USD": {
                "INR": 83.25,
                "EUR": 0.92,
                "GBP": 0.79,
                "JPY": 154.30,
                "AUD": 1.52
            },
            "EUR": {
                "INR": 90.45,
                "USD": 1.09,
                "GBP": 0.86,
                "JPY": 167.85,
                "AUD": 1.65
            }
        }
        
        base_rates = fallback_rates.get(base_currency, {})
        result = {}
        for currency in target_currencies:
            if currency in base_rates:
                result[currency] = base_rates[currency]
        return result
    async def set_manual_rate(
        self, 
        company_id: str, 
        base_currency: str, 
        target_currency: str, 
        rate: float
    ) -> ExchangeRate:
        """
        Set a manual exchange rate for a company
        """
        rate_data = ExchangeRate(
            id=f"{company_id}_{base_currency}_{target_currency}",
            base_currency=base_currency,
            target_currency=target_currency,
            rate=rate,
            source="manual",
            last_updated=datetime.now(timezone.utc),
            company_id=company_id
        )
        
        # Upsert rate to database
        await self.db.exchange_rates.update_one(
            {
                "company_id": company_id,
                "base_currency": base_currency,
                "target_currency": target_currency
            },
            {"$set": rate_data.dict()},
            upsert=True
        )
        
        return rate_data
    
    async def get_company_rates(
        self, 
        company_id: str, 
        base_currency: Optional[str] = None
    ) -> List[ExchangeRate]:
        """
        Get all exchange rates for a company
        """
        filter_query = {"company_id": company_id, "is_active": True}
        
        if base_currency:
            filter_query["base_currency"] = base_currency
        
        rates = await self.db.exchange_rates.find(filter_query).to_list(length=None)
        
        return [ExchangeRate(**rate) for rate in rates]
    
    async def convert_amount(
        self, 
        amount: float, 
        from_currency: str, 
        to_currency: str, 
        company_id: str
    ) -> Dict[str, Any]:
        """
        Convert amount between currencies using company's exchange rates
        """
        if from_currency == to_currency:
            return {
                "original_amount": amount,
                "converted_amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": 1.0,
                "rate_source": "same_currency"
            }
        
        # Find exchange rate
        rate_doc = await self.db.exchange_rates.find_one({
            "company_id": company_id,
            "base_currency": from_currency,
            "target_currency": to_currency,
            "is_active": True
        })
        
        if rate_doc:
            rate = rate_doc["rate"]
            converted_amount = amount * rate
            
            return {
                "original_amount": amount,
                "converted_amount": converted_amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": rate,
                "rate_source": rate_doc["source"],
                "last_updated": rate_doc["last_updated"]
            }
        else:
            # Try reverse conversion
            reverse_rate_doc = await self.db.exchange_rates.find_one({
                "company_id": company_id,
                "base_currency": to_currency,
                "target_currency": from_currency,
                "is_active": True
            })
            
            if reverse_rate_doc:
                rate = 1.0 / reverse_rate_doc["rate"]
                converted_amount = amount * rate
                
                return {
                    "original_amount": amount,
                    "converted_amount": converted_amount,
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "exchange_rate": rate,
                    "rate_source": reverse_rate_doc["source"] + "_reversed",
                    "last_updated": reverse_rate_doc["last_updated"]
                }
            
            raise ValueError(f"No exchange rate found for {from_currency} to {to_currency}")
    
    async def schedule_rate_updates(self, company_id: str):
        """
        Schedule automatic rate updates for a company
        This would typically be called by a background task scheduler
        """
        try:
            # Get company setup to find base currency and additional currencies
            company_setup = await self.db.company_setups.find_one({"user_id": company_id})
            
            if not company_setup:
                return {"success": False, "error": "Company setup not found"}
            
            base_currency = company_setup.get("base_currency")
            additional_currencies = company_setup.get("additional_currencies", [])
            
            if not additional_currencies:
                return {"success": True, "message": "No additional currencies to update"}
            
            # Update rates
            result = await self.update_company_rates(
                company_id=company_id,
                base_currency=base_currency,
                target_currencies=additional_currencies,
                source="online"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in scheduled rate update: {e}")
            return {"success": False, "error": str(e)}

# Utility functions
async def get_currency_service(db) -> CurrencyService:
    """Get currency service instance"""
    return CurrencyService(db)

def format_currency_amount(amount: float, currency_code: str) -> str:
    """Format amount with currency symbol"""
    from .accounting_systems import get_currency_info
    
    currency_info = get_currency_info(currency_code)
    symbol = currency_info.get("symbol", currency_code)
    decimal_places = currency_info.get("decimal_places", 2)
    
    if decimal_places == 0:
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.{decimal_places}f}"