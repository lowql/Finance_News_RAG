# tests\dataset_workflow\test_pipline.py
from pipeline import utils
from pipeline.news import News

def test_fetch_for_flask():
    news = News(6125)
    headlines = news.fetch_headline()
    print(headlines)
    print(news.fetch_content(headlines[0]))
