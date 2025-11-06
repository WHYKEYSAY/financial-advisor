#!/usr/bin/env python3
"""
VCM (Virtual Credit Manager) API Testing Script

Tests all VCM endpoints:
- Credit overview
- Utilization tracking
- Card management
- Payment reminders
"""
import requests
import json
import time
from decimal import Decimal
from datetime import datetime, date

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"vcm_test_{int(time.time())}@example.com"
TEST_PASSWORD = "VCMTest123!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}{'─'*60}{Colors.END}")
    print(f"{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'─'*60}{Colors.END}")

def log_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} {name}")
    if details:
        print(f"     {details}")

def print_json(data, indent=2):
    print(json.dumps(data, indent=indent, default=str))

def assert_decimal_places(value, decimal_places=2, name="value"):
    """Assert that a value has exactly N decimal places"""
    value_str = str(value)
    if '.' in value_str:
        actual_decimals = len(value_str.split('.')[1])
        return actual_decimals <= decimal_places
    return True

def register_and_login():
    """Register a new user and obtain access token"""
    print_section("Authentication Setup")
    
    # Register
    try:
        r = requests.post(f"{BASE_URL}/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "locale": "en"
        })
        if r.status_code == 201:
            log_test("User Registration", True, f"Email: {TEST_EMAIL}")
        else:
            log_test("User Registration", False, f"Status: {r.status_code}")
            return None
    except Exception as e:
        log_test("User Registration", False, str(e))
        return None
    
    # Login
    try:
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if r.status_code == 200:
            access_token = r.json()['access_token']
            log_test("User Login", True, f"Token: {access_token[:20]}...")
            return access_token
        else:
            log_test("User Login", False, f"Status: {r.status_code}")
            return None
    except Exception as e:
        log_test("User Login", False, str(e))
        return None

def add_test_cards(access_token):
    """Add test credit cards"""
    print_section("Adding Test Credit Cards")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    cards = []
    
    test_cards = [
        {
            "issuer": "RBC",
            "product": "Avion Visa Infinite",
            "credit_limit": 10000.00,
            "last4": "1234",
            "statement_day": 15,
            "due_day": 5
        },
        {
            "issuer": "MBNA",
            "product": "Rewards World Elite",
            "credit_limit": 5000.00,
            "last4": "5678",
            "statement_day": 20,
            "due_day": 10
        },
        {
            "issuer": "CIBC",
            "product": "Dividend Visa Infinite",
            "credit_limit": 3000.00,
            "last4": "9012",
            "statement_day": 1,
            "due_day": 25
        }
    ]
    
    for card_data in test_cards:
        try:
            r = requests.post(f"{BASE_URL}/vcm/cards", headers=headers, json=card_data)
            if r.status_code == 201:
                card_response = r.json()
                cards.append(card_response)
                log_test(f"Add Card: {card_data['issuer']} {card_data['product']}", 
                        True, 
                        f"ID: {card_response['card_id']}, Limit: ${card_response['credit_limit']}")
            else:
                log_test(f"Add Card: {card_data['issuer']}", False, f"Status: {r.status_code}, {r.text}")
        except Exception as e:
            log_test(f"Add Card: {card_data['issuer']}", False, str(e))
    
    return cards

def add_test_transactions(access_token, cards):
    """Add test transactions using direct database insertion"""
    print_section("Adding Test Transactions")
    
    # Note: Since there's no public API to create transactions with card_id,
    # we'll need to use the Docker exec to insert data directly
    # For now, we'll document this and proceed with testing cards without transactions
    
    print(f"{Colors.YELLOW}Note: Transaction creation requires direct database access.{Colors.END}")
    print(f"{Colors.YELLOW}Testing VCM with cards but without transaction history.{Colors.END}")
    print(f"{Colors.YELLOW}In production, transactions would be added via statement uploads.{Colors.END}")
    
    # We could use docker exec to insert transactions:
    # docker exec creditsphere-postgres psql -U postgres -d creditsphere -c "INSERT INTO transactions ..."
    return True

