#!/bin/bash

# Deployment Preparation Script for Airfacts
# This script helps you prepare for deployment to free hosting services

set -e

echo "🚀 Airfacts Deployment Preparation"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "../requirements-minimal.txt" ]; then
    echo "❌ Error: Please run this script from the deployment directory"
    echo "💡 Usage: cd deployment && ./deploy-prep.sh"
    exit 1
fi

# Change to project root
cd ..

echo "📋 Pre-deployment Checklist:"
echo ""

# 1. Check if data is loaded
echo "1️⃣  Checking database connection..."
if python3 database/check_connection.py > /dev/null 2>&1; then
    echo "   ✅ Database connected and has data"
else
    echo "   ⚠️  Database connection failed or no data"
    read -p "   Load data now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Loading data from OpenFlights..."
        cd database
        python3 loader.py
        cd ..
        echo "   ✅ Data loaded"
    fi
fi

# 2. Check if .env is configured
echo ""
echo "2️⃣  Checking environment configuration..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
    if grep -q "neo4j+s://" .env; then
        echo "   ✅ Using Neo4j AuraDB (cloud database)"
    elif grep -q "bolt://localhost" .env; then
        echo "   ⚠️  Warning: Using localhost database"
        echo "   💡 For production, consider using Neo4j AuraDB"
    fi
else
    echo "   ⚠️  No .env file found"
    read -p "   Create from .env.example? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "   ✅ Created .env from .env.example"
        echo "   ⚠️  Please edit .env with your credentials"
    fi
fi

# 3. Check if code is committed
echo ""
echo "3️⃣  Checking Git status..."
if [ -d ".git" ]; then
    if [[ -n $(git status -s) ]]; then
        echo "   ⚠️  You have uncommitted changes"
        echo "   📝 Files to commit:"
        git status -s
        echo ""
        read -p "   Commit changes now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            read -p "   Enter commit message: " commit_msg
            git commit -m "$commit_msg"
            echo "   ✅ Changes committed"
        fi
    else
        echo "   ✅ All changes committed"
    fi
    
    # Check if we need to push
    if [[ -n $(git log origin/main..HEAD 2>/dev/null) ]]; then
        echo "   ⚠️  You have unpushed commits"
        read -p "   Push to GitHub now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push
            echo "   ✅ Changes pushed to GitHub"
        fi
    else
        echo "   ✅ All commits pushed"
    fi
else
    echo "   ⚠️  Not a Git repository"
fi

# 4. Test API locally
echo ""
echo "4️⃣  Testing API locally..."
echo "   Starting API server (will run for 5 seconds)..."
cd api
timeout 5s uvicorn main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
API_PID=$!
sleep 2

if curl -s http://localhost:8000/ > /dev/null; then
    echo "   ✅ API starts successfully"
else
    echo "   ⚠️  API failed to start"
fi

kill $API_PID 2>/dev/null || true
cd ..

# 5. Summary
echo ""
echo "======================================"
echo "✨ Deployment Options:"
echo "======================================"
echo ""
echo "🔥 EASIEST (Recommended for beginners):"
echo "   1. Render.com - Deploy API (uses render.yaml)"
echo "   2. Streamlit Cloud - Deploy Dashboard"
echo "   👉 See deployment/DEPLOYMENT.md for step-by-step"
echo ""
echo "⚡ BEST PERFORMANCE:"
echo "   1. Railway.app - Deploy API (uses railway.json)"
echo "   2. Streamlit Cloud - Deploy Dashboard"
echo ""
echo "🌍 GLOBAL DEPLOYMENT:"
echo "   1. Fly.io - Deploy API (uses Dockerfile)"
echo "   2. Streamlit Cloud - Deploy Dashboard"
echo ""
echo "======================================"
echo "📚 Next Steps:"
echo "======================================"
echo ""
echo "1. Read the full guide:"
echo "   open deployment/DEPLOYMENT.md"
echo ""
echo "2. Choose your hosting platform"
echo ""
echo "3. Set these environment variables on your platform:"
echo "   NEO4J_URI=<your-auradb-uri>"
echo "   NEO4J_USERNAME=neo4j"
echo "   NEO4J_PASSWORD=<your-password>"
echo ""
echo "4. Deploy and test!"
echo ""
echo "Need help? Check deployment/DEPLOYMENT.md or open an issue on GitHub"
echo ""
