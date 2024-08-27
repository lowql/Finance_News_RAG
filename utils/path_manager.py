# utils/path_manager.py
from pathlib import Path

def get_project_root():
   return Path(__file__).resolve().parent.parent
def get_data_dir():
   return get_project_root() / 'dataset' / 'news'

def get_history_news_file():
    return get_data_dir() / '6125_history_news.csv'

if __name__ == '__main__':
    print(get_history_news_file())

