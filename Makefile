.PHONY: help install setup start start-neo4j stop-neo4j load-data clean test dashboard install-dashboard

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements-minimal.txt

setup: ## Initial setup (create venv and install dependencies)
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements-minimal.txt
	@echo "✅ Setup complete! Activate venv with: source .venv/bin/activate"

start-neo4j: ## Start Neo4j container
	docker run --name neo4j \
		-p 7474:7474 -p 7687:7687 \
		-d \
		-v $$HOME/neo4j/data:/data \
		-v $$HOME/neo4j/logs:/logs \
		-v $$HOME/neo4j/import:/var/lib/neo4j/import \
		-v $$HOME/neo4j/plugins:/plugins \
		--env NEO4J_AUTH=neo4j/airfacts-pw \
		neo4j:latest
	@echo "⏳ Waiting for Neo4j to start..."
	@sleep 30
	@echo "✅ Neo4j started at http://localhost:7474"

stop-neo4j: ## Stop and remove Neo4j container
	docker stop neo4j || true
	docker rm neo4j || true
	@echo "✅ Neo4j stopped and removed"

load-data: ## Load data from OpenFlights into Neo4j
	cd database && python3 loader.py
	@echo "✅ Data loaded successfully"

start: ## Start the API server
	cd api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dashboard: ## Start the Streamlit dashboard
	cd dashboard && streamlit run app.py

install-dashboard: ## Install dashboard dependencies
	cd dashboard && pip install -r requirements.txt
	@echo "✅ Dashboard dependencies installed"

clean: ## Clean up Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✅ Cleaned up cache files"

test: ## Test API endpoints
	@echo "Testing API endpoints..."
	@curl -s http://localhost:8000/ | python3 -m json.tool
	@echo "\n✅ API is responding"

all: setup start-neo4j load-data ## Complete setup and start everything
	@echo "✅ All setup complete!"
	@echo "Run 'make start' to start the API server"
