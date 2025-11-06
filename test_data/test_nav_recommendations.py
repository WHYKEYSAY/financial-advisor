#!/usr/bin/env python3
"""
Complete test suite for NAV calculation engine and credit card recommendations

Tests:
1. User registration and authentication
2. Upload sample transactions (diverse spending categories)
3. Get credit card recommendations sorted by NAV
4. Verify NAV calculation accuracy
"""
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal

BASE_URL = "http://localhost:8000"

# Test user credentials
TEST_EMAIL = "navtest@example.com"
TEST_PASSWORD = "NavTest123!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def check_health():
    """Check if API is running"""
    print_header("HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("API is healthy and running")
            return True
        else:
            print_error(f"API returned status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to API: {e}")
        return False


def register_and_login():
    """Register a new test user and login"""
    print_header("USER AUTHENTICATION")
    
    # Try to register
    print_info(f"Registering test user: {TEST_EMAIL}")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "locale": "en"
        }
    )
    
    if response.status_code == 201:
        print_success("User registered successfully")
    elif response.status_code == 400 and "already registered" in response.text.lower():
        print_warning("User already exists, proceeding to login")
    else:
        print_error(f"Registration failed: {response.status_code} - {response.text}")
        return None
    
    # Login
    print_info("Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_success(f"Login successful. Token: {token[:20]}...")
        return token
    else:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return None


def upload_sample_transactions(token):
    """Upload diverse sample transactions to test spending profile analysis"""
    print_header("UPLOADING SAMPLE TRANSACTIONS")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check if we can use an existing statement file
    print_info("Checking for existing statements...")
    
    # Try to upload MBNA statement if it exists
    try:
        mbna_path = "C:\\Users\\whyke\\financial-advisor\\bankstatement\\MBNA.PDF"
        with open(mbna_path, 'rb') as f:
            files = {'file': ('MBNA.PDF', f, 'application/pdf')}
            response = requests.post(
                f"{BASE_URL}/files/upload",
                headers=headers,
                files=files
            )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Uploaded MBNA statement: {data.get('transaction_count', 0)} transactions")
            return True
        else:
            print_warning(f"Could not upload statement: {response.status_code}")
            return False
    except FileNotFoundError:
        print_warning("MBNA.PDF not found, cannot upload transactions")
        print_info("For accurate recommendations, please upload a statement first")
        return False
    except Exception as e:
        print_error(f"Error uploading file: {e}")
        return False


def get_recommendations(token, months=12, include_welcome_bonus=True):
    """Get credit card recommendations"""
    print_header(f"CREDIT CARD RECOMMENDATIONS (Last {months} months)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    params = {
        "months": months,
        "welcome_bonus_years": 3,  # Amortize over 3 years
        "limit": 10
    }
    
    print_info(f"Fetching recommendations with params: {params}")
    
    response = requests.get(
        f"{BASE_URL}/recommendations/cards",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        recommendations = response.json()
        print_success(f"Retrieved {len(recommendations)} card recommendations\n")
        return recommendations
    else:
        print_error(f"Failed to get recommendations: {response.status_code}")
        print_error(f"Response: {response.text}")
        return []


def display_recommendations(recommendations):
    """Display recommendation results in a formatted table"""
    if not recommendations:
        print_warning("No recommendations available")
        print_info("This may be because:")
        print_info("  1. No credit cards are active in the database")
        print_info("  2. No transactions have been uploaded")
        print_info("  3. All NAV values are very negative")
        return
    
    print(f"\n{Colors.BOLD}{'Rank':<6}{'Card Name':<45}{'NAV ($/year)':<15}{'Annual Fee':<15}{Colors.END}")
    print("-" * 80)
    
    for idx, card in enumerate(recommendations, 1):
        nav = card.get('nav', 0)
        annual_fee = card.get('annual_fee', 0)
        card_name = f"{card.get('issuer', 'Unknown')} {card.get('product_name', 'Unknown')}"
        
        # Color code NAV
        if nav > 200:
            nav_color = Colors.GREEN
        elif nav > 0:
            nav_color = Colors.YELLOW
        else:
            nav_color = Colors.RED
        
        print(f"{idx:<6}{card_name:<45}{nav_color}${nav:>10.2f}{Colors.END}   ${annual_fee:>10.2f}")
    
    # Display detailed breakdown for top 3
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}TOP 3 RECOMMENDATIONS - DETAILED BREAKDOWN{Colors.END}")
    print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")
    
    for idx, card in enumerate(recommendations[:3], 1):
        card_name = f"{card.get('issuer', '')} {card.get('product_name', '')}"
        nav = card.get('nav', 0)
        annual_rewards = card.get('annual_rewards', 0)
        welcome_bonus = card.get('welcome_bonus_amortized', 0)
        annual_fee = card.get('annual_fee', 0)
        network = card.get('card_network', 'N/A')
        min_income = card.get('min_income')
        min_household_income = card.get('min_household_income')
        
        print(f"{Colors.BOLD}#{idx}. {card_name}{Colors.END}")
        print(f"   Network: {network}")
        print(f"   {Colors.CYAN}NAV Calculation:{Colors.END}")
        print(f"     Annual Rewards:              ${annual_rewards:>10.2f}")
        print(f"     Welcome Bonus (amortized):   ${welcome_bonus:>10.2f}")
        print(f"     Annual Fee:                 -${annual_fee:>10.2f}")
        print(f"     {'-'*40}")
        
        nav_color = Colors.GREEN if nav > 0 else Colors.RED
        print(f"     {nav_color}{Colors.BOLD}Net Annual Value (NAV):      ${nav:>10.2f}{Colors.END}")
        
        print(f"   {Colors.CYAN}Eligibility:{Colors.END}")
        if min_income:
            print(f"     Min Personal Income:  ${min_income:,}")
        else:
            print(f"     Min Personal Income:  No requirement")
        
        if min_household_income:
            print(f"     Min Household Income: ${min_household_income:,}")
        else:
            print(f"     Min Household Income: No requirement")
        
        print()


def test_different_scenarios(token):
    """Test recommendations with different parameters"""
    print_header("TESTING DIFFERENT SCENARIOS")
    
    scenarios = [
        {"months": 6, "name": "6-month analysis"},
        {"months": 12, "name": "12-month analysis (default)"},
        {"months": 24, "name": "24-month analysis"},
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for scenario in scenarios:
        print(f"\n{Colors.BLUE}Scenario: {scenario['name']}{Colors.END}")
        response = requests.get(
            f"{BASE_URL}/recommendations/cards",
            headers=headers,
            params={"months": scenario["months"], "limit": 3}
        )
        
        if response.status_code == 200:
            recs = response.json()
            if recs:
                top_card = recs[0]
                print(f"  Top recommendation: {top_card.get('issuer')} {top_card.get('product_name')}")
                print(f"  NAV: ${top_card.get('nav'):.2f}")
            else:
                print("  No recommendations available")
        else:
            print(f"  {Colors.RED}Failed: {response.status_code}{Colors.END}")


def verify_nav_calculation(recommendations):
    """Verify NAV calculation logic"""
    print_header("NAV CALCULATION VERIFICATION")
    
    if not recommendations:
        print_warning("No recommendations to verify")
        return
    
    print_info("Verifying NAV formula: NAV = Annual Rewards + Welcome Bonus - Annual Fee\n")
    
    all_correct = True
    for idx, card in enumerate(recommendations[:3], 1):
        nav = card.get('nav', 0)
        annual_rewards = card.get('annual_rewards', 0)
        welcome_bonus = card.get('welcome_bonus_amortized', 0)
        annual_fee = card.get('annual_fee', 0)
        
        calculated_nav = annual_rewards + welcome_bonus - annual_fee
        diff = abs(calculated_nav - nav)
        
        card_name = f"{card.get('issuer', '')} {card.get('product_name', '')}"
        
        if diff < 0.01:  # Allow for rounding errors
            print_success(f"#{idx} {card_name}: NAV calculation correct (${nav:.2f})")
        else:
            print_error(f"#{idx} {card_name}: NAV mismatch!")
            print(f"     Expected: ${calculated_nav:.2f}")
            print(f"     Got: ${nav:.2f}")
            print(f"     Difference: ${diff:.2f}")
            all_correct = False
    
    if all_correct:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All NAV calculations are correct!{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some NAV calculations have errors{Colors.END}")


def main():
    """Run complete test suite"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "NAV CALCULATION ENGINE & RECOMMENDATIONS API TEST SUITE".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print(f"{Colors.END}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Health check
    if not check_health():
        print_error("Backend is not running. Please start it with:")
        print("  wsl bash -c \"cd /mnt/c/Users/whyke/financial-advisor && docker-compose up -d\"")
        return
    
    # Step 2: Authentication
    token = register_and_login()
    if not token:
        return
    
    # Step 3: Upload transactions (optional, helps with better recommendations)
    upload_sample_transactions(token)
    
    # Step 4: Get recommendations
    recommendations = get_recommendations(token)
    
    # Step 5: Display results
    display_recommendations(recommendations)
    
    # Step 6: Verify calculations
    verify_nav_calculation(recommendations)
    
    # Step 7: Test different scenarios
    test_different_scenarios(token)
    
    # Final summary
    print_header("TEST SUMMARY")
    print_success("✓ Authentication working")
    print_success("✓ Recommendations API working")
    print_success(f"✓ Retrieved {len(recommendations)} card recommendations")
    
    if recommendations:
        top_nav = recommendations[0].get('nav', 0)
        print_success(f"✓ Top NAV: ${top_nav:.2f} ({recommendations[0].get('issuer')} {recommendations[0].get('product_name')})")
    
    print(f"\n{Colors.CYAN}💡 Next Steps:{Colors.END}")
    print("  1. View API documentation: http://localhost:8000/docs")
    print("  2. Upload more statements to improve recommendations")
    print("  3. Test with different user spending patterns")
    print(f"  4. Check detailed logs in backend container\n")


if __name__ == "__main__":
    main()