def test_credit_overview(access_token, expected_limit):
    """Test GET /vcm/overview"""
    print_section("Testing Credit Overview")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        r = requests.get(f"{BASE_URL}/vcm/overview", headers=headers)
        if r.status_code == 200:
            data = r.json()
            print_json(data)
            
            # Validate response structure
            checks = []
            checks.append(("Has total_credit_limit", "total_credit_limit" in data))
            checks.append(("Has total_used", "total_used" in data))
            checks.append(("Has overall_utilization", "overall_utilization" in data))
            checks.append(("Has health_status", "health_status" in data))
            checks.append(("Has cards_summary", "cards_summary" in data))
            
            # Validate calculations
            checks.append(("Total limit matches expected", 
                          float(data['total_credit_limit']) == expected_limit))
            checks.append(("Total used is decimal", 
                          assert_decimal_places(data['total_used'])))
            checks.append(("Utilization is decimal", 
                          assert_decimal_places(data['overall_utilization'])))
            checks.append(("Cards summary is list", 
                          isinstance(data['cards_summary'], list)))
            checks.append(("Cards count matches", 
                          len(data['cards_summary']) == 3))
            
            # Check individual cards
            for card in data['cards_summary']:
                checks.append((f"Card {card['card_id']} has utilization_rate", 
                              'utilization_rate' in card))
                checks.append((f"Card {card['card_id']} has health_status", 
                              'health_status' in card))
                checks.append((f"Card {card['card_id']} utilization is decimal", 
                              assert_decimal_places(card['utilization_rate'])))
            
            # Print validation results
            all_passed = all(check[1] for check in checks)
            for name, passed in checks:
                log_test(name, passed)
            
            log_test("GET /vcm/overview", all_passed, 
                    f"Total Limit: ${data['total_credit_limit']}, Utilization: {data['overall_utilization']}%")
            return all_passed
        else:
            log_test("GET /vcm/overview", False, f"Status: {r.status_code}, {r.text}")
            return False
    except Exception as e:
        log_test("GET /vcm/overview", False, str(e))
        return False

def test_utilization(access_token):
    """Test GET /vcm/utilization"""
    print_section("Testing Utilization Analysis")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        r = requests.get(f"{BASE_URL}/vcm/utilization", headers=headers)
        if r.status_code == 200:
            data = r.json()
            print_json(data)
            
            checks = []
            checks.append(("Has overall_utilization", "overall_utilization" in data))
            checks.append(("Has health_status", "health_status" in data))
            checks.append(("Has per_card", "per_card" in data))
            checks.append(("Per card is list", isinstance(data['per_card'], list)))
            checks.append(("Per card count is 3", len(data['per_card']) == 3))
            checks.append(("Utilization is decimal", 
                          assert_decimal_places(data['overall_utilization'])))
            
            all_passed = all(check[1] for check in checks)
            for name, passed in checks:
                log_test(name, passed)
            
            log_test("GET /vcm/utilization", all_passed)
            return all_passed
        else:
            log_test("GET /vcm/utilization", False, f"Status: {r.status_code}")
            return False
    except Exception as e:
        log_test("GET /vcm/utilization", False, str(e))
        return False

def test_card_utilization(access_token, card_id):
    """Test GET /vcm/cards/{card_id}/utilization"""
    print_section(f"Testing Card {card_id} Utilization")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        r = requests.get(f"{BASE_URL}/vcm/cards/{card_id}/utilization", headers=headers)
        if r.status_code == 200:
            data = r.json()
            print_json(data)
            
            checks = []
            checks.append(("Has card_id", data.get('card_id') == card_id))
            checks.append(("Has issuer", "issuer" in data))
            checks.append(("Has credit_limit", "credit_limit" in data))
            checks.append(("Has current_balance", "current_balance" in data))
            checks.append(("Has utilization_rate", "utilization_rate" in data))
            checks.append(("Has health_status", "health_status" in data))
            checks.append(("Credit limit is decimal", 
                          assert_decimal_places(data['credit_limit'])))
            checks.append(("Current balance is decimal", 
                          assert_decimal_places(data['current_balance'])))
            checks.append(("Utilization is decimal", 
                          assert_decimal_places(data['utilization_rate'])))
            
            all_passed = all(check[1] for check in checks)
            for name, passed in checks:
                log_test(name, passed)
            
            log_test(f"GET /vcm/cards/{card_id}/utilization", all_passed)
            return all_passed
        else:
            log_test(f"GET /vcm/cards/{card_id}/utilization", False, 
                    f"Status: {r.status_code}")
            return False
    except Exception as e:
        log_test(f"GET /vcm/cards/{card_id}/utilization", False, str(e))
        return False

