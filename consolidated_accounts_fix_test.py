#!/usr/bin/env python3
"""
CONSOLIDATED ACCOUNTS FIX TESTING SCRIPT
Tests the specific fix for consolidated accounts to include sister companies.

VERIFICATION NEEDED:
1. Test the fixed consolidated accounts endpoint
2. Verify it now returns accounts from ALL companies (main + sister companies)
3. Check that total_companies shows the correct count (should be 3: 1 main + 2 sister)
4. Verify consolidated data structure includes accounts from sister companies
5. Check that each account has proper company_name field showing which company it belongs to
6. Verify total_accounts reflects accounts from all companies (should be ~78 accounts: 26x3 companies)
"""

import requests
import json
import os
from datetime import datetime
import sys
import time
import random

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://zoios-erp-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials - create fresh account for testing
timestamp = str(int(time.time()))
TEST_EMAIL = f"consolidatedtest{timestamp}@example.com"
TEST_PASSWORD = "consolidatedtest123"

class ConsolidatedAccountsTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_login_with_group_company_account(self):
        """Login with existing Group Company account"""
        self.log("Testing login with Group Company account...")
        
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
                self.log("✅ Login successful with Group Company account")
                self.log(f"User ID: {self.user_data.get('id')}")
                self.log(f"Email: {self.user_data.get('email')}")
                return True
            else:
                self.log(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}")
            return False
    
    def test_get_companies_management(self):
        """Test GET /api/companies/management to verify company structure"""
        self.log("Testing GET /api/companies/management...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            self.log(f"Companies management response status: {response.status_code}")
            
            if response.status_code == 200:
                companies = response.json()
                self.log(f"✅ Found {len(companies)} companies")
                
                main_companies = [c for c in companies if c.get('is_main_company', False)]
                sister_companies = [c for c in companies if not c.get('is_main_company', True)]
                
                self.log(f"Main companies: {len(main_companies)}")
                self.log(f"Sister companies: {len(sister_companies)}")
                
                for company in companies:
                    self.log(f"  - {company.get('company_name')} (ID: {company.get('id')}) - Main: {company.get('is_main_company', False)}")
                
                if len(companies) >= 3:  # Should have at least 3 companies (1 main + 2 sisters)
                    self.log("✅ Company structure looks correct for consolidated testing")
                    return True, companies
                else:
                    self.log(f"⚠️ Expected at least 3 companies, found {len(companies)}")
                    return True, companies  # Still proceed with testing
            else:
                self.log(f"❌ Companies management failed: {response.text}")
                return False, []
                
        except Exception as e:
            self.log(f"❌ Companies management error: {str(e)}")
            return False, []
    
    def test_consolidated_accounts_enhanced_before_fix(self):
        """Test the consolidated accounts endpoint to see current behavior"""
        self.log("Testing GET /api/companies/consolidated-accounts/enhanced (current behavior)...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/consolidated-accounts/enhanced", headers=headers)
            self.log(f"Consolidated accounts enhanced response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Consolidated accounts enhanced endpoint working")
                
                # Extract key metrics
                total_companies = data.get('total_companies', 0)
                total_accounts = data.get('total_accounts', 0)
                consolidated_accounts = data.get('consolidated_accounts', [])
                companies = data.get('companies', [])
                
                self.log(f"📊 CONSOLIDATED ACCOUNTS METRICS:")
                self.log(f"  Total companies: {total_companies}")
                self.log(f"  Total accounts: {total_accounts}")
                self.log(f"  Consolidated accounts array length: {len(consolidated_accounts)}")
                self.log(f"  Companies array length: {len(companies)}")
                
                # Analyze company representation in consolidated accounts
                company_names_in_accounts = set()
                for account in consolidated_accounts:
                    company_name = account.get('company_name')
                    if company_name:
                        company_names_in_accounts.add(company_name)
                
                self.log(f"  Unique company names in accounts: {len(company_names_in_accounts)}")
                for company_name in company_names_in_accounts:
                    company_account_count = len([a for a in consolidated_accounts if a.get('company_name') == company_name])
                    self.log(f"    - {company_name}: {company_account_count} accounts")
                
                # Check if this matches expected results after fix
                expected_companies = 3  # 1 main + 2 sisters
                expected_accounts = 78  # 26 accounts × 3 companies
                
                self.log(f"\n🎯 EXPECTED AFTER FIX:")
                self.log(f"  Expected companies: {expected_companies}")
                self.log(f"  Expected accounts: ~{expected_accounts}")
                
                if total_companies >= expected_companies and total_accounts >= (expected_accounts * 0.8):  # Allow some variance
                    self.log("✅ CONSOLIDATED ACCOUNTS FIX APPEARS TO BE WORKING!")
                    self.log("✅ All companies are included in consolidated view")
                    return True
                else:
                    self.log("❌ CONSOLIDATED ACCOUNTS FIX NOT WORKING")
                    self.log(f"❌ Only showing {total_companies} companies instead of {expected_companies}")
                    self.log(f"❌ Only showing {total_accounts} accounts instead of ~{expected_accounts}")
                    return False
                    
            else:
                self.log(f"❌ Consolidated accounts enhanced failed: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Consolidated accounts enhanced error: {str(e)}")
            return False
    
    def test_individual_company_accounts(self, companies):
        """Test individual company chart of accounts to verify data exists"""
        self.log("Testing individual company chart of accounts...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        total_individual_accounts = 0
        
        for company in companies:
            company_id = company.get('id')
            company_name = company.get('company_name')
            is_main = company.get('is_main_company', False)
            
            self.log(f"Testing accounts for {company_name} ({'Main' if is_main else 'Sister'})...")
            
            try:
                response = self.session.get(f"{API_BASE}/company/{company_id}/chart-of-accounts", headers=headers)
                self.log(f"  Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    accounts_by_category = data.get('accounts_by_category', {})
                    total_accounts = data.get('total_accounts', 0)
                    
                    self.log(f"  ✅ {company_name}: {total_accounts} accounts")
                    total_individual_accounts += total_accounts
                    
                    # Show account categories
                    for category, accounts in accounts_by_category.items():
                        self.log(f"    - {category}: {len(accounts)} accounts")
                        
                else:
                    self.log(f"  ❌ {company_name}: Failed to get accounts - {response.text}")
                    
            except Exception as e:
                self.log(f"  ❌ {company_name}: Error - {str(e)}")
        
        self.log(f"\n📊 INDIVIDUAL ACCOUNTS SUMMARY:")
        self.log(f"  Total accounts across all companies: {total_individual_accounts}")
        
        return total_individual_accounts
    
    def test_consolidated_vs_individual_comparison(self, companies):
        """Compare consolidated accounts with sum of individual company accounts"""
        self.log("Comparing consolidated vs individual accounts...")
        
        # Get individual accounts total
        individual_total = self.test_individual_company_accounts(companies)
        
        # Get consolidated accounts
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/consolidated-accounts/enhanced", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                consolidated_total = data.get('total_accounts', 0)
                
                self.log(f"\n🔍 COMPARISON RESULTS:")
                self.log(f"  Individual accounts total: {individual_total}")
                self.log(f"  Consolidated accounts total: {consolidated_total}")
                
                if consolidated_total == individual_total:
                    self.log("✅ PERFECT MATCH - Consolidated accounts includes all company accounts")
                    return True
                elif consolidated_total > (individual_total * 0.9):  # Allow 10% variance
                    self.log("✅ CLOSE MATCH - Consolidated accounts includes most company accounts")
                    return True
                else:
                    self.log("❌ MISMATCH - Consolidated accounts missing company accounts")
                    self.log(f"❌ Missing {individual_total - consolidated_total} accounts")
                    return False
            else:
                self.log(f"❌ Could not get consolidated accounts for comparison")
                return False
                
        except Exception as e:
            self.log(f"❌ Comparison error: {str(e)}")
            return False
    
    def test_account_company_attribution(self):
        """Test that each account in consolidated view has proper company attribution"""
        self.log("Testing account company attribution in consolidated view...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/consolidated-accounts/enhanced", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                consolidated_accounts = data.get('consolidated_accounts', [])
                
                self.log(f"Testing company attribution for {len(consolidated_accounts)} accounts...")
                
                accounts_with_company_name = 0
                accounts_with_company_id = 0
                company_names = set()
                
                for account in consolidated_accounts:
                    if account.get('company_name'):
                        accounts_with_company_name += 1
                        company_names.add(account.get('company_name'))
                    
                    if account.get('company_id'):
                        accounts_with_company_id += 1
                
                self.log(f"📊 COMPANY ATTRIBUTION RESULTS:")
                self.log(f"  Accounts with company_name: {accounts_with_company_name}/{len(consolidated_accounts)}")
                self.log(f"  Accounts with company_id: {accounts_with_company_id}/{len(consolidated_accounts)}")
                self.log(f"  Unique company names: {len(company_names)}")
                
                for company_name in company_names:
                    count = len([a for a in consolidated_accounts if a.get('company_name') == company_name])
                    self.log(f"    - {company_name}: {count} accounts")
                
                if accounts_with_company_name == len(consolidated_accounts) and len(company_names) >= 3:
                    self.log("✅ All accounts have proper company attribution")
                    self.log("✅ Multiple companies represented in consolidated view")
                    return True
                else:
                    self.log("❌ Some accounts missing company attribution")
                    return False
                    
            else:
                self.log(f"❌ Could not get consolidated accounts for attribution test")
                return False
                
        except Exception as e:
            self.log(f"❌ Attribution test error: {str(e)}")
            return False
    
    def test_consolidated_accounts_data_structure(self):
        """Test the data structure of consolidated accounts response"""
        self.log("Testing consolidated accounts data structure...")
        
        if not self.auth_token:
            self.log("❌ No auth token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/companies/consolidated-accounts/enhanced", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                self.log("📋 CONSOLIDATED ACCOUNTS DATA STRUCTURE:")
                
                # Check required top-level fields
                required_fields = ['companies', 'consolidated_accounts', 'total_companies', 'total_accounts', 'summary']
                missing_fields = []
                
                for field in required_fields:
                    if field in data:
                        self.log(f"  ✅ {field}: {type(data[field]).__name__}")
                        if field == 'companies':
                            self.log(f"      Length: {len(data[field])}")
                        elif field == 'consolidated_accounts':
                            self.log(f"      Length: {len(data[field])}")
                        elif field in ['total_companies', 'total_accounts']:
                            self.log(f"      Value: {data[field]}")
                    else:
                        missing_fields.append(field)
                        self.log(f"  ❌ {field}: MISSING")
                
                # Check sample account structure
                consolidated_accounts = data.get('consolidated_accounts', [])
                if consolidated_accounts:
                    sample_account = consolidated_accounts[0]
                    self.log(f"\n📋 SAMPLE ACCOUNT STRUCTURE:")
                    account_fields = ['account_code', 'account_name', 'company_name', 'company_id', 'account_type', 'category']
                    
                    for field in account_fields:
                        if field in sample_account:
                            self.log(f"  ✅ {field}: {sample_account[field]}")
                        else:
                            self.log(f"  ❌ {field}: MISSING")
                
                # Check summary structure
                summary = data.get('summary', {})
                if summary:
                    self.log(f"\n📋 SUMMARY STRUCTURE:")
                    summary_fields = ['assets', 'liabilities', 'equity', 'revenue', 'expense']
                    for field in summary_fields:
                        if field in summary:
                            self.log(f"  ✅ {field}: {summary[field]}")
                        else:
                            self.log(f"  ❌ {field}: MISSING")
                
                if not missing_fields and consolidated_accounts:
                    self.log("✅ Data structure is complete and correct")
                    return True
                else:
                    self.log(f"❌ Data structure issues: {missing_fields}")
                    return False
                    
            else:
                self.log(f"❌ Could not get consolidated accounts for structure test")
                return False
                
        except Exception as e:
            self.log(f"❌ Data structure test error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all consolidated accounts fix tests"""
        self.log("🚀 STARTING COMPREHENSIVE CONSOLIDATED ACCOUNTS FIX TESTING")
        self.log("=" * 80)
        
        test_results = {}
        
        # Test 1: Login with Group Company account
        self.log("\n1️⃣ TESTING LOGIN WITH GROUP COMPANY ACCOUNT")
        test_results['login'] = self.test_login_with_group_company_account()
        
        if not test_results['login']:
            self.log("❌ Cannot proceed without successful login")
            return test_results
        
        # Test 2: Get companies management to verify structure
        self.log("\n2️⃣ TESTING COMPANY STRUCTURE")
        companies_result, companies = self.test_get_companies_management()
        test_results['company_structure'] = companies_result
        
        # Test 3: Test consolidated accounts enhanced endpoint
        self.log("\n3️⃣ TESTING CONSOLIDATED ACCOUNTS ENHANCED ENDPOINT")
        test_results['consolidated_accounts'] = self.test_consolidated_accounts_enhanced_before_fix()
        
        # Test 4: Test individual company accounts
        self.log("\n4️⃣ TESTING INDIVIDUAL COMPANY ACCOUNTS")
        if companies:
            test_results['individual_accounts'] = self.test_individual_company_accounts(companies) > 0
        else:
            test_results['individual_accounts'] = False
        
        # Test 5: Compare consolidated vs individual
        self.log("\n5️⃣ COMPARING CONSOLIDATED VS INDIVIDUAL ACCOUNTS")
        if companies:
            test_results['comparison'] = self.test_consolidated_vs_individual_comparison(companies)
        else:
            test_results['comparison'] = False
        
        # Test 6: Test account company attribution
        self.log("\n6️⃣ TESTING ACCOUNT COMPANY ATTRIBUTION")
        test_results['attribution'] = self.test_account_company_attribution()
        
        # Test 7: Test data structure
        self.log("\n7️⃣ TESTING DATA STRUCTURE")
        test_results['data_structure'] = self.test_consolidated_accounts_data_structure()
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log("🎯 CONSOLIDATED ACCOUNTS FIX TEST SUMMARY")
        self.log("=" * 80)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status} {test_name.replace('_', ' ').title()}")
        
        self.log(f"\n📊 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if test_results.get('consolidated_accounts') and test_results.get('attribution'):
            self.log("🎉 CONSOLIDATED ACCOUNTS FIX IS WORKING!")
            self.log("✅ Sister companies are now included in consolidated view")
            self.log("✅ All companies show proper account attribution")
        else:
            self.log("❌ CONSOLIDATED ACCOUNTS FIX NEEDS ATTENTION")
            self.log("❌ Sister companies may not be properly included")
        
        return test_results

def main():
    """Main test execution"""
    tester = ConsolidatedAccountsTester()
    results = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()