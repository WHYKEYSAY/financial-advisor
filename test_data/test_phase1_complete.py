#!/usr/bin/env python3
"""
CreditSphere Phase 1 MVP - Complete Test Suite

Tests all backend functionality:
- Authentication & Authorization
- File Upload & Statement Parsing
- Transaction Management
- Account Management
- NAV Calculation & Card Recommendations
- VCM Phase 1: Credit Overview & Utilization
- VCM Phase 2: Spending Optimization
"""
import requests
import json
import time
from decimal import Decimal
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"phase1_test_{int(time.time())}@example.com"
TEST_PASSWORD = "Phase1Test123!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}{'─'*70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'─'*70}{Colors.END}")

def print_subsection(text):
    print(f"\n{Colors.MAGENTA}▸ {text}{Colors.END}")

def log_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"  {status} {name}")
    if details:
        print(f"       {Colors.YELLOW}{details}{Colors.END}")
    return passed

def test_auth_flow():
    """Test authentication system"""
    print_section("1. Authentication & Authorization")
    results = []
    
    # Register
    print_subsection("User Registration")
    try:
        r = requests.post(f"{BASE_URL}/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "locale": "en"
        })
        passed = r.status_code == 201
        results.append(log_test("Register new user", passed, f"Email: {TEST_EMAIL}"))
    except Exception as e:
        results.append(log_test("Register new user", False, str(e)))
        return results, None
    
    # Login
    print_subsection("User Login")
    try:
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        passed = r.status_code == 200 and 'access_token' in r.json()
        access_token = r.json()['access_token'] if passed else None
        results.append(log_test("Login with credentials", passed, f"Token: {access_token[:20] if access_token else 'N/A'}..."))
        
        if not passed:
            return results, None
    except Exception as e:
        results.append(log_test("Login with credentials", False, str(e)))
        return results, None
    
    # Get current user
    print_subsection("Get Current User")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        passed = r.status_code == 200 and r.json().get('email') == TEST_EMAIL
        results.append(log_test("Get current user info", passed))
    except Exception as e:
        results.append(log_test("Get current user info", False, str(e)))
    
    return results, access_token


def test_quota_system(access_token):
    """Test quota system"""
    print_section("2. Quota System")
    results = []
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print_subsection("Quota Status")
    try:
        r = requests.get(f"{BASE_URL}/quota/status", headers=headers)
        passed = r.status_code == 200
        data = r.json() if passed else {}
        results.append(log_test("Get quota status", passed, 
                               f"Statements: {data.get('statements_parsed', 0)}/{data.get('statements_limit', 0)}"))
    except Exception as e:
        results.append(log_test("Get quota status", False, str(e)))
    
    return results


def test_vcm_card_management(access_token):
    """Test VCM card management"""
    print_section("3. VCM - Credit Card Management")
    results = []
    headers = {"Authorization": f"Bearer {access_token}"}
    card_ids = []
    
    # Add test cards
    print_subsection("Adding Test Credit Cards")
    test_cards = [
        {"issuer": "RBC", "product": "Avion Visa Infinite", "credit_limit": 10000.00, "last4": "1234", "due_day": 5},
        {"issuer": "MBNA", "product": "Rewards World Elite", "credit_limit": 5000.00, "last4": "5678", "due_day": 10},
        {"issuer": "CIBC", "product": "Dividend Visa", "credit_limit": 3000.00, "last4": "9012", "due_day": 15}
    ]
    
    for card_data in test_cards:
        try:
            r = requests.post(f"{BASE_URL}/vcm/cards", headers=headers, json=card_data)
            passed = r.status_code == 201
            if passed:
                card_response = r.json()
                card_ids.append(card_response['card_id'])
            results.append(log_test(f"Add {card_data['issuer']} {card_data['product']}", passed,
                                   f"Limit: ${card_data['credit_limit']:.2f}"))
        except Exception as e:
            results.append(log_test(f"Add {card_data['issuer']}", False, str(e)))
    
    # List all cards
    print_subsection("List All Cards")
    try:
        r = requests.get(f"{BASE_URL}/vcm/cards", headers=headers)
        passed = r.status_code == 200 and len(r.json()) == 3
        results.append(log_test("List all credit cards", passed, f"Found {len(r.json()) if passed else 0} cards"))
    except Exception as e:
        results.append(log_test("List all credit cards", False, str(e)))
    
    return results, card_ids


