import pytest
from neo4j import GraphDatabase
from config import db_config

@pytest.fixture(scope="module")
def driver():
    driver = GraphDatabase.driver(db_config.Neo4j_URI, auth=db_config.Neo4j_AUTH)
    yield driver
    driver.close()

def test_connection(driver):
    with driver.session() as session:
        result = session.run("RETURN 1 AS num")
        value = result.single()["num"]
        print(f"\nresult from noe4j is {value}")
        assert value == 1

def test_data_access(driver):
    with driver.session() as session:
        # 創建一個測試節點
        session.run("CREATE (n:TestNode {name: 'Test'}) RETURN n")
        
        # 查詢剛創建的節點
        result = session.run("MATCH (n:TestNode) RETURN n.name AS name")
        assert result.single()["name"] == "Test"
        
        # 清理測試數據
        session.run("MATCH (n:TestNode) DELETE n")

def test_return_content(driver):
    with driver.session() as session:
        result = session.run("CREATE (n:Person {name: 'Alice', age: 30}) RETURN n")
        record = result.single()
        node = record["n"]
        
        assert node.labels == {"Person"}
        assert node.get("name") == "Alice"
        assert node.get("age") == 30
        
        # 清理測試數據
        session.run("MATCH (n:Person {name: 'Alice'}) DELETE n")

if __name__ == "__main__":
    pytest.main([__file__])