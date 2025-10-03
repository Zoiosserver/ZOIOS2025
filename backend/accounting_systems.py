"""
Accounting systems and chart of accounts templates for different countries
"""

from typing import Dict, List, Any

# Accounting systems by country
ACCOUNTING_SYSTEMS = {
    "US": {
        "name": "US GAAP",
        "description": "Generally Accepted Accounting Principles (United States)",
        "currency": "USD",
        "fiscal_year_start": "01-01",
        "tax_system": "Federal and State",
        "chart_of_accounts": "us_gaap"
    },
    "GB": {
        "name": "UK GAAP / IFRS",
        "description": "UK Generally Accepted Accounting Practice / International Financial Reporting Standards",
        "currency": "GBP", 
        "fiscal_year_start": "04-06",
        "tax_system": "HMRC",
        "chart_of_accounts": "uk_gaap"
    },
    "DE": {
        "name": "German GAAP (HGB)",
        "description": "Handelsgesetzbuch - German Commercial Code",
        "currency": "EUR",
        "fiscal_year_start": "01-01",
        "tax_system": "German Tax Code",
        "chart_of_accounts": "german_hgb"
    },
    "FR": {
        "name": "French GAAP (PCG)",
        "description": "Plan Comptable Général - French Accounting Plan",
        "currency": "EUR",
        "fiscal_year_start": "01-01", 
        "tax_system": "French Tax Code",
        "chart_of_accounts": "french_pcg"
    },
    "IN": {
        "name": "Indian GAAP / Ind AS",
        "description": "Indian Accounting Standards",
        "currency": "INR",
        "fiscal_year_start": "04-01",
        "tax_system": "GST / Income Tax",
        "chart_of_accounts": "indian_gaap"
    },
    "CA": {
        "name": "Canadian GAAP / IFRS",
        "description": "Canadian Generally Accepted Accounting Principles / IFRS",
        "currency": "CAD",
        "fiscal_year_start": "01-01",
        "tax_system": "CRA",
        "chart_of_accounts": "canadian_gaap"
    },
    "AU": {
        "name": "Australian GAAP / AASB",
        "description": "Australian Accounting Standards Board Standards",
        "currency": "AUD",
        "fiscal_year_start": "07-01",
        "tax_system": "ATO",
        "chart_of_accounts": "australian_aasb"
    },
    "JP": {
        "name": "Japanese GAAP (J-GAAP)",
        "description": "Japanese Generally Accepted Accounting Principles",
        "currency": "JPY",
        "fiscal_year_start": "04-01",
        "tax_system": "Japanese Tax Code",
        "chart_of_accounts": "japanese_gaap"
    },
    "SG": {
        "name": "Singapore FRS / IFRS",
        "description": "Singapore Financial Reporting Standards",
        "currency": "SGD",
        "fiscal_year_start": "01-01",
        "tax_system": "IRAS",
        "chart_of_accounts": "singapore_frs"
    },
    "AE": {
        "name": "UAE GAAP / IFRS", 
        "description": "UAE Generally Accepted Accounting Principles / IFRS",
        "currency": "AED",
        "fiscal_year_start": "01-01",
        "tax_system": "UAE Tax Authority",
        "chart_of_accounts": "uae_gaap"
    }
}

