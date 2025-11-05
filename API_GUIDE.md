# CreditSphere API Guide

## Base URL
```
http://localhost:8000
```

## Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Authentication

### 1. Register a New User
**Endpoint**: `POST /auth/register`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "your-password-123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "locale": "en",
    "tier": "analyst",
    "created_at": "2025-11-05T22:00:00"
  }
}
```

### 2. Login
**Endpoint**: `POST /auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "your-password-123"
}
```

**Response**: Same as register

### 3. Get Current User
**Endpoint**: `GET /auth/me`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "locale": "en",
  "tier": "analyst",
  "created_at": "2025-11-05T22:00:00"
}
```

### 4. Refresh Token
**Endpoint**: `POST /auth/refresh`

**Request Body**:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

### 5. Logout
**Endpoint**: `POST /auth/logout`

**Headers**:
```
Authorization: Bearer {access_token}
```

---

## File Upload & Statement Processing

### Upload Statement
**Endpoint**: `POST /files/upload`

**Headers**:
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request**:
- File: PDF, CSV, PNG, or JPG (max 25MB)

**cURL Example**:
```bash
curl -X POST http://localhost:8000/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/statement.csv"
```

**Response**:
```json
{
  "id": 1,
  "user_id": 1,
  "source_type": "csv",
  "file_path": "/data/uploads/user_1/statement_20251105.csv",
  "parsed": true,
  "period_start": "2025-10-01",
  "period_end": "2025-10-31",
  "created_at": "2025-11-05T22:00:00"
}
```

### List Statements
**Endpoint**: `GET /files/statements`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response**:
```json
[
  {
    "id": 1,
    "source_type": "csv",
    "file_path": "/data/uploads/user_1/statement.csv",
    "parsed": true,
    "period_start": "2025-10-01",
    "period_end": "2025-10-31",
    "created_at": "2025-11-05T22:00:00"
  }
]
```

---

## Transactions

### Get Transactions
**Endpoint**: `GET /transactions`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `page` (default: 1)
- `page_size` (default: 50, max: 200)
- `category` (optional): Filter by category
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD
- `search` (optional): Search merchant name

**Example**:
```
GET /transactions?category=groceries&page=1&page_size=20
```

**Response**:
```json
{
  "transactions": [
    {
      "id": 1,
      "date": "2025-10-15",
      "amount": -45.67,
      "currency": "CAD",
      "category": "groceries",
      "subcategory": "supermarket",
      "merchant_name": "Loblaws",
      "raw_merchant": "LOBLAWS #1234",
      "tags": ["weekly shopping"],
      "confidence": 95
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "pages": 8
}
```

### Get Spending Breakdown
**Endpoint**: `GET /transactions/breakdown`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `start_date` (optional): Defaults to 30 days ago
- `end_date` (optional): Defaults to today

**Response**:
```json
{
  "categories": [
    {
      "category": "groceries",
      "total": 456.78,
      "count": 12,
      "percentage": 35.5
    },
    {
      "category": "dining",
      "total": 234.50,
      "count": 8,
      "percentage": 18.2
    }
  ],
  "start_date": "2025-10-06",
  "end_date": "2025-11-05"
}
```

### Get Transaction Statistics
**Endpoint**: `GET /transactions/stats`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `start_date` (optional)
- `end_date` (optional)

**Response**:
```json
{
  "total_transactions": 150,
  "total_spent": 3456.78,
  "average_transaction": 23.04,
  "top_merchant": "Loblaws",
  "top_category": "groceries",
  "date_range": {
    "start": "2025-10-06",
    "end": "2025-11-05"
  }
}
```

### Recategorize Transaction
**Endpoint**: `POST /transactions/{id}/categorize`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response**:
```json
{
  "id": 1,
  "category": "groceries",
  "subcategory": "supermarket",
  "merchant_name": "Loblaws",
  "confidence": 95
}
```

---

## Quota Management

### Get Quota Status
**Endpoint**: `GET /quota/status`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response**:
```json
{
  "tier": "analyst",
  "ai_calls_limit": 100,
  "ai_calls_used": 15,
  "ai_calls_remaining": 85,
  "files_parsed": 3,
  "period_start": "2025-11-01",
  "period_end": "2025-11-30",
  "reset_in_days": 25
}
```

---

## Categories

Available categories:
- `groceries` - Supermarkets, grocery stores
- `dining` - Restaurants, cafes, food delivery
- `subscription` - Netflix, Spotify, etc.
- `transport` - Transit, Uber, gas
- `rent` - Rent payments
- `travel` - Hotels, flights
- `utilities` - Electricity, water, internet
- `pharmacy` - Drugstores, medications
- `gas` - Gas stations
- `entertainment` - Movies, events
- `shopping` - General retail
- `other` - Uncategorized

---

## Rate Limits

- **Analyst (Free)**: 60 requests/minute, 100 AI calls/month
- **Optimizer**: 240 requests/minute, 1000 AI calls/month  
- **Autopilot**: 600 requests/minute, 3000 AI calls/month

---

## Testing with cURL

### Complete Workflow Example:

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456"}'

# Save the access_token from response
TOKEN="your_access_token_here"

# 2. Upload a statement
curl -X POST http://localhost:8000/files/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@statement.csv"

# 3. View transactions
curl -X GET "http://localhost:8000/transactions?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"

# 4. Get spending breakdown
curl -X GET http://localhost:8000/transactions/breakdown \
  -H "Authorization: Bearer $TOKEN"

# 5. Get statistics
curl -X GET http://localhost:8000/transactions/stats \
  -H "Authorization: Bearer $TOKEN"

# 6. Check quota
curl -X GET http://localhost:8000/quota/status \
  -H "Authorization: Bearer $TOKEN"
```

---

## Sample CSV Format

Create a file `sample_statement.csv`:

```csv
Date,Description,Amount
2025-10-01,LOBLAWS #1234,,-45.67
2025-10-02,STARBUCKS COFFEE,-5.75
2025-10-03,SHELL GAS STATION,-60.00
2025-10-05,UBER TRIP,-15.50
2025-10-10,AMAZON.COM,-89.99
2025-10-15,NETFLIX SUBSCRIPTION,-16.99
2025-10-20,METRO GROCERY,-67.43
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (quota exceeded)
- `404` - Not Found
- `422` - Validation Error
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error

---

## Next Steps

1. **Test the API** using Swagger UI at http://localhost:8000/docs
2. **Upload sample data** to see categorization in action
3. **Check transaction breakdown** to visualize spending
4. **Monitor quota** usage for AI calls

The backend is fully functional and ready to use!
