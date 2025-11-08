# 🚀 Quick Deploy - Airfacts (100% Free)

## Fastest Path to Production

### Step 1: Database (Already Done! ✅)
You're using Neo4j AuraDB - perfect for free tier deployment.

**Load your data:**
```bash
cp .env.local .env
cd database
python3 loader.py
```

---

### Step 2: Deploy API to Render (5 minutes)

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. **Deploy on Render**:
   - Go to https://render.com and sign up with GitHub
   - Click **"New +"** → **"Blueprint"**
   - Select your **airfacts** repository
   - Render auto-detects `render.yaml`
   - Click **"Apply"**
   
3. **Set environment variables** in Render dashboard:
   ```
   NEO4J_URI = neo4j+s://c7717b3f.databases.neo4j.io
   NEO4J_USERNAME = neo4j
   NEO4J_PASSWORD = <your-auradb-password>
   ```

4. **Wait for deploy** (~3 minutes)

5. **Test your API**:
   ```bash
   curl https://airfacts-api.onrender.com/api/airports/JFK
   ```

---

### Step 3: Deploy Dashboard to Streamlit Cloud (3 minutes)

1. **Go to Streamlit Cloud**:
   - Visit https://share.streamlit.io
   - Sign in with GitHub

2. **Create new app**:
   - Click **"New app"**
   - Repository: `catlikeflyer/airfacts`
   - Branch: `main`
   - Main file path: `dashboard/app.py`

3. **Add secrets** (click "Advanced settings"):
   ```toml
   NEO4J_URI = "neo4j+s://c7717b3f.databases.neo4j.io"
   NEO4J_USERNAME = "neo4j"
   NEO4J_PASSWORD = "<your-auradb-password>"
   ```

4. **Click "Deploy!"**

5. **Access your dashboard**:
   - URL: `https://<your-app-name>.streamlit.app`

---

### Step 4: Update CORS (1 minute)

Update `api/main.py` with your live URLs:

```python
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "https://airfacts.streamlit.app",  # Your Streamlit URL
    "https://airfacts-api.onrender.com",  # Your API URL
]
```

Push changes:
```bash
git add api/main.py
git commit -m "Update CORS for production"
git push
```

Render will auto-deploy the update!

---

## ✅ You're Live!

**API:** https://airfacts-api.onrender.com  
**Dashboard:** https://airfacts.streamlit.app  
**API Docs:** https://airfacts-api.onrender.com/docs

---

## 📊 What You Get (Free Tier)

| Component | Service | Free Limits |
|-----------|---------|-------------|
| Database | Neo4j AuraDB | 200k nodes, 400k relationships |
| API | Render | 750 hours/month, 512MB RAM |
| Dashboard | Streamlit Cloud | Unlimited apps, 1GB RAM |

**Limitations:**
- API sleeps after 15 min of inactivity (cold start ~30s)
- Dashboard may be rate-limited under heavy traffic
- Database limited to 200k nodes (enough for OpenFlights data)

---

## 🔧 Troubleshooting

**API won't start on Render:**
- Check build logs for errors
- Verify environment variables are set
- Make sure `requirements-minimal.txt` is in repo

**Dashboard can't connect:**
- Verify secrets are set in Streamlit Cloud
- Check Neo4j AuraDB is active
- Test database connection locally first

**Cold starts too slow:**
- Upgrade to Render paid tier ($7/mo) for always-on
- Or use Railway which has better free tier performance

---

## 💰 Upgrade Options (Optional)

If you outgrow the free tier:

**Render Starter ($7/mo):**
- No cold starts
- Better performance
- Custom domain

**Railway ($5 credit/mo):**
- Pay only for what you use
- No cold starts on free tier
- Better performance than Render free

**Fly.io (mostly free):**
- 3 VMs free
- Global deployment
- Great performance

---

## 📚 Full Documentation

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Alternative hosting options (Railway, Fly.io)
- Custom domain setup
- Monitoring and analytics
- Advanced configurations

---

**Need help?** Open an issue on GitHub or check the main [README](../README.md)
