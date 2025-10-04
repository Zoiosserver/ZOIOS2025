#!/usr/bin/env python3
"""
Final verification of the three critical fixes requested in the review
"""

import requests
import json
import os
from datetime import datetime
import sys
import time
import random

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://zoios-erp-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Use existing test user credentials
TEST_EMAIL = "criticaltest17595734584867@example.com"
TEST_PASSWORD = "testpass123"

class FinalCriticalTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.company_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def login(self):
        """Login with existing test user"""
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.log("✅ Logged in successfully")
                return True
            else:
                self.log(f"❌ Login failed: {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}")
            return False
    
    def get_company_id(self):
        """Get company ID from setup"""
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/setup/company", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.company_id = data.get('id')
                return True
            return False
        except:
            return False
    
    def test_all_fixes(self):
        """Test all three critical fixes"""
        if not self.login():
            return False
            
        if not self.get_company_id():
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        results = {}
        
        # Test 1: Sister Company Display Fix
        self.log("🔍 Testing Sister Company Display Fix...")
        try:
            response = self.session.get(f"{API_BASE}/companies/management", headers=headers)
            if response.status_code == 200:
                companies = response.json()
                main_companies = [c for c in companies if c.get('is_main_company') == True]
                sister_companies = [c for c in companies if c.get('is_main_company') == False]
                
                if main_companies and sister_companies:
                    sister = sister_companies[0]
                    if (sister.get('is_main_company') == False and 
                        sister.get('parent_company_id') is not None):
                        self.log("✅ Sister Company Display Fix - WORKING")
                        results['sister_display'] = True
                    else:
                        self.log("❌ Sister Company Display Fix - FAILED")
                        results['sister_display'] = False
                else:
                    self.log("❌ Sister Company Display Fix - No companies found")
                    results['sister_display'] = False
            else:
                self.log("❌ Sister Company Display Fix - API Error")
                results['sister_display'] = False
        except Exception as e:
            self.log(f"❌ Sister Company Display Fix - Error: {e}")
            results['sister_display'] = False
        
        # Test 2: Chart of Accounts Field Mapping Fix
        self.log("🔍 Testing Chart of Accounts Field Mapping Fix...")
        try:
            response = self.session.get(f"{API_BASE}/companies/{self.company_id}/accounts/enhanced", headers=headers)
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('accounts', [])
                
                if accounts:
                    account = accounts[0]
                    account_code = account.get('account_code')
                    account_name = account.get('account_name')
                    
                    if account_code and account_name and account_code != 'N/A' and account_name != 'N/A':
                        self.log("✅ Chart of Accounts Field Mapping Fix - WORKING")
                        results['chart_mapping'] = True
                    else:
                        self.log("❌ Chart of Accounts Field Mapping Fix - Field mapping issues")
                        results['chart_mapping'] = False
                else:
                    self.log("❌ Chart of Accounts Field Mapping Fix - No accounts")
                    results['chart_mapping'] = False
            else:
                self.log("❌ Chart of Accounts Field Mapping Fix - API Error")
                results['chart_mapping'] = False
        except Exception as e:
            self.log(f"❌ Chart of Accounts Field Mapping Fix - Error: {e}")
            results['chart_mapping'] = False
        
        # Test 3: Consolidated Accounts Field Mapping Fix
        self.log("🔍 Testing Consolidated Accounts Field Mapping Fix...")
        try:
            response = self.session.get(f"{API_BASE}/companies/consolidated-accounts/enhanced", headers=headers)
            if response.status_code == 200:
                data = response.json()
                consolidated_accounts = data.get('consolidated_accounts', [])
                
                if consolidated_accounts:
                    account = consolidated_accounts[0]
                    account_code = account.get('account_code')
                    account_name = account.get('account_name')
                    
                    if account_code and account_name and account_code != 'N/A' and account_name != 'N/A':
                        self.log("✅ Consolidated Accounts Field Mapping Fix - WORKING")
                        results['consolidated_mapping'] = True
                    else:
                        self.log("❌ Consolidated Accounts Field Mapping Fix - Field mapping issues")
                        results['consolidated_mapping'] = False
                else:
                    self.log("❌ Consolidated Accounts Field Mapping Fix - No accounts")
                    results['consolidated_mapping'] = False
            else:
                self.log("❌ Consolidated Accounts Field Mapping Fix - API Error")
                results['consolidated_mapping'] = False
        except Exception as e:
            self.log(f"❌ Consolidated Accounts Field Mapping Fix - Error: {e}")
            results['consolidated_mapping'] = False
        
        # Summary
        self.log("=" * 60)
        self.log("🏁 FINAL TEST RESULTS")
        self.log("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"{test_name}: {status}")
        
        self.log("=" * 60)
        self.log(f"OVERALL: {passed}/{total} critical fixes working correctly")
        
        if passed == total:
            self.log("🎉 ALL THREE CRITICAL FIXES ARE WORKING PERFECTLY!")
            return True
        else:
            self.log("❌ Some critical fixes need attention")
            return False

def main():
    tester = FinalCriticalTester()
    success = tester.test_all_fixes()
    
    if success:
        print("\n✅ All critical fixes verified!")
        sys.exit(0)
    else:
        print("\n❌ Some critical fixes failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()