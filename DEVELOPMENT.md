# CreditSphere - Development Guide

This document provides a comprehensive roadmap for completing the CreditSphere platform implementation.

## 📋 Implementation Status

### ✅ Completed
- [x] Project backup and cleanup
- [x] Docker Compose configuration
- [x] Backend scaffold (FastAPI structure)
- [x] Core configuration (Pydantic Settings)
- [x] Database setup (SQLAlchemy)
- [x] Security utilities (JWT, encryption)
- [x] Environment variables template
- [x] Comprehensive README

### 🔄 In Progress / Remaining

## Phase 1: Database & Models (Priority: HIGH)

### Task: Implement SQLAlchemy Models
**File:** `backend/app/models/models.py`

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    locale = Column(String(10), default="en")
    tier = Column(String(20), default="analyst")  # analyst, optimizer, autopilot
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    accounts = relationship("Account", back_populates="user")
    cards = relationship("Card", back_populates="user")
    statements = relationship("Statement", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    tags = relationship("Tag", back_populates="user")
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    quota = relationship("Quota", back_populates="user", uselist=False)

# Add remaining models: RefreshToken, Account, Card, Statement, Merchant, 
# Transaction, Tag, RewardRule, Subscription, Quota, PaymentPlan
```

### Task: Setup Alembic
**Commands:**
```powershell
docker compose run --rm backend alembic init alembic
# Edit alembic/env.py to import models
docker compose run --rm backend alembic revision --autogenerate -m "init schema"
docker compose run --rm backend alembic upgrade head
```

---

## Phase 2: Authentication & Authorization (Priority: HIGH)

### Task: Auth API Endpoints
**File:** `backend/app/api/auth.py`

Implement:
- `POST /auth/register` - User registration
- `POST /auth/login` - Login with JWT
- `POST /auth/refresh` - Token refresh
- `POST /auth/logout` - Logout & invalidate refresh token
- `GET /auth/me` - Get current user

**Features:**
- HTTPOnly cookies for web clients
- Bearer token support for mobile/API
- Password hashing with bcrypt
- Refresh token rotation

---

## Phase 3: File Upload & Statement Parsing (Priority: HIGH)

### Task: File Upload Endpoint
**File:** `backend/app/api/statements.py`

```python
@router.post("/upload")
async def upload_statement(
    file: UploadFile,
    user: User = Depends(get_current_user)
):
    # Validate file type and size
    # Save to storage
    # Create Statement record
    # Enqueue parsing task
    pass
```

### Task: Statement Parser Service
**File:** `backend/app/services/parser.py`

Implement parsers for:
1. **CSV** - pandas with column normalization
2. **PDF** - PyMuPDF with table extraction
3. **Image** - Tesseract OCR with preprocessing

---

## Phase 4: Merchant Normalization & Categorization (Priority: MEDIUM)

### Task: Create Merchant Aliases Database
**File:** `backend/app/data/merchant_aliases.json`

```json
{
  "AMZ Mktp": "Amazon",
  "AMZN Mktp": "Amazon",
  "LOBLAWS": "Loblaws",
  "TIM HORTONS": "Tim Hortons",
  "UBER EATS": "Uber Eats"
}
```

### Task: Categorization Service
**File:** `backend/app/services/categorization.py`

Two-tier approach:
1. Fuzzy matching with `rapidfuzz`
2. AI fallback with OpenAI (gpt-4o-mini)

Categories:
- groceries, dining, subscription, transport, rent, travel, utilities, pharmacy, gas, entertainment, other

---

## Phase 5: AI Integration (Priority: MEDIUM)

### Task: OpenAI Service
**File:** `backend/app/services/ai.py`

```python
async def classify_transaction(
    merchant: str,
    amount: float,
    locale: str = "en"
) -> dict:
    # Call OpenAI API
    # Cache result in Redis
    # Track usage in Quota
    pass
```

### Task: Quota Management
**File:** `backend/app/services/quota.py`

Track and enforce:
- Free: 100 AI calls/month
- Optimizer: 1,000 AI calls/month
- Autopilot: 3,000 AI calls/month

---

## Phase 6: Rewards Engine (Priority: MEDIUM)

### Task: Credit Card Database
**File:** `backend/app/data/cards.yaml`

```yaml
cards:
  - issuer: RBC
    product: ION+
    annual_fee: 0
    rewards:
      - category: all
        rate: 0.01  # 1%
    transfer_partners:
      - avion: 1
    tricks:
      - "Transfer ION+ points to Avion for flights at 1:1"

  - issuer: MBNA
    product: Rewards World Elite
    annual_fee: 89
    rewards:
      - category: groceries
        rate: 0.05  # 5%
    tricks:
      - "Use with Chexy to pay rent for 5% cashback"
```

### Task: Rewards Calculation Service
**File:** `backend/app/services/rewards.py`

Calculate Net Annual Value (NAV) for card combinations:
- Analyze user spending patterns
- Recommend optimal 1-3 card combos
- Include transfer partner optimizations
- Account for annual fees

---

## Phase 7: Virtual Credit Manager (Priority: HIGH)

### Task: Credit Utilization Algorithm
**File:** `backend/app/services/vcm.py`

```python
def distribute_spending(cards: List[Card], monthly_spend: float) -> dict:
    """
    Distribute spending across cards to maintain 10-30% utilization
    Target: 20% per card (ideal)
    """
    # Sort by credit limit descending
    # Allocate to maintain 20% utilization
    # Handle overflow to next cards
    # Return allocation plan
    pass
```

### Task: VCM API Endpoints
**File:** `backend/app/api/vcm.py`

- `GET /vcm/summary` - Combined credit limit & utilization
- `POST /vcm/plan` - Generate spending distribution plan
- `POST /vcm/autopilot` - Toggle auto-payment (Autopilot tier)
- `GET /vcm/schedule` - View scheduled payments

---

## Phase 8: Billing & Stripe Integration (Priority: HIGH)

### Task: Stripe Endpoints
**File:** `backend/app/api/billing.py`

```python
@router.post("/checkout")
async def create_checkout_session(
    price_id: str,
    user: User = Depends(get_current_user)
):
    # Create Stripe checkout session
    # Redirect to Stripe
    pass

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    # Handle subscription events
    # Update user tier
    # Reset quotas
    pass
```

**Webhook Events to Handle:**
- `checkout.session.completed`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`

---

## Phase 9: Frontend Bootstrap (Priority: HIGH)

### Task: Initialize Next.js Project
**Commands:**
```powershell
cd frontend
npm create next-app@latest . -- --ts --eslint --app --src-dir=false --tailwind --use-npm
npm i next-intl recharts ky js-cookie zustand next-themes
```

### Task: Configure Internationalization
**File:** `frontend/i18n.ts`

```typescript
import {getRequestConfig} from 'next-intl/server';

export default getRequestConfig(async ({locale}) => ({
  messages: (await import(`./locales/${locale}.json`)).default
}));
```

**Create locale files:**
- `frontend/locales/en.json`
- `frontend/locales/zh.json`

---

## Phase 10: Frontend Core Components (Priority: HIGH)

### Task: API Client
**File:** `frontend/lib/api.ts`

```typescript
import ky from 'ky';

const api = ky.create({
  prefixUrl: process.env.NEXT_PUBLIC_BACKEND_URL,
  credentials: 'include',
  hooks: {
    afterResponse: [
      async (request, options, response) => {
        if (response.status === 401) {
          // Try refresh token
        }
        return response;
      }
    ]
  }
});

export default api;
```

### Task: Layout & Navigation
**File:** `frontend/app/[locale]/layout.tsx`

Components needed:
- Header with locale switcher
- Theme toggle (dark mode)
- User menu
- Footer with links

---

## Phase 11: Frontend Pages (Priority: MEDIUM)

### Pages to Implement:

1. **Landing Page** - `app/[locale]/page.tsx`
   - Hero section with CTAs
   - Feature showcase
   - Pricing teaser
   - Social proof

2. **Pricing** - `app/[locale]/pricing/page.tsx`
   - Tier comparison table
   - Stripe checkout buttons
   - FAQ section

3. **Dashboard** - `app/[locale]/dashboard/page.tsx`
   - File upload widget
   - Recent statements
   - Spending charts (Recharts)
   - Transaction list

4. **Rewards** - `app/[locale]/rewards/page.tsx`
   - Spending analysis
   - Card recommendations
   - Hidden tricks tips

5. **VCM** - `app/[locale]/vcm/page.tsx`
   - Card list with utilization gauges
   - Spending distribution plan
   - Large purchase wizard

6. **Auth Pages**
   - `/login`
   - `/register`
   - `/account`

---

## Phase 12: Testing (Priority: MEDIUM)

### Backend Tests
**File:** `backend/tests/test_*.py`

```python
def test_parse_csv_statement():
    # Test CSV parser
    pass

def test_categorize_transaction():
    # Test categorization
    pass

def test_calculate_rewards():
    # Test rewards engine
    pass

def test_vcm_distribution():
    # Test credit utilization algorithm
    pass
```

### Frontend Tests
- Component tests with React Testing Library
- E2E tests with Playwright

---

## Phase 13: Deployment & DevOps (Priority: LOW)

### Task: GitHub Actions Workflow
**File:** `.github/workflows/ci.yml`

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run backend tests
        run: |
          cd backend
          pytest -v

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run frontend tests
        run: |
          cd frontend
          npm ci
          npm test
```

### Task: Production Docker Compose
**File:** `docker-compose.prod.yml`

Add:
- Caddy reverse proxy
- HTTPS configuration
- Production environment overrides

---

## Development Tips

### Running Locally
```powershell
# Start all services
docker compose up -d

# Watch backend logs
docker compose logs -f backend

# Watch frontend logs
docker compose logs -f frontend

# Run migrations
docker compose exec backend alembic upgrade head

# Access PostgreSQL
docker compose exec db psql -U app -d fin

# Access Redis
docker compose exec redis redis-cli
```

### Code Style
- Backend: Follow PEP 8, use `black` and `ruff`
- Frontend: Use ESLint and Prettier

### Git Workflow
```powershell
# Create feature branch
git checkout -b feature/statement-parser

# Make changes and commit
git add .
git commit -m "feat: add CSV statement parser"

# Push and create PR
git push origin feature/statement-parser
```

---

## Performance Optimization Checklist

- [ ] Enable orjson responses in FastAPI
- [ ] Add Redis caching for AI results
- [ ] Optimize SQL queries with indexes
- [ ] Use React Server Components
- [ ] Lazy load heavy components
- [ ] Optimize images (Next.js Image)
- [ ] Enable compression (gzip/brotli)
- [ ] Database connection pooling
- [ ] Rate limiting per tier

---

## Security Checklist

- [ ] HTTPS enforced in production
- [ ] HTTPOnly, Secure, SameSite cookies
- [ ] CORS allowlist configured
- [ ] Secrets rotated regularly
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitize inputs)
- [ ] CSRF protection
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] Encrypted sensitive data at rest

---

## Next Immediate Steps

1. **Implement database models** (models.py)
2. **Setup Alembic and run first migration**
3. **Create auth endpoints** (login, register, refresh)
4. **Build file upload endpoint**
5. **Implement CSV parser** as first parser type
6. **Create basic frontend with Next.js**
7. **Build login/register pages**
8. **Create dashboard with file upload UI**

---

## Resources

- FastAPI docs: https://fastapi.tiangolo.com/
- Next.js docs: https://nextjs.org/docs
- Stripe docs: https://stripe.com/docs
- OpenAI API: https://platform.openai.com/docs
- SQLAlchemy docs: https://docs.sqlalchemy.org/
- Recharts docs: https://recharts.org/

---

**Remember:** Build incrementally, test frequently, and prioritize core features first!
