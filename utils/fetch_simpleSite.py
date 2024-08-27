import httpx
from bs4 import BeautifulSoup
news_url =  "https://www.oligo.security/blog/0-0-0-0-day-exploiting-localhost-apis-from-the-browser"

def save_soup(soup):
    with open('news.html','w',encoding="utf-8") as f:
        f.write(soup)
def main():
    response = httpx.get(news_url)
    soup = BeautifulSoup(response.content,'html.parser')
    print(soup.main.get_text())
    save_soup(soup.main.get_text(separator="\n"))
    
    
    
if __name__ == '__main__':
    main()