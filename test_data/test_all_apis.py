#!/usr/bin/env python3
"""
Comprehensive API testing script for CreditSphere
Tests all endpoints and validates responses
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPass123!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} {name}")
    if details:
        print(f"     {details}")

def test_health():
    """Test health check endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/health")
        passed = r.status_code == 200 and r.json().get("status") == "healthy"
        log_test("GET /health", passed, f"Status: {r.json()}")
        return passed
    except Exception as e:
        log_test("GET /health", False, str(e))
        return False

def test_root():
    """Test root endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/")
        passed = r.status_code == 200
        log_test("GET /", passed, f"Response: {r.json()}")
        return passed
    except Exception as e:
        log_test("GET /", False, str(e))
        return False

def test_auth_flow():
    """Test complete authentication flow"""
    results = {}
    
    # 1. Register
    try:
        r = requests.post(f"{BASE_URL}/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "locale": "en"
        })
        passed = r.status_code == 201
        user_data = r.json() if passed else {}
        log_test("POST /auth/register", passed, f"User ID: {user_data.get('id')}")
        results['register'] = passed
    except Exception as e:
        log_test("POST /auth/register", False, str(e))
        results['register'] = False
        return results
    
    # 2. Login
    try:
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        passed = r.status_code == 200 and 'access_token' in r.json()
        tokens = r.json() if passed else {}
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        log_test("POST /auth/login", passed, f"Token received: {access_token[:20]}...")
        results['login'] = passed
        results['access_token'] = access_token
        results['refresh_token'] = refresh_token
    except Exception as e:
        log_test("POST /auth/login", False, str(e))
        results['login'] = False
        return results
    
    # 3. Get Me
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        passed = r.status_code == 200 and r.json().get('email') == TEST_EMAIL
        log_test("GET /auth/me", passed, f"Email: {r.json().get('email')}")
        results['me'] = passed
    except Exception as e:
        log_test("GET /auth/me", False, str(e))
        results['me'] = False
    
    # 4. Refresh token
    try:
        r = requests.post(f"{BASE_URL}/auth/refresh", json={
            "refresh_token": refresh_token
        })
        passed = r.status_code == 200 and 'access_token' in r.json()
        log_test("POST /auth/refresh", passed)
        results['refresh'] = passed
    except Exception as e:
        log_test("POST /auth/refresh", False, str(e))
        results['refresh'] = False
    
    # 5. Logout
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        r = requests.post(f"{BASE_URL}/auth/logout", headers=headers, json={
            "refresh_token": refresh_token
        })
        passed = r.status_code == 200
        log_test("POST /auth/logout", passed)
        results['logout'] = passed
    except Exception as e:
        log_test("POST /auth/logout", False, str(e))
        results['logout'] = False
    
    return results

def test_quota_endpoints(access_token):
    """Test quota endpoints"""
    headers = {"Authorization": f"Bearer {access_token}"}
    results = {}
    
    # Get quota status
    try:
        r = requests.get(f"{BASE_URL}/quota/status", headers=headers)
        passed = r.status_code == 200
        data = r.json() if passed else {}
        log_test("GET /quota/status", passed, 
                f"AI calls: {data.get('ai_calls_used')}/{data.get('ai_calls_limit')}")
        results['status'] = passed
    except Exception as e:
        log_test("GET /quota/status", False, str(e))
        results['status'] = False
    
    # Reset quota
    try:
        r = requests.post(f"{BASE_URL}/quota/reset", headers=headers)
        passed = r.status_code == 200
        log_test("POST /quota/reset", passed)
        results['reset'] = passed
    except Exception as e:
        log_test("POST /quota/reset", False, str(e))
        results['reset'] = False
    
    return results

def test_file_upload(access_token):
    """Test file upload with MBNA.PDF"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Upload MBNA.PDF
    try:
        file_path = "C:\\Users\\whyke\\financial-advisor\\bankstatement\\MBNA.PDF"
        with open(file_path, 'rb') as f:
            files = {'file': ('MBNA.PDF', f, 'application/pdf')}
            r = requests.post(f"{BASE_URL}/files/upload", headers=headers, files=files)
        
        passed = r.status_code == 200
        data = r.json() if passed else {}
        statement_id = data.get('statement_id')
        
        log_test("POST /files/upload", passed, 
                f"Statement ID: {statement_id}, Transactions: {data.get('message')}")
        
        return statement_id if passed else None
    except Exception as e:
        log_test("POST /files/upload", False, str(e))
        return None

def test_statement_endpoints(access_token, statement_id):
    """Test statement management endpoints"""
    headers = {"Authorization": f"Bearer {access_token}"}
    results = {}
    
    # List statements
    try:
        r = requests.get(f"{BASE_URL}/files/statements", headers=headers)
        passed = r.status_code == 200
        data = r.json() if passed else {}
        log_test("GET /files/statements", passed, 
                f"Total: {data.get('total')}, Institution: {data.get('statements', [{}])[0].get('institution')}")
        results['list'] = passed
    except Exception as e:
        log_test("GET /files/statements", False, str(e))
        results['list'] = False
    
    # Get statement status
    try:
        r = requests.get(f"{BASE_URL}/files/statements/{statement_id}", headers=headers)
        passed = r.status_code == 200
        data = r.json() if passed else {}
        log_test(f"GET /files/statements/{statement_id}", passed, 
                f"Parsed: {data.get('parsed')}, Transactions: {data.get('transaction_count')}")
        results['status'] = passed
    except Exception as e:
        log_test(f"GET /files/statements/{statement_id}", False, str(e))
        results['status'] = False
    
    # Reparse statement
    try:
        r = requests.post(f"{BASE_URL}/files/statements/{statement_id}/reparse", headers=headers)
        passed = r.status_code == 200
        log_test(f"POST /files/statements/{statement_id}/reparse", passed)
        results['reparse'] = passed
    except Exception as e:
        log_test(f"POST /files/statements/{statement_id}/reparse", False, str(e))
        results['reparse'] = False
    
    # Delete statement (commented out to preserve data)
    # try:
    #     r = requests.delete(f"{BASE_URL}/files/statements/{statement_id}", headers=headers)
    #     passed = r.status_code == 200
    #     log_test(f"DELETE /files/statements/{statement_id}", passed)
    #     results['delete'] = passed
    # except Exception as e:
    #     log_test(f"DELETE /files/statements/{statement_id}", False, str(e))
    #     results['delete'] = False
    
    return results

