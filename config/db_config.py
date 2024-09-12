import os
# Neo4j config
Neo4j_HOST = os.getenv("Neo4j_HOST", "localhost")
Neo4j_PORT = os.getenv("Neo4j_PORT", "7687")
Neo4j_URI = f"bolt://{Neo4j_HOST}:{Neo4j_PORT}"

Neo4j_USER = os.getenv("Neo4j_USER", "neo4j")
Neo4j_PWD = os.getenv("Neo4j_PWD", "stockinfo")
Neo4j_AUTH = (Neo4j_USER,Neo4j_PWD)
