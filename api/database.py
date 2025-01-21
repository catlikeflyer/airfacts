from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "airfacts-pw"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def get_db_session():
    """
    Return a new session to the database
    """
    return driver.session()

def close_db():
    """
    Close the database connection
    """
    driver.close()