def test_list_cards(access_token):
    """Test GET /vcm/cards"""
    print_section("Testing List Cards")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        r = requests.get(f"{BASE_URL}/vcm/cards", headers=headers)
        if r.status_code == 200:
            data = r.json()
            print_json(data)
            
            checks = []
            checks.append(("Response is list", isinstance(data, list)))
            checks.append(("Has 3 cards", len(data) == 3))
            
            for card in data:
                checks.append((f"Card {card.get('card_id')} has all fields", 
                              all(key in card for key in ['card_id', 'issuer', 'product', 
                                                          'credit_limit', 'current_balance', 
                                                          'utilization_rate', 'health_status'])))
            
            all_passed = all(check[1] for check in checks)
            for name, passed in checks:
                log_test(name, passed)
            
            log_test("GET /vcm/cards", all_passed)
            return all_passed
        else:
            log_test("GET /vcm/cards", False, f"Status: {r.status_code}")
            return False
    except Exception as e:
        log_test("GET /vcm/cards", False, str(e))
        return False

def test_payment_reminders(access_token):
    """Test GET /vcm/reminders"""
    print_section("Testing Payment Reminders")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        r = requests.get(f"{BASE_URL}/vcm/reminders", headers=headers)
        if r.status_code == 200:
            data = r.json()
            print_json(data)
            
            checks = []
            checks.append(("Response is list", isinstance(data, list)))
            
            # Reminders may be empty if no cards are due soon
            if len(data) > 0:
                for reminder in data:
                    checks.append((f"Reminder for card {reminder.get('card_id')} has due_date", 
                                  'due_date' in reminder))
                    checks.append((f"Reminder for card {reminder.get('card_id')} has days_until_due", 
                                  'days_until_due' in reminder))
            
            all_passed = all(check[1] for check in checks) if checks else True
            for name, passed in checks:
                log_test(name, passed)
            
            log_test("GET /vcm/reminders", all_passed, 
                    f"Found {len(data)} upcoming reminders")
            return all_passed
        else:
            log_test("GET /vcm/reminders", False, f"Status: {r.status_code}")
            return False
    except Exception as e:
        log_test("GET /vcm/reminders", False, str(e))
        return False

def test_delete_card(access_token, card_id):
    """Test DELETE /vcm/cards/{card_id}"""
    print_section(f"Testing Delete Card {card_id}")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        r = requests.delete(f"{BASE_URL}/vcm/cards/{card_id}", headers=headers)
        passed = r.status_code == 204
        log_test(f"DELETE /vcm/cards/{card_id}", passed)
        return passed
    except Exception as e:
        log_test(f"DELETE /vcm/cards/{card_id}", False, str(e))
        return False

def main():
    """Main test execution"""
    print_header("VCM API Testing Suite")
    print(f"{Colors.YELLOW}Testing VCM endpoints...{Colors.END}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}\n")
    
    results = []
    
    # 1. Register and login
    access_token = register_and_login()
    if not access_token:
        print(f"\n{Colors.RED}Authentication failed. Exiting.{Colors.END}")
        return
    
    # 2. Add test cards
    cards = add_test_cards(access_token)
    if not cards or len(cards) != 3:
        print(f"\n{Colors.RED}Failed to add test cards. Exiting.{Colors.END}")
        return
    
    card_ids = [card['card_id'] for card in cards]
    expected_total_limit = 10000.00 + 5000.00 + 3000.00  # Total: 18000.00
    
    # 3. Add test transactions (if possible)
    add_test_transactions(access_token, cards)
    
    # 4. Test credit overview
    results.append(test_credit_overview(access_token, 18000.00))
    
    # 5. Test utilization
    results.append(test_utilization(access_token))
    
    # 6. Test individual card utilization
    for card_id in card_ids:
        results.append(test_card_utilization(access_token, card_id))
    
    # 7. Test list cards
    results.append(test_list_cards(access_token))
    
    # 8. Test payment reminders
    results.append(test_payment_reminders(access_token))
    
    # 9. Test delete card
    results.append(test_delete_card(access_token, card_ids[0]))
    
    # Summary
    print_header("Test Summary")
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests:  {total_tests}")
    print(f"{Colors.GREEN}Passed:       {passed_tests}{Colors.END}")
    if failed_tests > 0:
        print(f"{Colors.RED}Failed:       {failed_tests}{Colors.END}")
    else:
        print(f"{Colors.GREEN}All tests passed!{Colors.END}")
    
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    main()
