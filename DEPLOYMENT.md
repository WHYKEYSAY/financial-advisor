# 🚀 CreditSphere Deployment Guide

## Frontend Deployment to Vercel

### ✅ Prerequisites Checklist

- [x] Frontend code ready in `/frontend` directory
- [x] Next.js 15.5.6 configured
- [x] package.json with build scripts
- [x] vercel.json configuration files created
- [x] GitHub repository: `whyke/financial-advisor`

---

## 📦 Step 1: Prepare GitHub Repository

### Commit and Push Changes

```bash
cd C:\Users\whyke\financial-advisor

# Check status
git status

# Add all changes
git add .

# Commit
git commit -m "feat: Add Vercel deployment configuration"

# Push to GitHub
git push origin main
```

---

## 🌐 Step 2: Deploy to Vercel

### Option A: Vercel Dashboard (Recommended)

1. **Visit Vercel**
   - Go to: https://vercel.com
   - Sign in with GitHub account

2. **Import Project**
   - Click "Add New..." → "Project"
   - Select "Import Git Repository"
   - Choose: `whyke/financial-advisor`
   - Click "Import"

3. **Configure Project**
   
   **Framework Detection:**
   - Framework: `Next.js` (auto-detected)
   - Root Directory: `frontend` ⚠️ **IMPORTANT: Set this!**
   
   **Build & Output Settings:**
   - Build Command: `npm run build` (auto-filled)
   - Output Directory: `.next` (auto-filled)
   - Install Command: `npm install` (auto-filled)

4. **Environment Variables**
   
   Click "Environment Variables" and add:
   
   | Key | Value | Environment |
   |-----|-------|-------------|
   | `NEXT_PUBLIC_BACKEND_URL` | `https://your-backend-url.com` | Production |
   | `NEXT_PUBLIC_BACKEND_URL` | `http://localhost:8000` | Development |
   
   > **Note:** Leave blank initially, update after backend deployment (Window 8)

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (~2-3 minutes)
   - ✅ Get your deployment URL!

---

### Option B: Vercel CLI (Alternative)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy from frontend directory
cd frontend
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (Your account)
# - Link to existing project? No
# - Project name: creditsphere
# - Directory: ./
# - Want to modify settings? No

# Production deployment
vercel --prod
```

---

## 🔧 Step 3: Post-Deployment Configuration

### Update Environment Variables

After backend is deployed (Window 8):

1. Go to Vercel Dashboard → Your Project
2. Settings → Environment Variables
3. Edit `NEXT_PUBLIC_BACKEND_URL`
4. Set to: `https://your-backend-url.railway.app`
5. Click "Save"
6. Go to Deployments → Latest → "Redeploy"

---

## ✅ Step 4: Verification

### Test Deployment

Visit your Vercel URL and verify:

- [ ] Homepage loads correctly
- [ ] Login page accessible at `/login`
- [ ] Register page accessible at `/register`
- [ ] Dashboard accessible (after login)
- [ ] No console errors
- [ ] API calls work (after backend URL configured)

### Common URLs to Test

```
https://your-app.vercel.app/
https://your-app.vercel.app/login
https://your-app.vercel.app/register
https://your-app.vercel.app/dashboard
```

---

## 🎨 Step 5: Custom Domain (Optional)

### Add Custom Domain

1. Go to: Project Settings → Domains
2. Click "Add Domain"
3. Enter: `creditsphere.com` (or your domain)
4. Follow DNS configuration instructions
5. Wait for SSL certificate (automatic)

### DNS Configuration Example

```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

---

## 🔍 Troubleshooting

### Build Fails

**Issue:** `Error: Cannot find module 'next-intl'`

**Solution:**
```bash
cd frontend
npm install
git add package-lock.json
git commit -m "Update dependencies"
git push
```

### Root Directory Not Set

**Issue:** "No framework detected"

**Solution:**
- In Vercel dashboard
- Settings → General
- Root Directory: `frontend`
- Save & Redeploy

### Environment Variables Not Working

**Issue:** API calls fail with 404

**Solution:**
- Check variable name: `NEXT_PUBLIC_BACKEND_URL` (must start with `NEXT_PUBLIC_`)
- Redeploy after changing environment variables
- Hard refresh browser (Ctrl+F5)

---

## 📊 Deployment Checklist

### Pre-Deployment
- [x] Code committed to GitHub
- [x] vercel.json configured
- [x] package.json has correct scripts
- [x] next.config.ts has env config

### During Deployment
- [ ] Vercel project created
- [ ] Root directory set to `frontend`
- [ ] Framework detected as Next.js
- [ ] Build succeeds
- [ ] Deployment URL generated

### Post-Deployment
- [ ] Site loads correctly
- [ ] Environment variables configured
- [ ] Backend URL updated (after Window 8)
- [ ] All pages accessible
- [ ] No console errors
- [ ] Custom domain configured (optional)

---

## 🎯 Expected Results

### Deployment Info

```
✅ Production Deployment
URL: https://creditsphere-xyz.vercel.app
Status: Ready
Build Time: ~2-3 minutes
Region: Washington, D.C., USA (iad1)
```

### Build Output

```
> Building...
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages (7/7)
✓ Finalizing page optimization

Route (app)                              Size     First Load JS
┌ ○ /                                    5.2 kB          87 kB
├ ○ /login                               3.8 kB          85 kB
├ ○ /register                            4.1 kB          86 kB
└ ● /dashboard                           12 kB           94 kB

✓ Build completed successfully
```

---

## 🔗 Quick Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Vercel Docs:** https://vercel.com/docs
- **Next.js Deployment:** https://nextjs.org/docs/deployment
- **Project Repo:** https://github.com/whyke/financial-advisor

---

## 📞 Support

If you encounter issues:

1. Check Vercel build logs
2. Review `DEPLOYMENT.md` troubleshooting section
3. Verify all environment variables
4. Ensure backend is deployed and accessible

---

**Last Updated:** 2025-11-06
**Status:** Ready for Deployment
**Next Step:** Deploy backend to Railway (Window 8)
