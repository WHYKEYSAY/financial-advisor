#!/usr/bin/env python3
"""
E2E API Tests for CreditSphere Production Environment
Run: python test_e2e_api.py
"""
import json
import time
import uuid

try:
    import requests
except ImportError:
    print("❌ requests not installed. Run: pip install requests")
    exit(1)

BACKEND_URL = "https://financial-advisor-production-e0a9.up.railway.app"

def test_health():
    """Test backend health endpoint"""
    print("\n🔍 Testing: Backend Health")
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if resp.status_code == 200:
            print(f"   ✅ PASS - Status: {resp.status_code}")
            print(f"   Response: {resp.json()}")
            return True
        else:
            print(f"   ❌ FAIL - Status: {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def test_register():
    """Test user registration"""
    print("\n🔍 Testing: User Registration")
    email = f"e2e+{int(time.time())}@example.com"
    password = f"Test1234!{uuid.uuid4().hex[:4]}"
    
    print(f"   Email: {email}")
    
    try:
        resp = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if resp.status_code in [200, 201]:
            print(f"   ✅ PASS - Status: {resp.status_code}")
            data = resp.json()
            print(f"   User ID: {data.get('id') or data.get('user_id')}")
            return True, email, password
        else:
            print(f"   ❌ FAIL - Status: {resp.status_code}")
            print(f"   Response: {resp.text[:200]}")
            return False, None, None
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False, None, None

def test_login(email, password):
    """Test user login"""
    print("\n🔍 Testing: User Login")
    print(f"   Email: {email}")
    
    try:
        resp = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            token = data.get('access_token') or data.get('token')
            if token:
                print(f"   ✅ PASS - Got access token")
                print(f"   Token preview: {token[:20]}...")
                return True, token
            else:
                print(f"   ⚠️  PASS but no token found")
                print(f"   Response: {data}")
                return True, None
        else:
            print(f"   ❌ FAIL - Status: {resp.status_code}")
            print(f"   Response: {resp.text[:200]}")
            return False, None
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False, None

def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing: Root Endpoint")
    try:
        resp = requests.get(f"{BACKEND_URL}/", timeout=10)
        if resp.status_code == 200:
            print(f"   ✅ PASS - Status: {resp.status_code}")
            print(f"   Response: {resp.json()}")
            return True
        else:
            print(f"   ❌ FAIL - Status: {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 CreditSphere E2E API Tests")
    print("=" * 60)
    print(f"Backend: {BACKEND_URL}")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "backend_url": BACKEND_URL,
        "started_at": time.time(),
        "tests": []
    }
    
    # Test 1: Root
    success = test_root()
    results["tests"].append({"name": "Root Endpoint", "pass": success})
    
    # Test 2: Health
    success = test_health()
    results["tests"].append({"name": "Health Check", "pass": success})
    
    # Test 3: Register
    success, email, password = test_register()
    results["tests"].append({"name": "User Registration", "pass": success})
    
    # Test 4: Login (only if register succeeded)
    if success and email and password:
        success, token = test_login(email, password)
        results["tests"].append({"name": "User Login", "pass": success})
    else:
        print("\n⏭️  Skipping login test (registration failed)")
        results["tests"].append({"name": "User Login", "pass": None, "skipped": True})
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for t in results["tests"] if t["pass"] is True)
    failed = sum(1 for t in results["tests"] if t["pass"] is False)
    skipped = sum(1 for t in results["tests"] if t.get("skipped"))
    total = len(results["tests"])
    
    print(f"✅ Passed:  {passed}/{total}")
    print(f"❌ Failed:  {failed}/{total}")
    print(f"⏭️  Skipped: {skipped}/{total}")
    
    results["finished_at"] = time.time()
    results["summary"] = {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "total": total
    }
    
    # Save results
    with open("e2e_api_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: e2e_api_report.json")
    
    if failed == 0 and passed > 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
