
from retrievers.graph_retriever import Neo4jRetriever

# MATCH (:Company {code:6125})-[r:competitor]->(p) RETURN p.name LIMIT 25

query = (
            f"MATCH (n:{node_label} {{ {node_property}: $value }})"
            f"-[:{relationship}]->(related:{target_label}) "
            "RETURN related"
        )