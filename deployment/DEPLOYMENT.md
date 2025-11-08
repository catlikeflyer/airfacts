# Deployment Guide - Free Tier Options

This guide shows you how to deploy Airfacts using free hosting services.

## 🎯 Architecture Overview

Your Airfacts deployment consists of three components:

1. **Neo4j Database** - Already using Neo4j AuraDB Free ✅
2. **FastAPI Backend** - Deploy to Render, Railway, or Fly.io
3. **Streamlit Dashboard** - Deploy to Streamlit Community Cloud

---

## 📊 Database: Neo4j AuraDB (Already Set Up!)

You're already using Neo4j AuraDB Free tier - perfect!

**Current Setup:**

- URI: `neo4j+s://c7717b3f.databases.neo4j.io`
- Free tier includes: 200k nodes, 400k relationships
- Always-on, managed service

**Load Your Data:**

```bash
# Make sure .env points to AuraDB
cp .env.local .env
cd database
python3 loader.py
```

---

## 🚀 Backend API: Multiple Free Options

### Option 1: Render (Recommended)

**Pros:** Easy setup, auto-deploy from GitHub, free SSL
**Cons:** Spins down after 15 min inactivity (cold starts)

**Free Tier:** 750 hours/month, 512 MB RAM

**Steps:**

1. **Prepare your repo:**

   The `render.yaml` file is already in the `deployment/` directory.

   ```yaml
   services:
     - type: web
       name: airfacts-api
       runtime: python
       buildCommand: "pip install -r requirements-minimal.txt"
       startCommand: "cd api && uvicorn main:app --host 0.0.0.0 --port $PORT"
       envVars:
         - key: NEO4J_URI
           value: neo4j+s://c7717b3f.databases.neo4j.io
         - key: NEO4J_USERNAME
           value: neo4j
         - key: NEO4J_PASSWORD
           sync: false # Will set in dashboard
   ```

2. **Deploy:**

   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New +" → "Blueprint"
   - Connect your `airfacts` repository
   - Render will detect `render.yaml` and create the service
   - Set `NEO4J_PASSWORD` in environment variables dashboard
   - Your API will be at: `https://airfacts-api.onrender.com`

3. **Test:**
   ```bash
   curl https://airfacts-api.onrender.com/api/airports/JFK
   ```

---

### Option 2: Railway

**Pros:** No cold starts on free tier, better performance
**Cons:** $5 credit/month (usually enough for API)

**Free Tier:** $5 credit/month (~500 hours)

**Steps:**

1. **Use the provided configuration:**

   The `railway.json` file is already in the `deployment/` directory.

2. **Deploy:**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variables:
     - `NEO4J_URI`: `neo4j+s://c7717b3f.databases.neo4j.io`
     - `NEO4J_USERNAME`: `neo4j`
     - `NEO4J_PASSWORD`: `your-password`
   - Railway auto-deploys on every push
   - Your API will be at: `https://airfacts-api.up.railway.app`

---

### Option 3: Fly.io

**Pros:** Global edge deployment, generous free tier
**Cons:** Requires Fly CLI

**Free Tier:** 3 shared VMs, 256MB RAM each

**Steps:**

1. **Install Fly CLI:**

   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**

   ```bash
   fly auth login
   ```

3. **Use the provided Dockerfile:**

   The `Dockerfile` is already in the `deployment/` directory.

4. **Deploy:**

   ```bash
   fly launch --no-deploy --dockerfile deployment/Dockerfile
   fly secrets set NEO4J_URI="neo4j+s://c7717b3f.databases.neo4j.io"
   fly secrets set NEO4J_USERNAME="neo4j"
   fly secrets set NEO4J_PASSWORD="your-password"
   fly deploy --dockerfile deployment/Dockerfile
   ```

   Your API will be at: `https://airfacts-api.fly.dev`

---

## 🎨 Dashboard: Streamlit Community Cloud

**Pros:** Made for Streamlit, very easy, unlimited apps
**Cons:** Public only, limited resources

**Free Tier:** Unlimited public apps, 1GB RAM

**Steps:**

1. **Prepare repository:**

   Ensure you have these files committed:

   - `dashboard/app.py` ✅
   - `dashboard/requirements.txt` ✅
   - `dashboard/database_connector.py` ✅
   - `dashboard/.streamlit/config.toml` ✅ (already configured)

