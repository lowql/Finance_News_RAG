import csv
import requests 
from bs4 import BeautifulSoup
import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..','..')))
print(sys.path)
from utils.decodeGoogleRss import decode_google_news_url
from utils.path_manager import get_history_news_file

"""
yahoo finance news web scraper (get_content)

Created on Sun 2021-06-13 20:01:25

@author: Jack.M.Liu
"""
def get_info(url):
    #send request   
    response = requests.get(url)
    #parse    
    soup = BeautifulSoup(response.text,"lxml")
    #get information we need
    content = soup.find('div',attrs={'class':'caas-body'})
    author = soup.find('span', attrs={'class': 'caas-author-byline-collapse'}).text
    headline = soup.find('h1').text 
    
    list_p = [p.get_text().strip() for p in content.find_all('p')]
    # 將列表中的項目組合成一個會換行的字符串
    pretty_content = '\n'.join(list_p)
    return author,headline,pretty_content

def store_to_pandas(data):
    df = pd.DataFrame(data=list(data),columns=['author', 'headline', 'content'])
    df.to_csv('./yahoo_news.csv',index=False)
    return 

def main():
    ok_urls = []
    with open(get_history_news_file(),'r',encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if row['source'] == 'Yahoo奇摩股市':
                try:
                    url = decode_google_news_url(row['link'])   
                    if not url.endswith('.html'):
                        raise Exception("url not pharse complete") 
                    else:
                        ok_urls.append(url)
                except:
                     print(row['title'],'\n',url,'\n\n')
    
    news = []
    for ok_url in ok_urls:
        news.append(get_info(ok_url))
        store_to_pandas(news)
if __name__ == '__main__':
    main()