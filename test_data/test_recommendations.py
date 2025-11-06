"""
Test script for NAV calculation engine and credit card recommendations API

Tests:
1. User spending profile analysis
2. NAV calculation for individual cards
3. Card recommendation API endpoint
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Test credentials (from previous tests)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"


def get_auth_token():
    """Login and get JWT token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login successful\n")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}\n")
        return None


def test_card_recommendations(token):
    """Test GET /recommendations/cards endpoint"""
    print("=" * 80)
    print("🎯 TEST: Card Recommendations API")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Basic recommendations (default parameters)
    print("\n📋 Test 1: Get basic recommendations (default parameters)")
    response = requests.get(
        f"{BASE_URL}/recommendations/cards",
        headers=headers
    )
    
    if response.status_code == 200:
        recommendations = response.json()
        print(f"✅ Request successful")
        print(f"   Returned {len(recommendations)} recommendations\n")
        
        # Display top 3 cards
        print("Top 3 recommended cards:")
        print("-" * 80)
        for i, card in enumerate(recommendations[:3], 1):
            print(f"{i}. {card['issuer']} - {card['product_name']}")
            print(f"   NAV: ${card['nav']:.2f} CAD/year")
            print(f"   └─ Annual Rewards: ${card['annual_rewards']:.2f}")
            print(f"   └─ Welcome Bonus (amortized): ${card['welcome_bonus_amortized']:.2f}")
            print(f"   └─ Annual Fee: ${card['annual_fee']:.2f}")
            print()
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"   Response: {response.text}\n")
        return
    
    # Test 2: With custom parameters
    print("\n📋 Test 2: Custom parameters (6 months, 5-year welcome bonus amortization)")
    response = requests.get(
        f"{BASE_URL}/recommendations/cards",
        headers=headers,
        params={
            "months": 6,
            "welcome_bonus_years": 5,
            "limit": 5
        }
    )
    
    if response.status_code == 200:
        recommendations = response.json()
        print(f"✅ Request successful")
        print(f"   Returned {len(recommendations)} recommendations\n")
        
        print("Top 5 cards (6-month analysis, 5-year welcome bonus amortization):")
        print("-" * 80)
        for i, card in enumerate(recommendations, 1):
            print(f"{i}. {card['issuer']} - {card['product_name']}: NAV = ${card['nav']:.2f}")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"   Response: {response.text}\n")
    
    # Test 3: With income filter
    print("\n📋 Test 3: Filter by minimum income requirement")
    response = requests.get(
        f"{BASE_URL}/recommendations/cards",
        headers=headers,
        params={
            "min_income": 60000,
            "limit": 10
        }
    )
    
    if response.status_code == 200:
        recommendations = response.json()
        print(f"✅ Request successful")
        print(f"   Returned {len(recommendations)} cards (min income: $60,000)\n")
        
        print("Cards suitable for $60,000 income:")
        print("-" * 80)
        for i, card in enumerate(recommendations, 1):
            income_req = card.get('min_income') or "No requirement"
            household_req = card.get('min_household_income') or "No requirement"
            print(f"{i}. {card['product_name']}")
            print(f"   NAV: ${card['nav']:.2f} | Personal: {income_req} | Household: {household_req}")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"   Response: {response.text}\n")


def test_detailed_nav_breakdown(token):
    """Test detailed NAV calculation breakdown"""
    print("\n" + "=" * 80)
    print("📊 TEST: Detailed NAV Breakdown Analysis")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/recommendations/cards",
        headers=headers,
        params={"limit": 1}
    )
    
    if response.status_code == 200:
        card = response.json()[0]
        
        print(f"\n🏆 Top Recommended Card:")
        print("-" * 80)
        print(f"Card: {card['issuer']} {card['product_name']}")
        print(f"Network: {card.get('card_network', 'N/A')}")
        print()
        print("NAV Breakdown:")
        print(f"  Annual Rewards:       ${card['annual_rewards']:>10.2f}")
        print(f"  Welcome Bonus (amor): ${card['welcome_bonus_amortized']:>10.2f}")
        print(f"  Annual Fee:          -${card['annual_fee']:>10.2f}")
        print(f"  " + "-" * 40)
        print(f"  Net Annual Value:     ${card['nav']:>10.2f}")
        print()
        print("Eligibility:")
        print(f"  Min Personal Income:  ${card.get('min_income', 0):,}" if card.get('min_income') else "  Min Personal Income:  No requirement")
        print(f"  Min Household Income: ${card.get('min_household_income', 0):,}" if card.get('min_household_income') else "  Min Household Income: No requirement")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"   Response: {response.text}")


def check_api_health():
    """Check if API is running"""
    print("🏥 Checking API health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy\n")
            return True
        else:
            print(f"⚠️  API returned status code {response.status_code}\n")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}\n")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("🧪 NAV Calculation Engine & Recommendations API Test Suite")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Health check
    if not check_api_health():
        print("⚠️  Please ensure the backend is running:")
        print("   wsl bash -c \"cd /mnt/c/Users/whyke/financial-advisor && docker-compose up -d\"")
        return
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("⚠️  Please ensure test user exists. Run test_all_apis.py first to create user.")
        return
    
    # Run tests
    test_card_recommendations(token)
    test_detailed_nav_breakdown(token)
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)
    print("\n💡 Next steps:")
    print("   1. Review the recommendations in the output above")
    print("   2. Check API documentation: http://localhost:8000/docs")
    print("   3. Test with different spending patterns by uploading more statements")
    print()


if __name__ == "__main__":
    main()
