def get_dataset_dir():
   return f"./dataset"

def get_download_news_file(code):
   return f"{get_dataset_dir()}/download/{code}_history_news.csv"
 
def get_filter_news_file(code):
   """ ./dataset/filter/{code}_yahoo_news.csv\n
   經一次處裡過後的過濾資料 :\n 
   1. 目前只有消息源 只有 YAHOO\n
   2. 正確解碼的URL
   """
   return f"{get_dataset_dir()}/filter/{code}_yahoo_news.csv"

def get_news_content_file(code):
   """ ./dataset/news/{code}_news.csv\n
   1. metadata: date,stock_id,author,headline\n
   2. content: content
   """
   return f"{get_dataset_dir()}/news/{code}_news.csv"

def get_company_relations():
   return f"{get_dataset_dir()}/base/company_relations.csv"

def get_templates_dir():
   return f"./templates"

def get_llama_index_template(type):
   return f"{get_templates_dir()}/llama-index/{type}_template.jinja"


