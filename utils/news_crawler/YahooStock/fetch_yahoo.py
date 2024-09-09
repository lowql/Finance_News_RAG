import csv
import requests 
from bs4 import BeautifulSoup
import sys
import os
import pandas as pd
from utils.decodeGoogleRss import decode_google_news_url
from utils.path_manager import get_filter_news_file,get_news_content_file

"""
yahoo finance news web scraper (get_content)

Created on Sun 2021-06-13 20:01:25

@author: Jack.M.Liu
"""
def get_info(row):
    #send request   
    response = requests.get(row['link'])
    #parse    
    soup = BeautifulSoup(response.text,"lxml")
    #get information we need
    content = soup.find('div',attrs={'class':'caas-body'})
    author = soup.find('span', attrs={'class': 'caas-author-byline-collapse'}).text
    headline = soup.find('h1').text 
    
    list_p = [p.get_text().strip() for p in content.find_all('p')]
    # 將列表中的項目組合成一個會換行的字符串
    pretty_content = '\n'.join(list_p)
    print('.',end='')
    return pd.Series({'author':author,'headline':headline,'content':pretty_content})

def store_to_pandas(data):
    # 6125_history_news: date,stock_id,link,source,title,is_similar
    df = pd.DataFrame(data=list(data),columns=['date','stock_id','author', 'headline', 'content'])
    df.to_csv(get_news_content_file(),index=False)
    return 

def main():
    filter_news_path = get_filter_news_file(6125)
    df = pd.read_csv(filter_news_path)
    
    # date,stock_id,link,source,title,is_similar,available
    df[['author','headline','content']] = df.apply(get_info,axis=1)

    news_path = get_news_content_file(code=6125)
    df.to_csv(news_path,columns=['date','stock_id','author','headline','content'],index=False)

if __name__ == '__main__':
    main()