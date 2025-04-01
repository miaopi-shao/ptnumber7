# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 12:18:07 2025

@author: OAP-0001
"""
# 程式名稱: Page_Noiser.py 三網站爬蟲混合展示

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random


def fetch_news():
    articles = []  # 儲存所有新聞的陣列
    start_time = datetime.now()

    # 📰【VOGUE】新聞爬取
    classes = ["fashion","beauty","entertainment","lifestyle","luxury","video"]
    
    url = "https://www.vogue.com.tw/"
    for c in classes:
        r = requests.get(url+c)
            
        if r.status_code == 200:
                # print(r.text)
                soup = BeautifulSoup(r.text,'html.parser')
                # print(soup.title.string)
                titles = soup.find_all('h2', class_="SummaryItemHedBase-hiFYpQ eLtvVr summary-item__hed")[:10]
                times = soup.find_all('time', class_="BaseWrap-sc-gjQpdd BaseText-ewhhUZ SummaryItemBylinePublishDate-ctLSIQ iUEiRd ipBjLL kiqveE summary-item__publish-date")[:10]
                links = soup.find_all("a", attrs={"class":"SummaryItemHedLink-civMjp jRfyII summary-item-tracking__hed-link summary-item__hed-link"})[:10]
                for title,time,link in zip(titles,times,links):
                    # print(title.text,time.text,"https://www.vogue.com.tw"+link.get("href"))
                    # print()
                    articles.append({
                        "title": title.text,
                        "published_at": time.text,
                        "url": "https://www.vogue.com.tw" + link.get("href"),
                        "source": "VOGUE",
                        "category": c
                    })
    
    # 🌍【YAM 旅行】新聞爬取
    classes = ["play","eat","foreign","hot"]
    
    url = "https://travel.yam.com/"
    
    for c in classes:
        r = requests.get(url+"/info/"+c)
            
        if r.status_code == 200:
                # print(r.text)
                soup = BeautifulSoup(r.text,'html.parser')
                # print(soup.title.string)
                titles = soup.find_all('h2')[:10]
                times = soup.find_all('p',class_="artcle_author_info")[:10]
                for title,time in zip(titles,times):
                    # print(type(title))
                    # soup2 = BeautifulSoup(str(title),'html.parser')
                    # links = soup2.find_all("a")
                    # for link in links:
                        # print(link.get("href"))
                    # print(title.text,title.get("href"),time.text,"https://travel.yam.com"+soup2.find("a").get("href"))
                    # print(title.text,title.get("href"),time.text,"https://travel.yam.com"+title.a.get("href"))
                    # print()
                    articles.append({
                        "title": title.text,
                        "published_at": time.text,
                        "url": "https://travel.yam.com" + title.a.get("href"),
                        "source": "YAM旅行",
                        "category": c
                    })
                    
                    
    
    # 🔬【PanSci 科學】新聞爬取
    classes = ["humanbeing","earth","space","文明足跡","environment","lifescience"]
    
    url = "https://pansci.asia/"
    
    for c in classes:
        r = requests.get(url+"/archives/category/type/"+c)
            
        if r.status_code == 200:
                # print(r.text)
                soup = BeautifulSoup(r.text,'html.parser')
                # print(soup.title.string)
                titles = soup.find_all('a', class_="post-title ga_track")[:10]
                times = soup.find_all('span', class_="post-text-light")[:10]
                for title,time in zip(titles,times):
                     # print(title.text,time.text,title.get("href"))
                     # print()
                     articles.append({
                           "title": title.text,
                           "published_at": time.text,
                           "url": title.get("href"),
                           "source": "PanSci",
                           "category": c
                       })

    # 🎯 隨機選取 10 則新聞
    end_time = datetime.now()
    execution_time = end_time - start_time
    print(f"爬取時間: {execution_time.total_seconds()} 秒")
    return random.sample(articles, min(len(articles), 10))





if __name__ == "__main__":
    news = fetch_news()
    for item in news:
        print(f"{item['published_at']} - {item['title']} ({item['source']})")
        print(f"🔗 {item['url']}")
        print()

