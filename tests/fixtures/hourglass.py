# test_autouse.py
import pytest
import time
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

""" 
scope='session'：這個參數定義了夾具的生命週期。在這裡，session表示該夾具在整個測試會話期間只會被創建一次，這意味著所有測試都將共享同一個夾具實例。
autouse=True：這個參數使得夾具自動應用於所有可以訪問它的測試，而無需在測試函數中顯式請求它。這樣，所有測試都會在運行之前自動執行這個夾具。
"""
@pytest.fixture(scope='session', autouse=True)
def timer_session_scope():
    start = time.time()
    print('\nstart: {}'.format(time.strftime(DATE_FORMAT, time.localtime(start))))

    yield

    finished = time.time()
    print('finished: {}'.format(time.strftime(DATE_FORMAT, time.localtime(finished))))
    print('Total time cost: {:.3f}s'.format(finished - start))
    
    
@pytest.fixture(autouse=True)
def timer_function_scope():
    start = time.time()
    yield
    print(' Time cost: {:.3f}s'.format(time.time() - start))