2. **Deploy to Streamlit Cloud:**
   font = "sans serif"

   [server]
   headless = true
   port = 8501

   ```

   ```

3. **Deploy:**

   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Repository: `catlikeflyer/airfacts`
   - Branch: `main`
   - Main file path: `dashboard/app.py`
   - Click "Advanced settings"
   - Add secrets (format: TOML):
     ```toml
     NEO4J_URI = "neo4j+s://c7717b3f.databases.neo4j.io"
     NEO4J_USERNAME = "neo4j"
     NEO4J_PASSWORD = "your-password"
     ```
   - Click "Deploy!"

4. **Access:**
   - Your dashboard will be at: `https://airfacts.streamlit.app`

---

## 🔧 Configuration for Production

### Update API CORS Settings

Edit `api/main.py` to allow your dashboard domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(...)

origins = [
    "http://localhost:8501",
    "https://airfacts.streamlit.app",  # Your Streamlit domain
    "https://airfacts-api.onrender.com",  # Your API domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment-Specific Configuration

Create `.env.production`:

```bash
NEO4J_URI=neo4j+s://c7717b3f.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
API_URL=https://airfacts-api.onrender.com
```

---

## 📝 Quick Comparison

| Service             | Type      | Free Tier    | Cold Starts | Best For               |
| ------------------- | --------- | ------------ | ----------- | ---------------------- |
| **Neo4j AuraDB**    | Database  | 200k nodes   | None        | ✅ Already set up      |
| **Render**          | API       | 750h/mo      | Yes (15min) | Easiest setup          |
| **Railway**         | API       | $5/mo credit | No          | Best performance       |
| **Fly.io**          | API       | 3 VMs        | Minimal     | Global deployment      |
| **Streamlit Cloud** | Dashboard | Unlimited    | Minimal     | Perfect for dashboards |

---

## 🎯 Recommended Stack (100% Free)

For a completely free deployment:

1. **Database:** Neo4j AuraDB Free ✅ (already set up)
2. **API:** Render Free Tier (easiest)
3. **Dashboard:** Streamlit Community Cloud

**Total Cost:** $0/month  
**Setup Time:** ~30 minutes

---

## 🚦 Deployment Checklist

- [ ] Load data into Neo4j AuraDB
- [ ] Test database connection: `python3 database/check_connection.py`
- [ ] Push code to GitHub
- [ ] Deploy API to Render/Railway/Fly.io
- [ ] Set environment variables on hosting platform
- [ ] Test API endpoints
- [ ] Deploy dashboard to Streamlit Cloud
- [ ] Update CORS settings in API
- [ ] Test dashboard → API connection
- [ ] Update README with live URLs

---

## 🔍 Testing Your Deployment

After deploying, test all components:

```bash
# Test API
curl https://your-api-url.onrender.com/api/airports/JFK

# Test database from API
curl https://your-api-url.onrender.com/api/airlines/?limit=5

# Visit dashboard
open https://your-app.streamlit.app
```

---

## 📊 Monitoring & Logs

**Render:**

- View logs in Render Dashboard → Your Service → Logs
- Monitor usage in Dashboard

**Railway:**

- View logs in Railway Dashboard → Your Service → Deployments
- Track credit usage in Settings

**Streamlit:**

- View logs in Streamlit Cloud → Manage app → Logs
- Monitor app health in dashboard

---

## 🆘 Troubleshooting

### API won't start

- Check environment variables are set correctly
- Verify `requirements-minimal.txt` is in repo root
- Check build logs for errors

### Dashboard can't connect to database

- Verify secrets are set in Streamlit Cloud
- Check Neo4j AuraDB is active
- Test connection locally first

### Cold start issues (Render)

- Expected behavior on free tier
- Consider upgrading to paid tier ($7/mo) for always-on
- Or use Railway which has minimal cold starts

---

## 💡 Next Steps

1. **Custom Domain:** Add custom domain to Render/Streamlit (free)
2. **API Documentation:** Your FastAPI docs at `/docs` are auto-deployed
3. **Analytics:** Add Google Analytics to dashboard
4. **Monitoring:** Set up UptimeRobot for free monitoring

---

Need help? Check the [main README](../README.md) or open an issue!
