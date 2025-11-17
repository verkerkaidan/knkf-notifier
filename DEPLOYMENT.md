# 🚀 Production Deployment Guide

## Overview

Your app has **2 parts** that need hosting:
1. **Frontend** (Next.js) → Deploy to Vercel
2. **Backend** (Python) → Deploy to Railway/Render/Fly.io

## Architecture

```
┌─────────────────┐      HTTPS      ┌──────────────────┐
│    Frontend     │─────────────────▶│     Backend      │
│  (Next.js)      │   API Requests   │   (FastAPI)      │
│  Vercel/Netlify │                  │  Railway/Render  │
└─────────────────┘                  └──────────────────┘
                                             │
                                             ▼
                                      ┌──────────────┐
                                      │   Database   │
                                      │  (Supabase)  │
                                      └──────────────┘
```

## Option 1: Separate Deployment (Recommended) ⭐

### Step 1: Deploy Backend (Python API)

#### A. Using Railway (Easiest)

1. **Create Account**: https://railway.app
2. **New Project** → **Deploy from GitHub**
3. **Select Repository**: `knkf-backend` folder
4. **Set Environment Variables**:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   API_KEY=generate_secure_key_here
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```
5. **Deploy** → Railway auto-detects Python and uses `railway.toml`

#### B. Using Render.com

1. **Create Account**: https://render.com
2. **New Web Service** → **Connect GitHub**
3. **Configure**:
   - **Build Command**: `pip install -r requirements-api.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
4. **Set Environment Variables** (same as above)
5. **Deploy**

#### C. Using Fly.io

```bash
cd knkf-backend
fly launch
fly secrets set SUPABASE_URL=xxx SUPABASE_KEY=xxx API_KEY=xxx
fly deploy
```

**Result**: You'll get a URL like `https://knkf-backend.railway.app`

### Step 2: Deploy Frontend (Next.js)

#### Using Vercel (Best for Next.js)

1. **Create Account**: https://vercel.com
2. **New Project** → **Import Git Repository**
3. **Select**: `knkf-frontend` folder
4. **Set Environment Variables**:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   NEXT_PUBLIC_BACKEND_URL=https://knkf-backend.railway.app
   NEXT_PUBLIC_SCRAPE_API_KEY=same_as_backend_api_key
   ```
5. **Deploy** → Automatic!

**Result**: You'll get a URL like `https://knkf-notifier.vercel.app`

### Step 3: Update CORS (Backend)

Update your backend's `ALLOWED_ORIGINS` env var:
```
ALLOWED_ORIGINS=https://knkf-notifier.vercel.app,https://knkf-notifier-*.vercel.app
```

### Step 4: Test

Visit your frontend → Click "🔄 Wedstrijden bijwerken" → Should work!

---

## Option 2: Cron Job (No Frontend Button)

Instead of on-demand scraping, run automatically on a schedule.

### Using GitHub Actions (Free)

```yaml
# .github/workflows/scrape.yml
name: Scrape Competitions

on:
  schedule:
    - cron: '0 9 * * *'  # Every day at 9 AM
  workflow_dispatch:  # Manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd knkf-backend
          pip install -r requirements.txt
      
      - name: Run scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: |
          cd knkf-backend
          python scraper.py --database --no-json
```

Then just deploy frontend to Vercel (no backend needed!)

---

## Option 3: All-in-One (Docker)

If you want everything in one place:

```dockerfile
# Dockerfile (root directory)
FROM nikolaik/python-nodejs:python3.9-nodejs20

WORKDIR /app

# Install Python dependencies
COPY knkf-backend/requirements-api.txt ./
RUN pip install -r requirements-api.txt

# Install Node dependencies
COPY knkf-frontend/package*.json ./frontend/
RUN cd frontend && npm install

# Copy files
COPY knkf-backend ./backend
COPY knkf-frontend ./frontend

# Build frontend
RUN cd frontend && npm run build

# Expose ports
EXPOSE 3000 8000

# Start both services
CMD python backend/api.py & cd frontend && npm start
```

Deploy to:
- **Railway**: Supports Dockerfile
- **Render**: Supports Dockerfile
- **Fly.io**: Supports Dockerfile
- **DigitalOcean App Platform**: Supports Dockerfile

---

## Cost Comparison

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| **Vercel** (Frontend) | Unlimited | Next.js apps ⭐ |
| **Railway** (Backend) | $5/month credit | Easy Python deployment |
| **Render** (Backend) | 750 hours/month | Free Python hosting |
| **Fly.io** (Backend) | 3 VMs free | Advanced users |
| **Supabase** (Database) | 500MB free | Existing setup ⭐ |
| **GitHub Actions** (Cron) | 2000 min/month | Scheduled tasks |

**Recommended Free Stack**:
- Frontend: Vercel (free)
- Backend: Render (free tier)
- Database: Supabase (free tier)
- Cron: GitHub Actions (optional)

---

## Environment Variables Summary

### Backend (.env):
```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
API_KEY=generate_with_openssl_rand_base64_32
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
PORT=8000  # Optional, platform provides this
```

### Frontend (.env.local):
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_BACKEND_URL=https://your-backend-domain.railway.app
NEXT_PUBLIC_SCRAPE_API_KEY=same_as_backend_api_key
```

---

## Quick Start (Recommended Path)

### 1. **Deploy Backend to Render** (5 minutes)
   - Sign up at render.com
   - "New Web Service" → Connect GitHub
   - Point to `knkf-backend` folder
   - Add environment variables
   - Deploy!

### 2. **Deploy Frontend to Vercel** (5 minutes)
   - Sign up at vercel.com
   - "New Project" → Connect GitHub
   - Point to `knkf-frontend` folder
   - Add environment variables (including backend URL)
   - Deploy!

### 3. **Test** (1 minute)
   - Visit your Vercel URL
   - Click the scrape button
   - Check Supabase for new data

**Total time: ~15 minutes** ⚡

---

## Troubleshooting

### Frontend can't reach backend
- Check `NEXT_PUBLIC_BACKEND_URL` is set correctly
- Check backend CORS allows frontend domain
- Check backend is actually running (visit `/health` endpoint)

### Backend can't scrape
- Check Python dependencies installed
- Check Supabase credentials are correct
- Check scraper can access KNKF website (firewall?)

### Rate limiting issues
- Increase `RATE_LIMIT_SECONDS` in `api.py`
- Or use cron job instead

---

## Next Steps

1. **Deploy backend** (Railway/Render)
2. **Deploy frontend** (Vercel)
3. **Test the connection**
4. **Set up monitoring** (optional)
5. **Add custom domain** (optional)

Need help with a specific platform? Let me know! 🚀