# Chart of Accounts Templates
CHART_OF_ACCOUNTS_TEMPLATES = {
    "us_gaap": {
        "assets": [
            {"code": "1000", "name": "Cash and Cash Equivalents", "type": "asset", "category": "current_asset"},
            {"code": "1100", "name": "Accounts Receivable", "type": "asset", "category": "current_asset"},
            {"code": "1200", "name": "Inventory", "type": "asset", "category": "current_asset"},
            {"code": "1300", "name": "Prepaid Expenses", "type": "asset", "category": "current_asset"},
            {"code": "1500", "name": "Property, Plant & Equipment", "type": "asset", "category": "fixed_asset"},
            {"code": "1600", "name": "Accumulated Depreciation", "type": "asset", "category": "fixed_asset"},
            {"code": "1700", "name": "Intangible Assets", "type": "asset", "category": "fixed_asset"},
        ],
        "liabilities": [
            {"code": "2000", "name": "Accounts Payable", "type": "liability", "category": "current_liability"},
            {"code": "2100", "name": "Accrued Expenses", "type": "liability", "category": "current_liability"},
            {"code": "2200", "name": "Short-term Debt", "type": "liability", "category": "current_liability"},
            {"code": "2300", "name": "Payroll Liabilities", "type": "liability", "category": "current_liability"},
            {"code": "2500", "name": "Long-term Debt", "type": "liability", "category": "long_term_liability"},
            {"code": "2600", "name": "Deferred Tax Liability", "type": "liability", "category": "long_term_liability"},
        ],
        "equity": [
            {"code": "3000", "name": "Common Stock", "type": "equity", "category": "equity"},
            {"code": "3100", "name": "Retained Earnings", "type": "equity", "category": "equity"},
            {"code": "3200", "name": "Additional Paid-in Capital", "type": "equity", "category": "equity"},
        ],
        "revenue": [
            {"code": "4000", "name": "Sales Revenue", "type": "revenue", "category": "operating_revenue"},
            {"code": "4100", "name": "Service Revenue", "type": "revenue", "category": "operating_revenue"},
            {"code": "4900", "name": "Other Revenue", "type": "revenue", "category": "non_operating_revenue"},
        ],
        "expenses": [
            {"code": "5000", "name": "Cost of Goods Sold", "type": "expense", "category": "cost_of_sales"},
            {"code": "6000", "name": "Salaries and Wages", "type": "expense", "category": "operating_expense"},
            {"code": "6100", "name": "Rent Expense", "type": "expense", "category": "operating_expense"},
            {"code": "6200", "name": "Utilities Expense", "type": "expense", "category": "operating_expense"},
            {"code": "6300", "name": "Marketing Expense", "type": "expense", "category": "operating_expense"},
            {"code": "6400", "name": "Depreciation Expense", "type": "expense", "category": "operating_expense"},
            {"code": "7000", "name": "Interest Expense", "type": "expense", "category": "financial_expense"},
        ]
    },
    "uk_gaap": {
        "assets": [
            {"code": "1000", "name": "Cash at Bank and in Hand", "type": "asset", "category": "current_asset"},
            {"code": "1100", "name": "Trade Debtors", "type": "asset", "category": "current_asset"},
            {"code": "1200", "name": "Stock", "type": "asset", "category": "current_asset"},
            {"code": "1300", "name": "Prepayments", "type": "asset", "category": "current_asset"},
            {"code": "1500", "name": "Tangible Fixed Assets", "type": "asset", "category": "fixed_asset"},
            {"code": "1600", "name": "Accumulated Depreciation", "type": "asset", "category": "fixed_asset"},
            {"code": "1700", "name": "Intangible Assets", "type": "asset", "category": "fixed_asset"},
        ],
        "liabilities": [
            {"code": "2000", "name": "Trade Creditors", "type": "liability", "category": "current_liability"},
            {"code": "2100", "name": "Accruals", "type": "liability", "category": "current_liability"},
            {"code": "2200", "name": "Bank Overdraft", "type": "liability", "category": "current_liability"},
            {"code": "2300", "name": "PAYE/NI Payable", "type": "liability", "category": "current_liability"},
            {"code": "2400", "name": "VAT Payable", "type": "liability", "category": "current_liability"},
            {"code": "2500", "name": "Long Term Loans", "type": "liability", "category": "long_term_liability"},
        ],
        "equity": [
            {"code": "3000", "name": "Share Capital", "type": "equity", "category": "equity"},
            {"code": "3100", "name": "Retained Profits", "type": "equity", "category": "equity"},
            {"code": "3200", "name": "Share Premium", "type": "equity", "category": "equity"},
        ],
        "revenue": [
            {"code": "4000", "name": "Sales", "type": "revenue", "category": "operating_revenue"},
            {"code": "4100", "name": "Other Operating Income", "type": "revenue", "category": "operating_revenue"},
            {"code": "4900", "name": "Investment Income", "type": "revenue", "category": "non_operating_revenue"},
        ],
        "expenses": [
            {"code": "5000", "name": "Cost of Sales", "type": "expense", "category": "cost_of_sales"},
            {"code": "6000", "name": "Wages and Salaries", "type": "expense", "category": "operating_expense"},
            {"code": "6100", "name": "Rent and Rates", "type": "expense", "category": "operating_expense"},
            {"code": "6200", "name": "Light and Heat", "type": "expense", "category": "operating_expense"},
            {"code": "6300", "name": "Advertising", "type": "expense", "category": "operating_expense"},
            {"code": "6400", "name": "Depreciation", "type": "expense", "category": "operating_expense"},
            {"code": "7000", "name": "Interest Payable", "type": "expense", "category": "financial_expense"},
        ]
    },
    "indian_gaap": {
        "assets": [
            {"code": "1000", "name": "Cash and Bank", "type": "asset", "category": "current_asset"},
            {"code": "1100", "name": "Sundry Debtors", "type": "asset", "category": "current_asset"},
            {"code": "1200", "name": "Stock/Inventory", "type": "asset", "category": "current_asset"},
            {"code": "1300", "name": "Advances and Prepayments", "type": "asset", "category": "current_asset"},
            {"code": "1500", "name": "Fixed Assets", "type": "asset", "category": "fixed_asset"},
            {"code": "1600", "name": "Accumulated Depreciation", "type": "asset", "category": "fixed_asset"},
        ],
        "liabilities": [
            {"code": "2000", "name": "Sundry Creditors", "type": "liability", "category": "current_liability"},
            {"code": "2100", "name": "Outstanding Expenses", "type": "liability", "category": "current_liability"},
            {"code": "2200", "name": "Bank Overdraft", "type": "liability", "category": "current_liability"},
            {"code": "2300", "name": "TDS Payable", "type": "liability", "category": "current_liability"},
            {"code": "2400", "name": "GST Payable", "type": "liability", "category": "current_liability"},
            {"code": "2500", "name": "Long Term Loans", "type": "liability", "category": "long_term_liability"},
        ],
        "equity": [
            {"code": "3000", "name": "Capital", "type": "equity", "category": "equity"},
            {"code": "3100", "name": "Reserves and Surplus", "type": "equity", "category": "equity"},
        ],
        "revenue": [
            {"code": "4000", "name": "Sales/Revenue", "type": "revenue", "category": "operating_revenue"},
            {"code": "4100", "name": "Other Income", "type": "revenue", "category": "operating_revenue"},
        ],
        "expenses": [
            {"code": "5000", "name": "Cost of Goods Sold", "type": "expense", "category": "cost_of_sales"},
            {"code": "6000", "name": "Salary and Wages", "type": "expense", "category": "operating_expense"},
            {"code": "6100", "name": "Rent", "type": "expense", "category": "operating_expense"},
            {"code": "6200", "name": "Electricity", "type": "expense", "category": "operating_expense"},
            {"code": "6300", "name": "Advertisement", "type": "expense", "category": "operating_expense"},
            {"code": "6400", "name": "Depreciation", "type": "expense", "category": "operating_expense"},
            {"code": "7000", "name": "Interest on Loans", "type": "expense", "category": "financial_expense"},
        ]
    }
}

