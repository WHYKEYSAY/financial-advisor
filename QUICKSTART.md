# CreditSphere Quick Start Guide 🚀

## Current Status

✅ **Backend API**: Fully functional  
✅ **Database**: PostgreSQL with all migrations  
✅ **Authentication**: JWT with bcrypt working  
✅ **File Processing**: CSV/PDF/Image parsing  
✅ **AI Categorization**: OpenAI integration ready  
⚠️ **Frontend**: Has routing issues (known Next.js 15/16 + next-intl compatibility bug)

---

## Getting Started (5 minutes)

### 1. Start Services

```bash
cd C:\Users\whyke\financial-advisor
wsl bash -c "docker-compose up -d db redis backend"
```

Wait 10 seconds for services to initialize.

### 2. Run Migrations

```bash
wsl bash -c "docker-compose exec backend alembic upgrade head"
```

### 3. Access Swagger UI

Open in your browser: **http://localhost:8000/docs**

---

## Using the API (Interactive)

### Step 1: Register a User

1. Go to http://localhost:8000/docs
2. Click on **POST /auth/register**
3. Click "Try it out"
4. Use this request body:
   ```json
   {
     "email": "yourname@example.com",
     "password": "yourpassword123"
   }
   ```
5. Click "Execute"
6. **Copy the `access_token`** from the response

### Step 2: Authorize

1. Scroll to the top of the Swagger page
2. Click the green **"Authorize"** button (🔓)
3. Paste your `access_token` in the "Value" field
4. Click "Authorize"
5. Click "Close"

### Step 3: Upload a Statement

1. Find **POST /files/upload** endpoint
2. Click "Try it out"
3. Click "Choose File" and select `sample_statement.csv` (included in the repo)
4. Click "Execute"
5. Wait 3-5 seconds for processing

### Step 4: View Your Transactions

1. Find **GET /transactions** endpoint
2. Click "Try it out"
3. Click "Execute"
4. See all your categorized transactions!

### Step 5: Get Spending Breakdown

1. Find **GET /transactions/breakdown** endpoint
2. Click "Try it out"
3. Click "Execute"
4. See spending by category with percentages!

### Step 6: Check Your Statistics

1. Find **GET /transactions/stats** endpoint
2. Click "Try it out"
3. Click "Execute"
4. See total spent, average transaction, top merchant, etc.

---

## Sample Data

The repo includes `sample_statement.csv` with 14 transactions:
- Groceries (Loblaws, Metro, Costco)
- Dining (Starbucks, Tim Hortons, Uber Eats)
- Gas (Shell)
- Entertainment (Cineplex)
- Subscriptions (Netflix, Rogers)
- Pharmacy (Shoppers Drug Mart)
- Shopping (Amazon)

---

## Available Endpoints

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/login` - Get access token
- `GET /auth/me` - Get user info
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - Logout

### File Upload
- `POST /files/upload` - Upload statement (PDF/CSV/Image)
- `GET /files/statements` - List uploaded statements
- `GET /files/statements/{id}` - Get statement details
- `DELETE /files/statements/{id}` - Delete statement
- `POST /files/statements/{id}/reparse` - Re-parse statement

### Transactions
- `GET /transactions` - List transactions (with filters)
- `GET /transactions/breakdown` - Spending by category
- `GET /transactions/stats` - Statistics
- `POST /transactions/{id}/categorize` - Re-categorize

### Quota
- `GET /quota/status` - Check AI quota usage

---

## Categories

Transactions are automatically categorized into:
- `groceries` - Supermarkets
- `dining` - Restaurants, cafes
- `gas` - Gas stations
- `transport` - Uber, transit
- `entertainment` - Movies, events
- `subscription` - Netflix, Spotify, etc.
- `shopping` - General retail
- `pharmacy` - Drugstores
- `utilities` - Bills, internet
- `rent` - Rent payments
- `travel` - Hotels, flights
- `other` - Uncategorized

---

## Tiers & Quotas

### Analyst (Free - Default)
- 60 API requests/minute
- 100 AI categorization calls/month
- Basic features

### Optimizer ($9.99/month)
- 240 API requests/minute
- 1,000 AI calls/month
- Rewards engine access

### Autopilot ($19.99/month)
- 600 API requests/minute
- 3,000 AI calls/month
- Full automation

---

## Troubleshooting

### Services won't start
```bash
wsl bash -c "cd /mnt/c/Users/whyke/financial-advisor && docker-compose down -v && docker-compose up -d db redis backend"
```

### Database connection error
```bash
wsl bash -c "cd /mnt/c/Users/whyke/financial-advisor && docker-compose restart backend"
```

### Check service status
```bash
wsl bash -c "cd /mnt/c/Users/whyke/financial-advisor && docker-compose ps"
```

### View logs
```bash
wsl bash -c "cd /mnt/c/Users/whyke/financial-advisor && docker-compose logs backend"
```

---

## Next Steps

1. ✅ **Test with sample data** (included)
2. 📄 **Read full API docs**: See `API_GUIDE.md`
3. 💳 **Add real statements**: Upload your own CSV/PDF files
4. 🔧 **Customize categories**: Use re-categorization endpoint
5. 🚀 **Build your own client**: Use any HTTP client/language

---

## Project Structure

```
financial-advisor/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   └── schemas/     # Pydantic schemas
│   ├── alembic/         # Database migrations
│   └── requirements.txt
├── frontend/            # Next.js frontend (has routing issues)
├── docker-compose.yml   # Docker services
├── .env                 # Environment variables
├── API_GUIDE.md        # Full API documentation
├── QUICKSTART.md       # This file
├── sample_statement.csv # Test data
└── test_api.sh         # Automated test script
```

---

## Need Help?

- **API Docs**: http://localhost:8000/docs
- **Full Guide**: See `API_GUIDE.md`
- **Health Check**: http://localhost:8000/health

---

## What's Working

✅ User registration & authentication  
✅ JWT tokens with refresh  
✅ File upload (CSV, PDF, Image)  
✅ Automatic transaction parsing  
✅ AI-powered merchant categorization  
✅ Fuzzy matching for known merchants  
✅ Transaction filtering & search  
✅ Spending breakdowns  
✅ Statistics & analytics  
✅ Rate limiting by tier  
✅ Quota tracking  
✅ Multi-currency support  
✅ Duplicate detection  

The backend is production-ready! 🎉
