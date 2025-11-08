# Deploy to Streamlit Community Cloud - Step by Step

This guide walks you through deploying the Airfacts dashboard to Streamlit Community Cloud in just a few minutes.

## 📋 Prerequisites

- ✅ GitHub account
- ✅ Your code pushed to GitHub repository
- ✅ Neo4j AuraDB instance running (you have this!)

## 🚀 Deployment Steps

### Step 1: Push Your Code to GitHub

Make sure all your latest changes are committed and pushed:

```bash
cd /Users/dhnam/Desktop/Data/airfacts

# Check status
git status

# Add all changes
git add .

# Commit
git commit -m "Ready for Streamlit deployment"

# Push to GitHub
git push origin main
```

### Step 2: Go to Streamlit Community Cloud

1. Open your browser and go to: **https://share.streamlit.io**

2. Click **"Sign up"** or **"Sign in"** using your GitHub account

3. Authorize Streamlit to access your GitHub repositories

### Step 3: Deploy New App

1. Click the **"New app"** button (top right)

2. Fill in the deployment form:

   **Repository:**
   - Select: `catlikeflyer/airfacts`

   **Branch:**
   - Select: `main`

   **Main file path:**
   - Enter: `dashboard/app.py`

3. Click **"Advanced settings"** (before deploying)

### Step 4: Add Secrets (IMPORTANT!)

In the Advanced settings, you'll see a **"Secrets"** section. Add your Neo4j credentials in TOML format:

```toml
NEO4J_URI = "neo4j+s://6b229126.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "aW3Kaz_40eY1poKjblu4ecVawDQ3zc4ccQNjxa_SOGs"
```

**Important Notes:**
- ✅ Use the exact format above (TOML format)
- ✅ No quotes around the keys (left side)
- ✅ Use quotes around the values (right side)
- ✅ These secrets are encrypted and never exposed in logs

### Step 5: Deploy!

1. Click **"Deploy!"** button

2. Wait for deployment (usually 2-3 minutes)
   - You'll see the build logs
   - Dependencies will be installed
   - App will start automatically

3. Your dashboard will be live at:
   ```
   https://<your-app-name>.streamlit.app
   ```

## 🎨 Customize Your App (Optional)

### Change App Name

After deployment, you can customize:
1. Go to your app settings (⚙️ icon)
2. Click "Settings"
3. Change the app name/URL
4. Choose a custom subdomain

### Update App

Whenever you push changes to GitHub:
1. Streamlit will automatically redeploy
2. Or click "Reboot" in the app menu

## ✅ Verify Deployment

After deployment, test your dashboard:

1. **Home Page:** Should show database statistics
2. **Airport Search:** Try searching for "JFK"
3. **Route Explorer:** Try finding routes between airports
4. **Analytics:** Check the charts load properly

## 🔧 Troubleshooting

### App Won't Start

**Check build logs:**
- Click on "Manage app" → "Logs"
- Look for import errors or missing dependencies

**Common fixes:**
- Verify `dashboard/requirements.txt` includes all dependencies
- Make sure secrets are in correct TOML format
- Check file path is exactly `dashboard/app.py`
- **Python version errors:** The `.python-version` file pins to Python 3.11 (fixes pandas/numpy build issues)

### Can't Connect to Database

**Verify secrets:**
- Go to app settings → Secrets
- Make sure NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD are set
- Check for typos in the values

**Test connection:**
- Check if your AuraDB instance is running at: https://console.neo4j.io
- Verify the URI matches your AuraDB instance

### App is Slow

**Normal behavior:**
- First load may take 10-30 seconds (cold start)
- Subsequent loads are faster
- Free tier has resource limits

**If too slow:**
- Check Neo4j query performance
- Consider upgrading Streamlit plan for better resources

## 📊 What You Get (Free Tier)

✅ **Unlimited public apps**
✅ **1 GB RAM per app**
✅ **Community support**
✅ **Auto-deploy from GitHub**
✅ **Free SSL certificate**
✅ **Custom subdomain**

## 🔐 Security Notes

**Secrets are safe:**
- Environment variables are encrypted
- Never logged or exposed in UI
- Only accessible to your app runtime

**Making app private:**
- Free tier is public only
- For private apps, upgrade to Teams plan ($20/month)

## 📱 Sharing Your App

Once deployed, share your dashboard:

```
https://airfacts-dashboard.streamlit.app
```

Or add a custom domain (requires Teams plan).

## 🎯 Next Steps

After successful deployment:

1. **Add to README:** Link to your live dashboard
2. **Monitor usage:** Check Streamlit dashboard for metrics
3. **Gather feedback:** Share with users and iterate
4. **Scale if needed:** Upgrade plan if you need more resources

## 📚 Additional Resources

- **Streamlit Docs:** https://docs.streamlit.io/streamlit-community-cloud
- **Deploy Tutorial:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- **Secrets Management:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management

---

**Ready to deploy?** Just follow steps 1-5 above and you'll be live in minutes! 🚀
