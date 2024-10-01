import requests 
from bs4 import BeautifulSoup
import pandas as pd
from utils.path_manager import get_filter_news_file,get_news_content_file

"""
yahoo finance news web scraper (get_content)

Created on Sun 2021-06-13 20:01:25

@author: Jack.M.Liu
"""
def fetch_announcement_news(row):
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
    code = 2421
    
    
    
    import os
    filters = os.listdir('./dataset/filter/')
    codes = [f.split('_')[0] for f in filters]
    print(codes)
    for code in codes:
        filter_news_path = get_filter_news_file(code)
        df = pd.read_csv(filter_news_path)
        df[['author','headline','content']] = df.apply(fetch_announcement_news,axis=1) #  return pd.Series({'author':author,'headline':headline,'content':pretty_content})
        # 過濾掉缺失數據的行
        df = df.dropna(subset=['author', 'headline', 'content'])
        news_path = get_news_content_file(code=code)
        df.to_csv(news_path,columns=['date','stock_id','author','headline','content'],index=False)
    
    # announcement_news = df[df['title'].str.contains(pat = '【.*】', regex = True)].loc[:,['title','link']]
    # print(df[df['title'].str.contains(pat = '盤中速報', regex = True)].loc[:,['date','title']],'\n')
    # print(df[df['title'].str.contains(pat = '焦點股', regex = True)].loc[:,['date','title']],'\n')
    # print(df[df['title'].str.contains(pat = '熱門股', regex = True)].loc[:,['date','title']],'\n')
    # print(df[df['title'].str.contains(pat = '營收', regex = True)].loc[:,['date','title']],'\n')
    # print(df[df['title'].str.contains(pat = '《.*》', regex = True)].loc[:,['date','title']],'\n')
    


if __name__ == '__main__':
    main()