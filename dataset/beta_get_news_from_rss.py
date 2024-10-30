from datetime import datetime
from dataset.news_crawler.fetch_yahoo import fetch_new
import feedparser
def show_news_info(feed,cols=['title','link','published']):
    entries = [entry for entry in feed.entries]
    for entry in entries:
        # [print(f"key: {key}\nitem:\n{item}\n====")for key,item in entry.items()]
        if 'title' in cols:
            print(entry['title']) 
        if 'link' in cols:
            print(entry['link'])
            print(fetch_new(entry)['content'])
        if 'published' in cols:
            timestamp = entry['published']
            # 2023-01-10T07:39:30.000Z
            formatted_date = datetime.strptime(timestamp, "%a, %d %b %Y %H:%M:%S GMT").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            print(formatted_date) 
        print('===============')
        
def fetch_stock_news(stock_id):
    stock_news_url = f"https://tw.stock.yahoo.com/rss?s={stock_id}.TWO"
    feed = feedparser.parse(stock_news_url)
    show_news_info(feed)

def fetch_market_news():
    yahoo_rss =[
    ("最新新聞","https://tw.stock.yahoo.com/rss?category=news"), 
    ("台股動態","https://tw.stock.yahoo.com/rss?category=tw-market"), 
    ("國際財經","https://tw.stock.yahoo.com/rss?category=intl-markets"), 
    # ("小資理財","https://tw.stock.yahoo.com/rss?category=personal-finance"), 廣告新聞偏多
    ("基金動態","https://tw.stock.yahoo.com/rss?category=funds-news"), 
    ("專家專欄","https://tw.stock.yahoo.com/rss?category=column"), 
    ("研究報導","https://tw.stock.yahoo.com/rss?category=research"), 
    ]
    for rss_url in yahoo_rss:
        print(f" ================ {rss_url[0]} ================ ")
        feed = feedparser.parse(rss_url[1])
        show_news_info(feed,['title','link','published'])

if __name__ == "__main__":
    fetch_market_news()