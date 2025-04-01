# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 12:59:06 2025

@author: OAP-0001
"""

# 聯合新聞網爬蟲程式

import requests

def fetch_udn2_news():
    """即時抓取聯合新聞網的最新新聞，返回前 10 則新聞列表"""
    api_url = "https://udn.com/api/more?page=2&id=&channelId=1&cate_id=0&type=breaknews&totalRecNo=20752"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        news_data = response.json()  # 解析 JSON 數據
        articles = [
            {
                "title": news.get("title", "無標題"),
                "url": "https://udn.com" + news.get("url", "")
            }
            for news in news_data.get("lists", [])[:10]
        ]
        return articles
    else:
        print(f"❌ 無法獲取新聞資料，HTTP 狀態碼：{response.status_code}")
        return []

# 📡 直接執行時輸出新聞資料
if __name__ == "__main__":
    news = fetch_udn2_news()
    for index, item in enumerate(news, start=1):
        print(f"{index}. {item['title']}\n   🔗 {item['url']}")
        print("======================================")