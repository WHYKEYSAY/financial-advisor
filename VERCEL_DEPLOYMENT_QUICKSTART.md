# ⚡ Vercel Deployment - Quick Start Guide

## 🎯 5-Minute Deployment

### Step 1: Visit Vercel (2 min)
1. Go to: **https://vercel.com**
2. Click "Sign Up" or "Login" with GitHub
3. Authorize Vercel to access your GitHub account

### Step 2: Import Project (1 min)
1. Click **"Add New..."** → **"Project"**
2. Find and select: **`whyke/financial-advisor`**
3. Click **"Import"**

### Step 3: Configure (1 min)
**⚠️ CRITICAL SETTINGS:**

```
Root Directory: frontend    ← MUST SET THIS!
Framework: Next.js          ← Auto-detected
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

**Environment Variables:**
```
NEXT_PUBLIC_BACKEND_URL = [Leave blank for now]
```
> Will be updated after backend deployment

### Step 4: Deploy (1 min)
1. Click **"Deploy"**
2. Wait for build (~2-3 minutes)
3. 🎉 **Copy your deployment URL!**

---

## ✅ Post-Deployment Checklist

After deployment completes:

- [ ] Visit your Vercel URL
- [ ] Verify homepage loads
- [ ] Check login page works
- [ ] No 404 errors
- [ ] Save deployment URL for backend configuration

---

## 🔗 Your Deployment URLs

**Frontend URL:** `https://your-project-name.vercel.app`

**Common Routes:**
- Homepage: `/`
- Login: `/login`
- Register: `/register`
- Dashboard: `/dashboard`

---

## 🚨 Common Issues & Fixes

### Issue: "No Framework Detected"
**Fix:** Set Root Directory to `frontend`

### Issue: Build Fails with Module Error
**Fix:** Dependencies will be installed automatically, wait for build

### Issue: Page Shows 404
**Fix:** Check that Root Directory is set to `frontend`

---

## 📞 Next Steps

1. ✅ Save your Vercel URL
2. ⏭️ Proceed to Window 8: Backend Deployment
3. 🔄 Update NEXT_PUBLIC_BACKEND_URL after backend is live
4. ✨ Redeploy to connect frontend to backend

---

## 🎓 Detailed Guide

For comprehensive instructions, see: **DEPLOYMENT.md**

---

**Status:** Ready to Deploy
**Estimated Time:** 5 minutes
**Difficulty:** Easy 🟢
