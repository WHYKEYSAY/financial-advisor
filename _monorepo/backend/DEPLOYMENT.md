# Backend Deployment Guide - Railway

## 🚀 Quick Start

### Prerequisites
- GitHub account
- Railway account (https://railway.app)
- OpenAI API key

### Step 1: Generate Secret Keys

Run these commands to generate secure keys:

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY
openssl rand -hex 32
```

Save these keys for the next step.

### Step 2: Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your `financial-advisor` repository
4. Railway will detect the Dockerfile automatically

### Step 3: Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically create a `DATABASE_URL` variable

### Step 4: Add Redis

1. Click "New Service" again
2. Select "Database" → "Add Redis"
3. Railway will automatically create a `REDIS_URL` variable

### Step 5: Configure Environment Variables

Go to your backend service → "Variables" tab and add:

**Required Variables:**
```
APP_ENV=production
LOG_LEVEL=INFO
TZ=UTC

SECRET_KEY=<your-generated-secret-key>
ENCRYPTION_KEY=<your-generated-encryption-key>

JWT_ALG=HS256
JWT_ACCESS_TTL_MIN=10080
JWT_REFRESH_TTL_DAYS=14

BACKEND_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
FRONTEND_URL=https://financial-advisor-rust.vercel.app
BACKEND_CORS_ORIGINS=https://financial-advisor-rust.vercel.app,http://localhost:3000

OPENAI_API_KEY=<your-openai-api-key>
OPENAI_MODEL=gpt-4o-mini

FILE_STORAGE_DIR=/data/uploads
MAX_FILE_SIZE_MB=25

RATE_LIMIT_FREE=60/minute
RATE_LIMIT_OPTIMIZER=240/minute
RATE_LIMIT_AUTOPILOT=600/minute

AI_QUOTA_FREE=100
AI_QUOTA_OPTIMIZER=1000
AI_QUOTA_AUTOPILOT=3000
```

**Optional Variables (for later):**
```
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
PLAID_CLIENT_ID=
PLAID_SECRET=
PLAID_ENV=sandbox
SENTRY_DSN=
```

### Step 6: Set Root Directory

1. Go to "Settings" tab
2. Under "Build & Deploy" → "Root Directory"
3. Set to: `_monorepo/backend`

### Step 7: Deploy

1. Click "Deploy" or push to GitHub
2. Railway will build and deploy automatically
3. Once deployed, copy your backend URL (e.g., `https://xxx.up.railway.app`)

### Step 8: Update Frontend

Go to Vercel dashboard → Your project → Settings → Environment Variables

Add:
```
NEXT_PUBLIC_BACKEND_URL=<your-railway-backend-url>
```

Then redeploy the frontend.

### Step 9: Run Database Migrations

In Railway dashboard, go to your backend service and open the "Deploy Logs".

You may need to run migrations manually using Railway's CLI or add a startup script.

## 🔍 Troubleshooting

### Check Logs
- Go to your backend service in Railway
- Click "Deployments" → Latest deployment → "View Logs"

### Common Issues

1. **Database connection failed**
   - Ensure PostgreSQL service is running
   - Check `DATABASE_URL` is correctly set

2. **CORS errors**
   - Verify `BACKEND_CORS_ORIGINS` includes your Vercel URL
   - Check `FRONTEND_URL` matches your Vercel deployment

3. **Missing environment variables**
   - Review all required variables from `.env.example`
   - Ensure no typos in variable names

## 📊 Monitoring

- Railway provides automatic metrics and logs
- Check the "Metrics" tab for resource usage
- View "Logs" tab for application logs

## 💰 Cost Estimation

Railway free tier includes:
- $5 credit/month
- Suitable for development and small projects
- Backend + PostgreSQL + Redis ≈ $3-5/month

For production, consider upgrading to the Developer plan ($5/month + usage).
