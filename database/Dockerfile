# Use the official Neo4j image as the base
FROM neo4j:latest

# Set environment variables for Neo4j configuration
ENV NEO4J_AUTH=neo4j/airfacts-pw \
    NEO4J_dbms_memory_heap_initial__size=512m \
    NEO4J_dbms_memory_heap_max__size=1G \
    NEO4JLABS_PLUGINS='["graph-data-science"]' \
    NEO4J_apoc_import_file_enabled=true \
    NEO4J_dbms_security_procedures_unrestricted=apoc.*

# Create the import directory (if it doesn't already exist)
RUN mkdir -p /var/lib/neo4j/import

# Expose ports for Bolt and HTTP protocols
EXPOSE 7687 7474

# Entry point for Neo4j
CMD ["neo4j"]
