from neo4j import GraphDatabase
from typing import List, Dict, Any
from config import db_config

class Neo4jRetriever:
    def __init__(self, uri, auth):
        """
        Initialize the Neo4jRetriever with connection details.

        :param uri: The URI of the Neo4j database.
        :param auth: authentication (username,password).
        """
        self.driver = GraphDatabase.driver(uri, auth=auth)

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

    def retrieve_suppliers(self,value: Any = None) -> List[Dict[str, Any]]:
        # HACK: noly 6125 fit 
        query = """MATCH (n:Company {code:$code}) RETURN n.suppliers"""
        
        # TODO: build new relation
        # query = """"MATCH (:Company {code:$code})-[r:supplier]->(p) RETURN p.name LIMIT 25"""
        
        return self.retrieve_by_query(query, {"code": value})

    def retrieve_competitor(self,value: Any = None) -> List[Dict[str, Any]]:
        query = """MATCH (:Company {code:$code})-[r:competitor]->(p) RETURN p.name LIMIT 25"""
        return self.retrieve_by_query(query, {"code": value})
    
if __name__ == '__main__':
    
    retriever = Neo4jRetriever(db_config.Neo4j_URI, db_config.Neo4j_AUTH)
    query = """MATCH (:Company {code:6125})-[r:competitor]->(p) RETURN p.name LIMIT 25"""
    
    results = retriever.retrieve_competitor(6125)
    [print(i) for i in results]
    
    results = retriever.retrieve_suppliers(6125)
    [print(i) for i in results]
    retriever.close()
