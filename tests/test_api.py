import pytest
def test_correct():
    assert 1==1
    
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def test_divide_by_zero():
    #正常運算 pass
    assert divide(1,1)
    #正常觸發異常 pass
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        assert divide(1, 0)