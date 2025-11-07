# Troubleshooting Guide

## Common Issues and Solutions

### 1. Neo4j Connection Failed

**Error:** `ServiceUnavailable: Failed to establish connection`

**Solutions:**
- Ensure Neo4j is running: `docker ps | grep neo4j`
- Check if port 7687 is available: `lsof -i :7687`
- Verify credentials in your environment or code (username: `neo4j`, password: `airfacts-pw`)
- Wait a bit longer for Neo4j to fully start (can take 30-60 seconds)

### 2. Port Already in Use

**Error:** `Address already in use` (port 8000 or 7687)

**Solutions:**
- For API (port 8000):
  ```bash
  lsof -ti:8000 | xargs kill -9
  ```
  Or run on a different port:
  ```bash
  uvicorn main:app --port 8001
  ```

- For Neo4j (port 7687):
  ```bash
  docker stop neo4j
  docker rm neo4j
  ```
  Then restart the container.

### 3. No Module Named 'fastapi'

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solutions:**
- Ensure virtual environment is activated:
  ```bash
  source .venv/bin/activate
  ```
- Reinstall dependencies:
  ```bash
  pip install -r requirements-minimal.txt
  ```

### 4. Empty Database / No Data Returned

**Error:** API returns empty arrays `[]`

**Solutions:**
- Load data into Neo4j:
  ```bash
  cd neo4j
  python3 loader.py
  ```
- Verify data in Neo4j browser (http://localhost:7474):
  ```cypher
  MATCH (n) RETURN count(n)
  ```

### 5. Import Error in Routers

**Error:** `ImportError: cannot import name 'schemas'`

**Solutions:**
- Ensure you're running from the correct directory:
  ```bash
  cd api
  python -m uvicorn main:app --reload
  ```
- Check that `schemas.py` exists in the `api` folder

### 6. Docker Permission Denied

**Error:** `permission denied while trying to connect to the Docker daemon`

**Solutions:**
- Add your user to the docker group:
  ```bash
  sudo usermod -aG docker $USER
  ```
- Log out and back in for changes to take effect
- Or run with sudo (not recommended for production)

### 7. Data Loading Takes Too Long

**Issue:** `loader.py` is running for a very long time

**Solutions:**
- This is normal! Loading all airports, airlines, and routes can take 5-10 minutes
- Check progress by looking at printed messages
- Verify internet connection (data is fetched from OpenFlights)
- If it fails, try running again (might be a temporary network issue)

### 8. CORS Error in Browser

**Error:** `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS`

**Solutions:**
- Update CORS origins in `api/main.py`:
  ```python
  origins = [
      "http://localhost:3000",
      "http://127.0.0.1:3000",
      "your-frontend-url",
  ]
  ```

## Checking System Status

### Verify Python Installation
```bash
python3 --version  # Should be 3.8 or higher
```

### Verify Docker Installation
```bash
docker --version
docker ps  # Should show neo4j container if running
```

### Check Neo4j Status
```bash
docker logs neo4j  # View Neo4j logs
```

### Test API Endpoints
```bash
curl http://localhost:8000/
curl http://localhost:8000/api/airports/JFK
```

### Check Neo4j Database
1. Open http://localhost:7474 in your browser
2. Login with username: `neo4j`, password: `airfacts-pw`
3. Run query:
   ```cypher
   MATCH (a:Airport) RETURN a LIMIT 10
   ```

## Getting More Help

If you're still experiencing issues:

1. Check the logs:
   - API logs in terminal where you ran `uvicorn`
   - Neo4j logs: `docker logs neo4j`

2. Verify all dependencies are installed:
   ```bash
   pip list
   ```

3. Create an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Your OS and Python version
   - Output of `docker ps` and `pip list`
