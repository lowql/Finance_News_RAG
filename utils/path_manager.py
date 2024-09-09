# utils/path_manager.py
from pathlib import Path

def get_data_dir():
   return f"./dataset/news"

def get_history_news_file(code):
   """從FinMind API 爬取下來的原始資料 (url被google額外編碼)
   date,stock_id,link,source,title
   """
   return f"{get_data_dir()}/{code}_history_news.csv"
 
def get_filter_news_file(code):
   """ 
   經一次處裡過後的過濾資料 : 
      1. 除了YAHOO以外的消息源
      2. 無法正確解碼的URL
   """
   return f"{get_data_dir()}/{code}_news.csv"

def get_news_content_file(code):
   """ 具有內文的新聞資料集
   1. metadata: date,stock_id,author,headline
   2. content: content
   """
   return f"{get_data_dir()}/{code}_news_content.csv"

if __name__ == '__main__':
    print(get_history_news_file(6125))

