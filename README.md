# CreditSphere

**Your AI Financial Co-Pilot** | **您的 AI 金融管家**

Automatically analyze spending, maximize credit card rewards, and optimize your credit health.

自动分析支出、最大化信用卡收益、智能优化信用健康。

---

## 🚀 Overview

CreditSphere is an AI-powered personal finance platform that helps users:

1. **Smart Dashboard** (Free) - Upload bank statements (PDF/CSV/Image), get AI-powered categorization, and visualize spending with interactive charts
2. **Rewards Maximization Engine** (Paid) - Discover optimal credit card combinations and hidden strategies to maximize rewards
3. **Virtual Credit Manager** (Paid) - Intelligently distribute spending across multiple cards to maintain optimal credit utilization (10-30%)

### Core Features

#### Free Tier - "The Analyst"
- ✅ Statement upload & parsing (PDF, CSV, images)
- ✅ AI-powered transaction categorization
- ✅ Spending visualization (pie charts, trends)
- ✅ Basic annual summaries
- ✅ Limited AI insights (100/month)

#### Paid Tier - "The Optimizer" ($9.99/month or $99/year)
- ✨ Everything in Analyst, plus:
- ✨ Rewards Maximization Engine
- ✨ Personalized credit card recommendations
- ✨ Hidden tricks & strategies (e.g., RBC ION+ → Avion transfers, MBNA WE + Chexy rent)
- ✨ Virtual Credit Manager manual guidance
- ✨ Deep AI analysis (1,000 calls/month)

#### Premium Tier - "The Autopilot" ($19.99/month or $199/year)
- 🚀 Everything in Optimizer, plus:
- 🚀 One-click automated payment distribution
- 🚀 Real-time credit health alerts
- 🚀 Advanced bank integrations
- 🚀 Unlimited AI insights (3,000 calls/month)

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI (Python 3.11) - High-performance async API
- PostgreSQL 16 - Relational database
- Redis 7 - Caching & rate limiting
- OpenAI GPT-4o-mini - AI categorization & insights
- Stripe - Payment processing
- PyMuPDF + Tesseract - PDF parsing & OCR

**Frontend:**
- Next.js 14 (App Router) - React framework with SSR/SSG
- Tailwind CSS - Utility-first styling
- Recharts - Data visualization
- next-intl - Internationalization (EN/中文)
- Zustand - State management

**Infrastructure:**
- Docker & Docker Compose - Containerization
- Alembic - Database migrations
- GitHub Actions - CI/CD

### Project Structure

```
financial-advisor/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, DB, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── workers/      # Background tasks
│   │   ├── data/         # Static data (cards.yaml, aliases)
│   │   └── main.py       # FastAPI app
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   │   └── [locale]/     # Internationalized routes
│   ├── components/       # Reusable UI components
│   ├── lib/              # Utilities & API client
│   ├── locales/          # i18n translations (en.json, zh.json)
│   ├── public/           # Static assets
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🛠️ Setup Instructions

### Prerequisites

- **Docker Desktop for Windows** (with WSL2)
- **Node.js 20 LTS**
- **Python 3.11+**
- **Git**
- **PowerShell 5+**

### Quick Start

1. **Clone & Navigate**
   ```powershell
   cd C:\Users\whyke\financial-advisor
   ```

2. **Configure Environment**
   ```powershell
   Copy-Item .env.example .env
   # Edit .env and set your actual keys:
   # - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
   # - ENCRYPTION_KEY (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
   # - OPENAI_API_KEY
   # - STRIPE_SECRET_KEY
   ```

3. **Build & Run**
   ```powershell
   docker compose build
   docker compose up -d
   ```

4. **Initialize Database**
   ```powershell
   docker compose exec backend alembic upgrade head
   ```

5. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## 📊 Database Models

### Core Entities

- **User** - Authentication & profile
- **Account** - Linked bank accounts
- **Card** - Credit cards with limits & terms
- **Statement** - Uploaded financial statements
- **Transaction** - Individual transactions
- **Merchant** - Normalized merchant names
- **Tag** - Custom user tags
- **Subscription** - Stripe billing
- **Quota** - AI usage tracking
- **RewardRule** - Credit card rewards database
- **PaymentPlan** - Automated payment schedules

---

## 🔐 Environment Variables

See `.env.example` for a complete list. Key variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | 32+ char random string |
| `ENCRYPTION_KEY` | Fernet key for sensitive data | 44-char base64 string |
| `DATABASE_URL` | PostgreSQL connection | `postgresql+psycopg2://...` |
| `REDIS_URL` | Redis connection | `redis://redis:6379/0` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_...` or `sk_live_...` |

---

## 🧪 Testing

**Backend:**
```powershell
docker compose exec backend pytest -v
```

**Frontend:**
```powershell
cd frontend
npm test
npm run test:e2e
```

---

## 🚢 Deployment

### Production Considerations

1. **HTTPS**: Use Caddy or nginx as reverse proxy
2. **Secrets**: Rotate `SECRET_KEY` and `ENCRYPTION_KEY`
3. **Database**: Use managed PostgreSQL (AWS RDS, Digital Ocean, etc.)
4. **Redis**: Use managed Redis or Redis Cloud
5. **File Storage**: Use S3-compatible object storage
6. **Monitoring**: Enable Sentry (`SENTRY_DSN`)
7. **Backups**: Automated database backups
8. **Rate Limiting**: Ensure Redis is properly configured

### Docker Compose Production

```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🌍 Internationalization

The app supports English (EN) and Simplified Chinese (ZH).

- Locale files: `frontend/locales/en.json` and `frontend/locales/zh.json`
- Route-based: `/en/...` and `/zh/...`
- Cookie persistence: User preference saved

---

## 📝 API Endpoints

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh token
- `GET /auth/me` - Current user

### Statements & Transactions
- `POST /statements/upload` - Upload statement
- `GET /statements` - List statements
- `GET /transactions` - List transactions

### Rewards & VCM
- `GET /rewards/recommendations` - Card recommendations
- `GET /vcm/summary` - Credit utilization summary
- `POST /vcm/plan` - Generate payment plan

### Billing
- `POST /billing/checkout` - Create Stripe checkout
- `GET /billing/portal` - Billing portal
- `POST /webhooks/stripe` - Stripe webhooks

---

## 💳 Credit Card Data

Canadian & US cards are seeded in `backend/app/data/cards.yaml`:

- RBC ION+, Avion
- MBNA Rewards World Elite
- Amex Cobalt, Gold
- Scotiabank Gold Amex
- TD Cash Back
- BMO CashBack

Update this file to add new cards or modify rewards structures.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 🐛 Troubleshooting

### Backend won't start
- Check Docker logs: `docker compose logs backend`
- Verify `.env` has all required variables
- Ensure DATABASE_URL and REDIS_URL are correct

### Frontend build fails
- Clear Next.js cache: `rm -rf frontend/.next`
- Reinstall dependencies: `cd frontend && npm ci`

### Database migrations fail
- Reset database: `docker compose down -v && docker compose up -d`
- Re-run migrations: `docker compose exec backend alembic upgrade head`

### OCR not working
- Verify Tesseract is installed in Docker container
- Check language packs: `tesseract-ocr-eng`, `tesseract-ocr-chi-sim`

---

## 📞 Support

For issues or questions, please open a GitHub issue or contact support.

---

**Built with ❤️ for smarter financial management**
