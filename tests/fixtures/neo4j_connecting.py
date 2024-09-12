import pytest
from config import db_config
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from storages.build.property_graph import BuildPropertyGraph


def create_connection():
    uri = db_config.Neo4j_URI
    auth = db_config.Neo4j_AUTH
    driver = GraphDatabase.driver(uri,auth=auth)
    return driver

@pytest.fixture
def db_connection():
    try:
        connection = create_connection()
    except ServiceUnavailable:
        print("請確認資料庫的連結")
        return False
    except Exception as e:
        print("something wrong: ",str(e))
        return False
    yield connection
    connection.close()
    
@pytest.fixture
def neo4j_connection():
    try:
        driver = BuildPropertyGraph()
    except ServiceUnavailable:
        print("請確認資料庫的連結")
        return False
    except Exception as e:
        print("something wrong: ",str(e))
        return False
    yield driver
    driver.graph_store.close()