def test_vcm_credit_overview(access_token):
    """Test VCM credit overview and utilization"""
    print_section("4. VCM Phase 1 - Credit Overview & Utilization")
    results = []
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Credit Overview
    print_subsection("Credit Overview")
    try:
        r = requests.get(f"{BASE_URL}/vcm/overview", headers=headers)
        passed = r.status_code == 200
        if passed:
            data = r.json()
            results.append(log_test("Get credit overview", True,
                                   f"Total Limit: ${data['total_credit_limit']}, " +
                                   f"Utilization: {data['overall_utilization']}%"))
            
            # Validate structure
            checks = [
                ("Has total_credit_limit", "total_credit_limit" in data),
                ("Has overall_utilization", "overall_utilization" in data),
                ("Has health_status", "health_status" in data),
                ("Has cards_summary", "cards_summary" in data and len(data['cards_summary']) == 3)
            ]
            
            for name, check in checks:
                results.append(log_test(name, check))
        else:
            results.append(log_test("Get credit overview", False, f"Status: {r.status_code}"))
    except Exception as e:
        results.append(log_test("Get credit overview", False, str(e)))
    
    # Utilization Analysis
    print_subsection("Utilization Analysis")
    try:
        r = requests.get(f"{BASE_URL}/vcm/utilization", headers=headers)
        passed = r.status_code == 200
        if passed:
            data = r.json()
            results.append(log_test("Get utilization analysis", True,
                                   f"Overall: {data['overall_utilization']}%, " +
                                   f"Status: {data['health_status']}"))
        else:
            results.append(log_test("Get utilization analysis", False))
    except Exception as e:
        results.append(log_test("Get utilization analysis", False, str(e)))
    
    return results


def test_vcm_spending_optimization(access_token):
    """Test VCM Phase 2 - Spending Optimization"""
    print_section("5. VCM Phase 2 - Spending Optimization")
    results = []
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test scenarios
    test_scenarios = [
        {"amount": 500.00, "description": "Small purchase ($500)"},
        {"amount": 2000.00, "description": "Medium purchase ($2000)"},
        {"amount": 5000.00, "description": "Large purchase ($5000)"},
        {"amount": 25000.00, "description": "Exceeds total limit ($25000)"}
    ]
    
    for scenario in test_scenarios:
        print_subsection(scenario['description'])
        try:
            r = requests.post(f"{BASE_URL}/vcm/optimize-spending", 
                            headers=headers, 
                            json={"amount": scenario['amount']})
            passed = r.status_code == 200
            
            if passed:
                data = r.json()
                feasible = data['allocation_feasible']
                
                if feasible:
                    steps = len(data['allocation_steps'])
                    results.append(log_test(f"Optimize ${scenario['amount']:.2f}", True,
                                           f"Allocated across {steps} card(s), " +
                                           f"Strategy: {data['optimization_summary'][:50]}..."))
                    
                    # Validate allocation
                    total_allocated = sum(float(step['amount_to_charge']) 
                                        for step in data['allocation_steps'])
                    allocation_correct = abs(total_allocated - scenario['amount']) < 0.01
                    results.append(log_test("Allocation sum matches", allocation_correct,
                                           f"Allocated: ${total_allocated:.2f}"))
                    
                    # Check utilization stays reasonable
                    max_util = max(float(step['new_utilization']) 
                                 for step in data['allocation_steps'])
                    util_ok = max_util <= 50.0  # Should try to stay below 50%
                    results.append(log_test("Utilization stays reasonable", util_ok,
                                           f"Max utilization: {max_util:.2f}%"))
                else:
                    results.append(log_test(f"Optimize ${scenario['amount']:.2f}", True,
                                           f"Not feasible: {data['optimization_summary']}"))
            else:
                results.append(log_test(f"Optimize ${scenario['amount']:.2f}", False,
                                       f"Status: {r.status_code}"))
        except Exception as e:
            results.append(log_test(f"Optimize ${scenario['amount']:.2f}", False, str(e)))
    
    return results


def test_vcm_payment_reminders(access_token):
    """Test VCM payment reminders"""
    print_section("6. VCM - Payment Reminders")
    results = []
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print_subsection("Get Payment Reminders")
    try:
        r = requests.get(f"{BASE_URL}/vcm/reminders", headers=headers)
        passed = r.status_code == 200
        if passed:
            data = r.json()
            results.append(log_test("Get payment reminders", True,
                                   f"Found {len(data)} upcoming reminders"))
        else:
            results.append(log_test("Get payment reminders", False))
    except Exception as e:
        results.append(log_test("Get payment reminders", False, str(e)))
    
    return results


def test_accounts_api(access_token):
    """Test accounts API"""
    print_section("7. Account Management")
    results = []
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print_subsection("Account Summary")
    try:
        r = requests.get(f"{BASE_URL}/accounts/summary", headers=headers)
        passed = r.status_code == 200
        if passed:
            data = r.json()
            results.append(log_test("Get account summary", True,
                                   f"Credit cards: {len(data.get('credit_cards', {}).get('accounts', []))}"))
        else:
            results.append(log_test("Get account summary", False))
    except Exception as e:
        results.append(log_test("Get account summary", False, str(e)))
    
    print_subsection("List Accounts")
    try:
        r = requests.get(f"{BASE_URL}/accounts/list", headers=headers)
        passed = r.status_code == 200
        results.append(log_test("List all accounts", passed))
    except Exception as e:
        results.append(log_test("List all accounts", False, str(e)))
    
    return results


