import requests 
from bs4 import BeautifulSoup
import pandas as pd
from utils.path_manager import get_filter_news_file,get_news_content_file

"""
yahoo finance news web scraper (get_content)

Created on Sun 2021-06-13 20:01:25

@author: Jack.M.Liu
"""
def fetch_new(row):
    #send request   
    response = requests.get(row['link'])
    #parse    
    soup = BeautifulSoup(response.text,"lxml")
    #get information we need
    author = soup.find('span', attrs={'class': 'caas-author-byline-collapse'}).text
    time = soup.find('time').get('datetime')
    headline = soup.find('h1').text 
    
    content = soup.find('div',attrs={'class':'caas-body'})
    list_p = [p.get_text().strip() for p in content.find_all('p')]
    pretty_content = '\n'.join(list_p)
    
    print('.',end='')
    return pd.Series({'headline':headline,'author':author,'time':time,'content':pretty_content})

    
def main():
    code = 2421
    import os
    filters = os.listdir('./dataset/filter/')
    codes = [f.split('_')[0] for f in filters]
    print(codes)
    for code in codes:
        print(f"fetch {code} news",end='')
        
        filter_news_path = get_filter_news_file(code)
        df = pd.read_csv(filter_news_path)
        df[['headline','author','time','content']] = df.apply(fetch_new,axis=1) #  return pd.Series({'author':author,'headline':headline,'content':pretty_content})
        df = df.dropna(subset=['headline','author','time','content'])
        
        news_path = get_news_content_file(code=code)
        df.to_csv(news_path,columns=['headline','author','time','content'],index=False)
        print()
    
if __name__ == '__main__':
    main()