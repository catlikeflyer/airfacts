"""
Detailed Neo4j Connection Diagnostic Tool
"""

from dotenv import load_dotenv
import os
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
import socket

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "airfacts-pw")

print("=" * 70)
print("Neo4j Connection Diagnostics")
print("=" * 70)
print()

# 1. Check environment variables
print("1. Environment Configuration:")
print(f"   URI:      {NEO4J_URI}")
print(f"   Username: {NEO4J_USERNAME}")
print(f"   Password: {'*' * min(len(NEO4J_PASSWORD), 40)}")
print()

# 2. Parse URI
print("2. URI Analysis:")
if NEO4J_URI.startswith("neo4j+s://"):
    print("   ✓ Using secure Neo4j protocol (AuraDB)")
    host = NEO4J_URI.replace("neo4j+s://", "")
    port = 7687
    is_aura = True
elif NEO4J_URI.startswith("bolt://"):
    print("   ✓ Using bolt protocol (local/self-hosted)")
    host = NEO4J_URI.replace("bolt://", "").split(":")[0]
    port = int(NEO4J_URI.split(":")[-1]) if ":" in NEO4J_URI else 7687
    is_aura = False
else:
    print(f"   ⚠️  Unknown protocol: {NEO4J_URI.split('://')[0]}")
    host = None
    port = None
    is_aura = False

print(f"   Host: {host}")
print(f"   Port: {port}")
print()

# 3. DNS resolution
if host:
    print("3. DNS Resolution:")
    try:
        ip = socket.gethostbyname(host)
        print(f"   ✓ Host resolves to: {ip}")
    except socket.gaierror as e:
        print(f"   ✗ DNS resolution failed: {e}")
        print("   → Check your internet connection")
    print()

# 4. Network connectivity (for AuraDB, we can't test socket connection due to routing)
if not is_aura and host:
    print("4. Network Connectivity:")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"   ✓ Port {port} is reachable")
        else:
            print(f"   ✗ Port {port} is not reachable")
            print("   → Check if Neo4j is running")
    except Exception as e:
        print(f"   ✗ Connection test failed: {e}")
    print()

# 5. Neo4j driver connection
print(f"{'4' if is_aura else '5'}. Neo4j Driver Connection:")
driver = None
try:
    print("   Attempting to connect...")
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
        max_connection_lifetime=3600,
        max_connection_pool_size=50,
        connection_acquisition_timeout=60,
    )

    print("   Verifying connectivity...")
    driver.verify_connectivity()
    print("   ✓ Driver connection successful!")
    print()

    # 6. Test query
    print(f"{'5' if is_aura else '6'}. Database Query Test:")
    with driver.session() as session:
        result = session.run("RETURN 1 as test")
        record = result.single()
        if record and record["test"] == 1:
            print("   ✓ Query execution successful!")

        # Check if database has data
        result = session.run("MATCH (n) RETURN count(n) as count LIMIT 1")
        count = result.single()["count"]
        print(f"   Total nodes in database: {count:,}")

        if count == 0:
            print("   ⚠️  Database is empty - no data loaded yet")
        else:
            print("   ✓ Database contains data")

    print()
    print("=" * 70)
    print("✓ All diagnostics passed - connection is healthy!")
    print("=" * 70)

except AuthError as e:
    print(f"   ✗ Authentication failed: {e}")
    print()
    print("   Troubleshooting:")
    print("   → Check your username and password in .env")
    print("   → For AuraDB: verify credentials in Neo4j Aura console")
    print("   → For local: default is neo4j/airfacts-pw")

except ServiceUnavailable as e:
    print(f"   ✗ Service unavailable: {e}")
    print()
    print("   Troubleshooting:")
    if is_aura:
        print("   → Your AuraDB instance might be paused or deleted")
        print("   → Check Neo4j Aura console: https://console.neo4j.io")
        print("   → Verify the instance is running")
        print("   → Check if you need to resume the instance")
    else:
        print("   → Check if Neo4j is running: docker ps | grep neo4j")
        print("   → Try starting Neo4j: docker start neo4j")
        print("   → Check Neo4j logs: docker logs neo4j")

except Exception as e:
    print(f"   ✗ Connection failed: {type(e).__name__}")
    print(f"   Error: {str(e)}")
    print()
    print("   Troubleshooting:")
    print("   → Check your .env file configuration")
    print("   → Verify the URI format is correct")
    if is_aura:
        print("   → For AuraDB: URI should be neo4j+s://xxxxx.databases.neo4j.io")
    else:
        print("   → For local: URI should be bolt://localhost:7687")

finally:
    if driver:
        driver.close()

print()
