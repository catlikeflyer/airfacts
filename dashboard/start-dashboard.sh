#!/bin/bash

# Quick start script for Airfacts Dashboard

set -e

echo "🎨 Airfacts Dashboard - Quick Start"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the dashboard directory"
    echo "   cd dashboard && ./start-dashboard.sh"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check for Streamlit
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Streamlit is installed"
fi

echo ""

# Check if Neo4j is running
echo "🔍 Checking Neo4j connection..."

if command -v docker &> /dev/null; then
    if docker ps | grep -q neo4j; then
        echo "✓ Neo4j container is running"
    else
        echo "⚠️  Neo4j container is not running"
        echo "   Start it with: docker start neo4j"
        echo "   Or from project root: make start-neo4j"
        echo ""
        read -p "Continue anyway? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⚠️  Docker not found. Make sure Neo4j is running manually."
fi

echo ""
echo "🚀 Starting Streamlit dashboard..."
echo ""
echo "   Dashboard will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

streamlit run app.py