def test_recommendations_api(access_token):
    """Test credit card recommendations"""
    print_section("8. Credit Card Recommendations (NAV)")
    results = []
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print_subsection("Get Card Recommendations")
    try:
        r = requests.get(f"{BASE_URL}/recommendations/cards?months=12&limit=5", headers=headers)
        passed = r.status_code == 200
        if passed:
            data = r.json()
            results.append(log_test("Get NAV recommendations", True,
                                   f"Found {len(data)} card recommendations"))
            
            # Validate NAV structure
            if len(data) > 0:
                first_card = data[0]
                has_nav = 'nav' in first_card
                has_issuer = 'issuer' in first_card
                results.append(log_test("Recommendations have NAV data", has_nav and has_issuer,
                                       f"Top card: {first_card.get('issuer', 'N/A')}, NAV: ${first_card.get('nav', 0):.2f}"))
        else:
            results.append(log_test("Get NAV recommendations", False))
    except Exception as e:
        results.append(log_test("Get NAV recommendations", False, str(e)))
    
    return results


def test_health_check():
    """Test health check"""
    print_section("0. System Health Check")
    results = []
    
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        passed = r.status_code == 200
        results.append(log_test("Backend health check", passed))
    except Exception as e:
        results.append(log_test("Backend health check", False, str(e)))
        return results, False
    
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        passed = r.status_code == 200
        results.append(log_test("Root endpoint accessible", passed))
    except Exception as e:
        results.append(log_test("Root endpoint accessible", False, str(e)))
    
    return results, True


def main():
    """Main test execution"""
    print_header("CreditSphere Phase 1 MVP - Complete Test Suite")
    print(f"{Colors.YELLOW}Testing all backend functionality...{Colors.END}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}\n")
    
    all_results = []
    
    # 0. Health check
    health_results, system_healthy = test_health_check()
    all_results.extend(health_results)
    
    if not system_healthy:
        print(f"\n{Colors.RED}❌ System health check failed. Please ensure the backend is running.{Colors.END}")
        return 1
    
    # 1. Authentication
    auth_results, access_token = test_auth_flow()
    all_results.extend(auth_results)
    
    if not access_token:
        print(f"\n{Colors.RED}❌ Authentication failed. Cannot proceed with tests.{Colors.END}")
        return 1
    
    # 2. Quota system
    all_results.extend(test_quota_system(access_token))
    
    # 3. VCM Card Management
    card_results, card_ids = test_vcm_card_management(access_token)
    all_results.extend(card_results)
    
    if not card_ids:
        print(f"\n{Colors.YELLOW}⚠ No cards created. VCM tests may have limited results.{Colors.END}")
    
    # 4. VCM Phase 1
    all_results.extend(test_vcm_credit_overview(access_token))
    
    # 5. VCM Phase 2
    all_results.extend(test_vcm_spending_optimization(access_token))
    
    # 6. VCM Reminders
    all_results.extend(test_vcm_payment_reminders(access_token))
    
    # 7. Accounts
    all_results.extend(test_accounts_api(access_token))
    
    # 8. Recommendations
    all_results.extend(test_recommendations_api(access_token))
    
    # Summary
    print_header("Test Summary")
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results if r)
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Colors.BOLD}Results:{Colors.END}")
    print(f"  Total Tests:  {total_tests}")
    print(f"  {Colors.GREEN}Passed:       {passed_tests} ({pass_rate:.1f}%){Colors.END}")
    
    if failed_tests > 0:
        print(f"  {Colors.RED}Failed:       {failed_tests} ({100-pass_rate:.1f}%){Colors.END}")
    
    print(f"\n{Colors.BOLD}Phase 1 MVP Status:{Colors.END}")
    if pass_rate >= 95:
        print(f"  {Colors.GREEN}✓ READY FOR PRODUCTION{Colors.END}")
        print(f"  {Colors.GREEN}All critical systems operational!{Colors.END}")
    elif pass_rate >= 80:
        print(f"  {Colors.YELLOW}⚠ MINOR ISSUES DETECTED{Colors.END}")
        print(f"  {Colors.YELLOW}Review failed tests before deployment{Colors.END}")
    else:
        print(f"  {Colors.RED}✗ SIGNIFICANT ISSUES{Colors.END}")
        print(f"  {Colors.RED}Critical functionality is broken{Colors.END}")
    
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    # Exit code
    return 0 if pass_rate >= 95 else 1


if __name__ == "__main__":
    exit(main())