# Currencies with their details
CURRENCIES = {
    "USD": {"name": "US Dollar", "symbol": "$", "decimal_places": 2},
    "EUR": {"name": "Euro", "symbol": "€", "decimal_places": 2},
    "GBP": {"name": "British Pound", "symbol": "£", "decimal_places": 2},
    "JPY": {"name": "Japanese Yen", "symbol": "¥", "decimal_places": 0},
    "CNY": {"name": "Chinese Yuan", "symbol": "¥", "decimal_places": 2},
    "INR": {"name": "Indian Rupee", "symbol": "₹", "decimal_places": 2},
    "AUD": {"name": "Australian Dollar", "symbol": "A$", "decimal_places": 2},
    "CAD": {"name": "Canadian Dollar", "symbol": "C$", "decimal_places": 2},
    "CHF": {"name": "Swiss Franc", "symbol": "Fr", "decimal_places": 2},
    "SEK": {"name": "Swedish Krona", "symbol": "kr", "decimal_places": 2},
    "NOK": {"name": "Norwegian Krone", "symbol": "kr", "decimal_places": 2},
    "DKK": {"name": "Danish Krone", "symbol": "kr", "decimal_places": 2},
    "SGD": {"name": "Singapore Dollar", "symbol": "S$", "decimal_places": 2},
    "HKD": {"name": "Hong Kong Dollar", "symbol": "HK$", "decimal_places": 2},
    "AED": {"name": "UAE Dirham", "symbol": "د.إ", "decimal_places": 2},
    "SAR": {"name": "Saudi Riyal", "symbol": "﷼", "decimal_places": 2},
    "ZAR": {"name": "South African Rand", "symbol": "R", "decimal_places": 2},
    "BRL": {"name": "Brazilian Real", "symbol": "R$", "decimal_places": 2},
    "MXN": {"name": "Mexican Peso", "symbol": "$", "decimal_places": 2},
    "RUB": {"name": "Russian Ruble", "symbol": "₽", "decimal_places": 2},
    "KRW": {"name": "South Korean Won", "symbol": "₩", "decimal_places": 0},
    "THB": {"name": "Thai Baht", "symbol": "฿", "decimal_places": 2},
    "MYR": {"name": "Malaysian Ringgit", "symbol": "RM", "decimal_places": 2},
    "PHP": {"name": "Philippine Peso", "symbol": "₱", "decimal_places": 2},
    "IDR": {"name": "Indonesian Rupiah", "symbol": "Rp", "decimal_places": 0},
    "VND": {"name": "Vietnamese Dong", "symbol": "₫", "decimal_places": 0},
}

