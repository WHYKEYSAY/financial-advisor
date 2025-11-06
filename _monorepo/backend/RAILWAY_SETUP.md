# 🚀 Railway Backend Deployment - Quick Setup

## ✅ Pre-generated Secrets (SAVE THESE SECURELY!)

```
SECRET_KEY=Fl503xEsJCVheA5cJ2yi2vtuljeFolrz4VuZq6PafIU
ENCRYPTION_KEY=pjkB0zll5e31X2mAH23Gkbg-UHSEzJEkER8YD0y5-r0=
```

⚠️ **IMPORTANT**: Save these keys in a password manager. Don't share them publicly!

---

## 📋 Deployment Checklist

### 1️⃣ Create Railway Account
- [ ] Go to https://railway.app
- [ ] Sign up with GitHub
- [ ] Verify your account

### 2️⃣ Create New Project
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose `financial-advisor` repository
- [ ] Set **Root Directory** to: `_monorepo/backend`

### 3️⃣ Add Database Services

**Add PostgreSQL:**
- [ ] Click "New Service" → "Database" → "Add PostgreSQL"
- [ ] Wait for it to provision

**Add Redis:**
- [ ] Click "New Service" → "Database" → "Add Redis"
- [ ] Wait for it to provision

### 4️⃣ Configure Environment Variables

Go to your backend service → **Variables** tab → Click "RAW Editor" and paste:

```bash
# Security (Use the generated keys above!)
SECRET_KEY=Fl503xEsJCVheA5cJ2yi2vtuljeFolrz4VuZq6PafIU
ENCRYPTION_KEY=pjkB0zll5e31X2mAH23Gkbg-UHSEzJEkER8YD0y5-r0=
JWT_ALG=HS256
JWT_ACCESS_TTL_MIN=10080
JWT_REFRESH_TTL_DAYS=14

# Application
APP_ENV=production
LOG_LEVEL=INFO
TZ=UTC

# Database (Railway auto-fills these)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# URLs
BACKEND_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
FRONTEND_URL=https://financial-advisor-rust.vercel.app
BACKEND_CORS_ORIGINS=https://financial-advisor-rust.vercel.app,http://localhost:3000

# OpenAI (REQUIRED - Add your key!)
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
OPENAI_MODEL=gpt-4o-mini

# File Storage
FILE_STORAGE_DIR=/data/uploads
MAX_FILE_SIZE_MB=25

# Rate Limiting
RATE_LIMIT_FREE=60/minute
RATE_LIMIT_OPTIMIZER=240/minute
RATE_LIMIT_AUTOPILOT=600/minute

# AI Quotas
AI_QUOTA_FREE=100
AI_QUOTA_OPTIMIZER=1000
AI_QUOTA_AUTOPILOT=3000
```

**Don't forget to replace:**
- `YOUR_OPENAI_API_KEY_HERE` with your actual OpenAI API key

### 5️⃣ Deploy Backend
- [ ] Click "Deploy" button
- [ ] Wait for build to complete (5-10 minutes)
- [ ] Check deployment logs for errors
- [ ] Copy your backend URL (e.g., `https://financial-advisor-production-xxx.up.railway.app`)

### 6️⃣ Update Frontend on Vercel
- [ ] Go to https://vercel.com/dashboard
- [ ] Select your `financial-advisor` project
- [ ] Go to **Settings** → **Environment Variables**
- [ ] Add new variable:
  - Name: `NEXT_PUBLIC_BACKEND_URL`
  - Value: `<your-railway-backend-url>` (from step 5)
- [ ] Click "Save"
- [ ] Go to **Deployments** tab
- [ ] Click "..." on latest deployment → "Redeploy"

### 7️⃣ Test the Connection
- [ ] Visit: `https://financial-advisor-rust.vercel.app`
- [ ] Open browser DevTools (F12) → Console
- [ ] Try registering a new account
- [ ] Check if API calls work

---

## 🔍 Verification Steps

### Check Backend Health
Visit: `https://<your-railway-url>/health`

Should return:
```json
{"status": "ok"}
```

### Check API Docs (Development mode only)
Visit: `https://<your-railway-url>/docs`

### View Logs
In Railway:
1. Go to your backend service
2. Click "Deployments"
3. Click on latest deployment
4. View logs

---

## 🐛 Troubleshooting

### Error: "Module not found"
- Check Root Directory is set to `_monorepo/backend`
- Verify all files are committed to GitHub

### Error: "Database connection failed"
- Ensure PostgreSQL service is healthy (green status)
- Check DATABASE_URL variable is properly set with `${{Postgres.DATABASE_URL}}`

### Error: "CORS policy"
- Verify BACKEND_CORS_ORIGINS includes your Vercel URL
- Make sure there are no trailing slashes in URLs

### Error: "Application failed to respond"
- Check deployment logs for Python errors
- Verify all required environment variables are set
- Ensure requirements.txt dependencies are compatible

---

## 💰 Cost Estimate

Railway charges:
- **$5 free credits/month** (enough for testing)
- Estimated usage: ~$3-5/month for backend + DB + Redis
- Consider upgrading to Developer plan ($5/month + usage) for production

---

## 📚 Next Steps

Once deployment is successful:

1. ✅ Set up database migrations (Alembic)
2. ✅ Configure monitoring (Sentry)
3. ✅ Set up Stripe for payments (optional)
4. ✅ Add Plaid for bank connections (optional)
5. ✅ Configure CI/CD for automatic deployments

---

## 🆘 Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check `DEPLOYMENT.md` for detailed instructions