def test_transaction_endpoints(access_token):
    """Test transaction endpoints"""
    headers = {"Authorization": f"Bearer {access_token}"}
    results = {}
    
    # List transactions
    try:
        r = requests.get(f"{BASE_URL}/transactions", headers=headers, params={'page_size': 5})
        passed = r.status_code == 200
        data = r.json() if passed else {}
        log_test("GET /transactions", passed, f"Total: {data.get('total')}")
        results['list'] = passed
        
        # Get first transaction ID for recategorize test
        txn_id = data.get('transactions', [{}])[0].get('id') if data.get('transactions') else None
        results['transaction_id'] = txn_id
    except Exception as e:
        log_test("GET /transactions", False, str(e))
        results['list'] = False
    
    # Category breakdown
    try:
        r = requests.get(f"{BASE_URL}/transactions/breakdown", headers=headers)
        passed = r.status_code == 200
        data = r.json() if passed else []
        log_test("GET /transactions/breakdown", passed, 
                f"Categories: {len(data)}")
        results['breakdown'] = passed
    except Exception as e:
        log_test("GET /transactions/breakdown", False, str(e))
        results['breakdown'] = False
    
    # Transaction stats
    try:
        r = requests.get(f"{BASE_URL}/transactions/stats", headers=headers)
        passed = r.status_code == 200
        data = r.json() if passed else {}
        log_test("GET /transactions/stats", passed, 
                f"Total spent: ${data.get('total_spent')}")
        results['stats'] = passed
    except Exception as e:
        log_test("GET /transactions/stats", False, str(e))
        results['stats'] = False
    
    # Recategorize transaction
    if results.get('transaction_id'):
        try:
            txn_id = results['transaction_id']
            r = requests.post(f"{BASE_URL}/transactions/{txn_id}/categorize", headers=headers)
            passed = r.status_code == 200
            data = r.json() if passed else {}
            log_test(f"POST /transactions/{txn_id}/categorize", passed, 
                    f"Category: {data.get('category')}")
            results['recategorize'] = passed
        except Exception as e:
            log_test(f"POST /transactions/{txn_id}/categorize", False, str(e))
            results['recategorize'] = False
    
    return results

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  CreditSphere API Comprehensive Test Suite")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}{Colors.END}\n")
    
    all_results = {}
    
    # 1. Basic endpoints
    print(f"\n{Colors.YELLOW}[1/6] Testing Basic Endpoints{Colors.END}")
    all_results['health'] = test_health()
    all_results['root'] = test_root()
    
    # 2. Authentication flow
    print(f"\n{Colors.YELLOW}[2/6] Testing Authentication Flow{Colors.END}")
    auth_results = test_auth_flow()
    all_results['auth'] = auth_results
    
    if not auth_results.get('login'):
        print(f"\n{Colors.RED}❌ Login failed, cannot continue tests{Colors.END}")
        return
    
    access_token = auth_results.get('access_token')
    
    # 3. Quota endpoints
    print(f"\n{Colors.YELLOW}[3/6] Testing Quota Endpoints{Colors.END}")
    all_results['quota'] = test_quota_endpoints(access_token)
    
    # 4. File upload
    print(f"\n{Colors.YELLOW}[4/6] Testing File Upload{Colors.END}")
    statement_id = test_file_upload(access_token)
    all_results['upload'] = statement_id is not None
    
    # 5. Statement management
    if statement_id:
        print(f"\n{Colors.YELLOW}[5/6] Testing Statement Endpoints{Colors.END}")
        all_results['statements'] = test_statement_endpoints(access_token, statement_id)
    
    # 6. Transaction endpoints
    print(f"\n{Colors.YELLOW}[6/6] Testing Transaction Endpoints{Colors.END}")
    all_results['transactions'] = test_transaction_endpoints(access_token)
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print("  Test Summary")
    print(f"{'='*60}{Colors.END}\n")
    
    total_tests = 0
    passed_tests = 0
    
    def count_results(results):
        nonlocal total_tests, passed_tests
        if isinstance(results, dict):
            for v in results.values():
                if isinstance(v, bool):
                    total_tests += 1
                    if v:
                        passed_tests += 1
                elif isinstance(v, dict):
                    count_results(v)
        elif isinstance(results, bool):
            total_tests += 1
            if results:
                passed_tests += 1
    
    count_results(all_results)
    
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    color = Colors.GREEN if pass_rate >= 80 else Colors.YELLOW if pass_rate >= 60 else Colors.RED
    
    print(f"{color}Passed: {passed_tests}/{total_tests} ({pass_rate:.1f}%){Colors.END}\n")
    
    if pass_rate == 100:
        print(f"{Colors.GREEN}🎉 All tests passed!{Colors.END}\n")
    elif pass_rate >= 80:
        print(f"{Colors.YELLOW}⚠️  Most tests passed, some minor issues{Colors.END}\n")
    else:
        print(f"{Colors.RED}❌ Multiple failures detected{Colors.END}\n")

if __name__ == "__main__":
    main()
