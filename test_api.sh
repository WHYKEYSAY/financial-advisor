#!/bin/bash

# CreditSphere API Test Script
# This script demonstrates the complete workflow

BASE_URL="http://localhost:8000"
EMAIL="test$(date +%s)@example.com"
PASSWORD="test123456"

echo "🚀 CreditSphere API Test Workflow"
echo "=================================="
echo ""

# 1. Register
echo "1️⃣  Registering user: $EMAIL"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

TOKEN=$(echo $REGISTER_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Registration failed!"
  echo "Response: $REGISTER_RESPONSE"
  exit 1
fi

echo "✅ Registered successfully!"
echo "   Access Token: ${TOKEN:0:50}..."
echo ""

# 2. Get user info
echo "2️⃣  Fetching user info..."
USER_INFO=$(curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN")
echo "✅ User Info:"
echo "$USER_INFO" | python3 -m json.tool 2>/dev/null || echo "$USER_INFO"
echo ""

# 3. Check quota
echo "3️⃣  Checking quota status..."
QUOTA=$(curl -s -X GET "$BASE_URL/quota/status" \
  -H "Authorization: Bearer $TOKEN")
echo "✅ Quota Status:"
echo "$QUOTA" | python3 -m json.tool 2>/dev/null || echo "$QUOTA"
echo ""

# 4. Upload sample statement
echo "4️⃣  Uploading sample statement..."
if [ -f "sample_statement.csv" ]; then
  UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/files/upload" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@sample_statement.csv")
  echo "✅ Upload Response:"
  echo "$UPLOAD_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UPLOAD_RESPONSE"
  echo ""
  
  # Wait for processing
  echo "⏳ Waiting 3 seconds for transaction processing..."
  sleep 3
  echo ""
  
  # 5. Get transactions
  echo "5️⃣  Fetching transactions..."
  TRANSACTIONS=$(curl -s -X GET "$BASE_URL/transactions?page=1&page_size=5" \
    -H "Authorization: Bearer $TOKEN")
  echo "✅ Transactions:"
  echo "$TRANSACTIONS" | python3 -m json.tool 2>/dev/null || echo "$TRANSACTIONS"
  echo ""
  
  # 6. Get breakdown
  echo "6️⃣  Fetching spending breakdown..."
  BREAKDOWN=$(curl -s -X GET "$BASE_URL/transactions/breakdown" \
    -H "Authorization: Bearer $TOKEN")
  echo "✅ Spending Breakdown:"
  echo "$BREAKDOWN" | python3 -m json.tool 2>/dev/null || echo "$BREAKDOWN"
  echo ""
  
  # 7. Get stats
  echo "7️⃣  Fetching statistics..."
  STATS=$(curl -s -X GET "$BASE_URL/transactions/stats" \
    -H "Authorization: Bearer $TOKEN")
  echo "✅ Statistics:"
  echo "$STATS" | python3 -m json.tool 2>/dev/null || echo "$STATS"
  echo ""
else
  echo "⚠️  sample_statement.csv not found. Skipping file upload."
  echo ""
fi

echo "=================================="
echo "✅ Test completed successfully!"
echo ""
echo "💡 Your access token (save this for future requests):"
echo "$TOKEN"
echo ""
echo "🌐 Access Swagger UI at: http://localhost:8000/docs"