# Countries with their details
COUNTRIES = {
    "US": {"name": "United States", "code": "US", "phone_code": "+1"},
    "GB": {"name": "United Kingdom", "code": "GB", "phone_code": "+44"},
    "DE": {"name": "Germany", "code": "DE", "phone_code": "+49"},
    "FR": {"name": "France", "code": "FR", "phone_code": "+33"},
    "IN": {"name": "India", "code": "IN", "phone_code": "+91"},
    "CA": {"name": "Canada", "code": "CA", "phone_code": "+1"},
    "AU": {"name": "Australia", "code": "AU", "phone_code": "+61"},
    "JP": {"name": "Japan", "code": "JP", "phone_code": "+81"},
    "SG": {"name": "Singapore", "code": "SG", "phone_code": "+65"},
    "AE": {"name": "United Arab Emirates", "code": "AE", "phone_code": "+971"},
    "CN": {"name": "China", "code": "CN", "phone_code": "+86"},
    "BR": {"name": "Brazil", "code": "BR", "phone_code": "+55"},
    "MX": {"name": "Mexico", "code": "MX", "phone_code": "+52"},
    "RU": {"name": "Russia", "code": "RU", "phone_code": "+7"},
    "KR": {"name": "South Korea", "code": "KR", "phone_code": "+82"},
    "IT": {"name": "Italy", "code": "IT", "phone_code": "+39"},
    "ES": {"name": "Spain", "code": "ES", "phone_code": "+34"},
    "NL": {"name": "Netherlands", "code": "NL", "phone_code": "+31"},
    "CH": {"name": "Switzerland", "code": "CH", "phone_code": "+41"},
    "SE": {"name": "Sweden", "code": "SE", "phone_code": "+46"},
    "NO": {"name": "Norway", "code": "NO", "phone_code": "+47"},
    "DK": {"name": "Denmark", "code": "DK", "phone_code": "+45"},
    "FI": {"name": "Finland", "code": "FI", "phone_code": "+358"},
    "BE": {"name": "Belgium", "code": "BE", "phone_code": "+32"},
    "AT": {"name": "Austria", "code": "AT", "phone_code": "+43"},
    "PL": {"name": "Poland", "code": "PL", "phone_code": "+48"},
    "CZ": {"name": "Czech Republic", "code": "CZ", "phone_code": "+420"},
    "HU": {"name": "Hungary", "code": "HU", "phone_code": "+36"},
    "TH": {"name": "Thailand", "code": "TH", "phone_code": "+66"},
    "MY": {"name": "Malaysia", "code": "MY", "phone_code": "+60"},
    "PH": {"name": "Philippines", "code": "PH", "phone_code": "+63"},
    "ID": {"name": "Indonesia", "code": "ID", "phone_code": "+62"},
    "VN": {"name": "Vietnam", "code": "VN", "phone_code": "+84"},
    "ZA": {"name": "South Africa", "code": "ZA", "phone_code": "+27"},
    "EG": {"name": "Egypt", "code": "EG", "phone_code": "+20"},
    "SA": {"name": "Saudi Arabia", "code": "SA", "phone_code": "+966"},
}

def get_accounting_system(country_code: str) -> Dict[str, Any]:
    """Get accounting system for a country"""
    return ACCOUNTING_SYSTEMS.get(country_code, ACCOUNTING_SYSTEMS["US"])

def get_chart_of_accounts(accounting_system: str) -> Dict[str, List[Dict]]:
    """Get chart of accounts for an accounting system"""
    return CHART_OF_ACCOUNTS_TEMPLATES.get(accounting_system, CHART_OF_ACCOUNTS_TEMPLATES["us_gaap"])

def get_currency_info(currency_code: str) -> Dict[str, Any]:
    """Get currency information"""
    return CURRENCIES.get(currency_code, CURRENCIES["USD"])

def get_country_info(country_code: str) -> Dict[str, Any]:
    """Get country information"""
    return COUNTRIES.get(country_code, COUNTRIES["US"])

def get_available_countries() -> List[Dict[str, Any]]:
    """Get list of available countries"""
    return [
        {
            "code": code,
            "name": details["name"],
            "phone_code": details["phone_code"],
            "accounting_system": ACCOUNTING_SYSTEMS.get(code, {}).get("name", "International GAAP"),
            "currency": ACCOUNTING_SYSTEMS.get(code, {}).get("currency", "USD")
        }
        for code, details in COUNTRIES.items()
    ]

def get_available_currencies() -> List[Dict[str, Any]]:
    """Get list of available currencies"""
    return [
        {
            "code": code,
            "name": details["name"],
            "symbol": details["symbol"],
            "decimal_places": details["decimal_places"]
        }
        for code, details in CURRENCIES.items()
    ]