# utils/path_manager.py
from pathlib import Path

""" DataSets """
def get_dataset_dir():
   return f"./dataset"

def get_download_news_file(code):
   return f"{get_dataset_dir()}/download/{code}_history_news.csv"
 
def get_filter_news_file(code):
   """ 
   經一次處裡過後的過濾資料 : 
      1. 除了YAHOO以外的消息源
      2. 無法正確解碼的URL
   """
   return f"{get_dataset_dir()}/filter/{code}_yahoo_news.csv"

def get_news_content_file(code):
   """ 具有內文的新聞資料集
   1. metadata: date,stock_id,author,headline
   2. content: content
   """
   return f"{get_dataset_dir()}/news/{code}_news.csv"

def get_company_relations():
   return f"{get_dataset_dir()}/base/company_relations.csv"

""" Templates """
def get_templates_dir():
   return f"./templates"

def get_llama_index_template(type):
   return f"{get_templates_dir()}/llama-index/{type}_template.jinja"
   

if __name__ == '__main__':
    print(get_news_content_file(6125))

