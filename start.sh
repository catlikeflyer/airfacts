#!/bin/bash

# Airfacts API - Quick Start Script
# This script helps you set up and run the Airfacts API locally

set -e  # Exit on error

echo "🛫 Airfacts API - Quick Start"
echo "=============================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed. You'll need to set up Neo4j manually."
    echo "   Visit: https://neo4j.com/download/"
else
    echo "✓ Docker found: $(docker --version)"
fi

echo ""

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements-minimal.txt
echo "✓ Dependencies installed"

echo ""

# Check if Neo4j is running
if command -v docker &> /dev/null; then
    if docker ps | grep -q neo4j; then
        echo "✓ Neo4j container is already running"
    else
        echo "🐳 Starting Neo4j container..."
        docker run --name neo4j \
            -p 7474:7474 -p 7687:7687 \
            -d \
            -v $HOME/neo4j/data:/data \
            -v $HOME/neo4j/logs:/logs \
            -v $HOME/neo4j/import:/var/lib/neo4j/import \
            -v $HOME/neo4j/plugins:/plugins \
            --env NEO4J_AUTH=neo4j/airfacts-pw \
            neo4j:latest 2>/dev/null || echo "⚠️  Container 'neo4j' already exists. Remove it with: docker rm neo4j"
        
        echo "⏳ Waiting for Neo4j to start (30 seconds)..."
        sleep 30
        echo "✓ Neo4j is ready"
    fi
fi

echo ""

# Load data
read -p "📊 Do you want to load data from OpenFlights? (This may take a few minutes) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📥 Loading data from OpenFlights..."
    cd neo4j
    python3 loader.py
    cd ..
    echo "✓ Data loaded successfully"
fi

echo ""
echo "🚀 Starting API server..."
echo ""
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Neo4j: http://localhost:7474"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
