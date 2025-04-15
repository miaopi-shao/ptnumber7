# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 11:11:37 2025

@author: OAP-0001
"""

import requests
from bs4 import BeautifulSoup
import random

# 爬取 華視新聞
def fetch_cts2_news():
    url = "https://news.cts.com.tw/real/index.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        response.encoding = 'utf-8'  # 或者 'big5'
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 找到新聞列表的父容器
        news_container = soup.find("div", class_="newslist-container flexbox one_row_style")
        
        if news_container:
            articles = news_container.find_all("a")  # 找到所有新聞區塊
            
            results = []
            for article in articles:
                # 嘗試獲取圖片，使用 data-src
                image_tag = article.find("div", class_="item-img-s").find("img") if article.find("div", class_="item-img-s") else None
                
                if not image_tag or "data-src" not in image_tag.attrs:
                    continue  # 跳過沒有圖片的新聞
                
                image_url = image_tag["data-src"]  # 取得圖片網址
    
                # 提取標題與連結
                title = article.get("title").strip() if article.get("title") else "No Title"
                link = article.get("href") if article.get("href") else "No Link"
    
                # 提取發布日期（從 `newstime` 內部）
                date_tag = article.find("div", class_="newstime")
                date = date_tag.text.strip() if date_tag else "No Date"
                
                results.append({
                    "title": title,
                    "link": link,
                    "image_link": image_url, 
                    "image_link2": image_url,
                    "date-time":date,
                    "source": "cts News",
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
    news = fetch_cts2_news()
    print("=== 隨機抓取各兩則新聞 ===")
    for item in news:  # 限制輸出前兩則新聞
            print(f"標題: {item['title']}")
            print(f"網址: {item['link']}")
            print(f"圖片: {item['image_link']}")
            print(f"時間: {item['date-time']}")
            print("-" * 40)