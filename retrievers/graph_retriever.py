from neo4j import GraphDatabase
from typing import List, Dict, Any
from config import db_config

class Neo4jRetriever:
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize the Neo4jRetriever with connection details.

        :param uri: The URI of the Neo4j database.
        :param user: The username for authentication.
        :param password: The password for authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Close the connection to the database.
        """
        self.driver.close()

    def retrieve_by_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and retrieve results.

        :param query: The Cypher query to execute.
        :param parameters: A dictionary of parameters to include in the query.
        :return: A list of dictionaries representing the query results.
        """
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def retrieve_related_nodes(self, cypher_query:str, value: Any = None) -> List[Dict[str, Any]]:
        """
        Retrieve related nodes based on a relationship and node property.

        :param query: cypher query
        :param value: The value of the node property to match.
        :return: A list of dictionaries representing the related nodes.
        """
        
        return self.retrieve_by_query(cypher_query, {"value": value})


if __name__ == '__main__':
    
    retriever = Neo4jRetriever(db_config.Neo4j_URL, db_config.Neo4j_USER, db_config.Neo4j_PWD)
    query = """MATCH (:Company {code:6125})-[r:competitor]->(p) RETURN p.name LIMIT 25"""
    results = retriever.retrieve_related_nodes(query)
    for i in results:
        print(i)
    retriever.close()
