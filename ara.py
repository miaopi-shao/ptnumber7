# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 10:00:23 2025

@author: OAP-0001
"""

import requests
from bs4 import BeautifulSoup
import random

# 爬取 年代新聞
def fetch_ara_news():
    url = "https://www.eracom.com.tw/EraNews/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'  # 或者 'big5'
        soup = BeautifulSoup(response.text, "html.parser")
        
        news_list = soup.find("div", class_="overflow")
    
        if news_list:
            articles = news_list.find_all("li")  # 遍歷 li 區塊   
            # print(len(articles))  # 確認是否抓到了新聞區塊
            results = []
            for article in articles:
                # print(article.prettify())  # 查看每個新聞區塊的 HTML 結構
                title_tag = article.find("p").find("a")  # 找到 <p> 內的 <a>
                title = title_tag.text.strip() if title_tag else "No Title"
                link = article.find("a")["href"] if article.find("a") else "No Link"
                image = article.find("img")["src"] if article.find("img") else "No Image"
                image2 = image.replace("196x110", "711x400")
                
                results.append({
                    "title": title,
                    "link": link,
                    "image_link": image,
                    "image_link2": image2,
                    "source": "Era News",
                })
            return random.sample(results, min(2, len(results)))
        else:
         print("未找到 ul.clearfix，請確認 HTML 結構")
         return []
    else:
        print(f"無法獲取網頁內容，狀態碼: {response.status_code}")
        return []
    

# 運行程式並打印結果
if __name__ == '__main__':
    news = fetch_ara_news()
    print("=== 隨機抓取各兩則新聞 ===")
    for item in news:  # 限制輸出前兩則新聞
            print(f"標題: {item['title']}")
            print(f"網址: {item['link']}")
            print(f"圖片: {item['image_link']}")
            print("-" * 40)


