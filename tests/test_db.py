
def test_query(db_connection):
    # 使用db_connection進行測試
    assert db_connection is not None
    # assert db_connection.query("SELECT * FROM table") is not None

def test_neo4j_version():
    from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
    from config.db_config import Neo4j_USER,Neo4j_PWD,Neo4j_URI
    graph_store = Neo4jPropertyGraphStore(
            username=Neo4j_USER,
            password=Neo4j_PWD,
            url=Neo4j_URI,
        )
    db_data = graph_store.structured_query("CALL dbms.components()")
    version = db_data[0]["versions"][0]
    print("version: ",version)
