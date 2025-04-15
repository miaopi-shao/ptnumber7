# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 11:28:08 2025

@author: OAP-0001
"""


import requests
from bs4 import BeautifulSoup
import random

# 爬取 台視新聞
def fetch_ttv_news():
    url = "https://news.ttv.com.tw/realtime"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 找到新聞列表的父容器
        news_container = soup.find("article", class_="container").find("div", class_="news-list news-list-h img-left mt-ht").find("ul")
        
        if news_container:
            articles = news_container.find_all("li")  # 找到所有新聞區塊
            
            results = []
            for article in articles:
                # 提取圖片
                image_tag = article.find("img")
                image_url = image_tag["src"] if image_tag and "src" in image_tag.attrs else None
                if not image_url:
                    continue  # 跳過沒有圖片的新聞
    
                # 提取標題
                title_tag = article.find("div", class_="title")
                title = title_tag.text.strip() if title_tag else "No Title"
    
                # 提取摘要
                summary_tag = article.find("div", class_="summary")
                summary = summary_tag.text.strip() if summary_tag else "No Summary"
    
                # 提取日期
                date_tag = article.find("div", class_="time")
                date = date_tag.text.strip() if date_tag else "No Date"
    
                # 提取分類
                category_tag = article.find("div", class_="cate")
                category = category_tag.text.strip() if category_tag else "No Category"
    
                # 提取連結
                link_tag = article.find("a")
                link = link_tag["href"] if link_tag and "href" in link_tag.attrs else "No Link"
                
                results.append({
                    "category": category,
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "image_link": image_url, 
                    "image_link2": image_url,
                    "date-time":date,
                    "source": "ttv News",
                })
            return random.sample(results, min(2, len(results)))
        else:
            print("未找到新聞容器，請確認 HTML 結構")
            return []
    else:
        print(f"無法獲取網頁內容，狀態碼: {response.status_code}")
        return []
        
# 運行程式並打印結果
if __name__ == '__main__':
    news = fetch_ttv_news()
    print("=== 隨機抓取各兩則新聞 ===")
    for item in news:  # 限制輸出前兩則新聞
            print(f"標題: {item['title']}")
            print(f"網址: {item['link']}")
            print(f"圖片: {item['image_link']}")
            print(f"時間: {item['date-time']}")
            print("-" * 40)