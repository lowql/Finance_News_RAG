import pytest

def add(a,b):
    return a+b
    
@pytest.mark.parametrize("test_input,expected", [(1, 2), (3, 4), (5, 6)])
def test_add(test_input, expected):
    assert add(test_input, 1) == expected
    
    
def test_query(db_connection):
    # 使用db_connection進行測試
    assert db_connection is not None
    # assert db_connection.query("SELECT * FROM table") is not None