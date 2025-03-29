# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 21:28:04 2024

@author: USER
"""
#城市名稱:tvbs.py

#====================
# 東森新聞往爬蟲程式
#====================

#import sqlite3                          # 匯入 sqlite3 模組，用於操作 SQLite 資料庫
# ========================================================
# 東森新聞爬蟲程式：TVBS 即時新聞
# TVBS News Scraper for Real-Time News
# ========================================================

import requests  # 匯入 requests 模組，用於發送 HTTP 請求
# Import requests library for HTTP requests
from bs4 import BeautifulSoup  # 匯入 BeautifulSoup，用於解析 HTML
# Import BeautifulSoup for HTML parsing
from flask import Blueprint, jsonify
# Import Flask Blueprint and JSON response module
from models import db, NewsArticle  # 從 models 匯入資料庫與新聞模型
from database import db
# Import database and NewsArticle model from models.py
from datetime import datetime  # 用於解析與格式化日期時間
# For handling and formatting date and time
import random  # 用於隨機內文生成
# For random text generation

# 初始化 Blueprint
# Initialize Blueprint
tvbs_bp = Blueprint('tvbs', __name__)

def fetch_tvbs_news():
    """
    爬取 TVBS 即時新聞
    Fetch real-time news from TVBS
    """
    # 設定目標網址與 Headers
    # Target URL and headers
    url = "https://news.tvbs.com.tw/realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    # 發送 GET 請求並取得回應
    # Send GET request and fetch response
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # 定位到新聞列表的區塊
    # Locate news list section
    newslist = soup.find(class_='news_list')
    if not newslist:
        print("❌ 無法找到新聞列表區塊")
        return []

    # 獲取所有新聞項目
    # Get all news items
    news = newslist.find(class_='list')
    if not news:
        print("❌ 無法找到具體新聞內容")
        return []

    li_items = news.find_all('li')
    inserted_news = []  # 儲存成功插入的新聞
    source = "TVBS"  # 新聞來源

    # 迭代每一則新聞
    # Process each news item
    for row in li_items:
        link_tag = row.find('a')
        if link_tag:
            link = "https://news.tvbs.com.tw" + link_tag.get('href')  # 拼接完整網址
            photo = row.find('img').get('data-original')  # 獲取圖片
            title = row.find('h2').text.strip()  # 獲取標題
            
            # 隨機文字或摘要
            # Random content or summary
            content_tag = row.find('p')
            content = content_tag.text.strip() if content_tag else random.choice(["點擊查看更多", "瞭解詳情", "快速瀏覽"])

            # 發布時間處理
            # Handle publication time
            time_tag = row.find('time')
            try:
                published_at = datetime.strptime(time_tag.text.strip(), "%Y-%m-%d %H:%M:%S")
            except (ValueError, AttributeError):
                published_at = datetime.utcnow()  # 無法解析時使用當前時間

            # 檢查新聞是否已存在於資料庫中
            # Check if the news already exists in the database
            existing = NewsArticle.query.filter_by(url=link).first()
            if not existing:
                # 將新聞插入資料庫
                # Insert news into the database
                news_article = NewsArticle(
                    title=title,
                    content=content,
                    source=source,
                    image_url=photo,
                    url=link,
                    published_at=published_at
                )
                db.session.add(news_article)
                db.session.commit()
                inserted_news.append({"title": title, "link": link})

    return inserted_news

@tvbs_bp.route("/scrape", methods=["GET"])
def fetch_tvbs_api():
    """
    提供 API，手動觸發新聞爬取
    Provide an API to trigger the news scraping manually
    """
    news = fetch_tvbs_news()
    return jsonify({"message": f"成功存入 {len(news)} 篇新聞", "data": news}), 200
# 運行程式並打印結果
if __name__ == '__main__':
    news = fetch_tvbs_news()
    print("=== 隨機抓取各兩則新聞 ===")
    for idx, article in enumerate(news, start=1):
        print(f"新聞 {idx}:")
        print(f"標題: {article['title']}")
        print(f"連結: {article['link']}")
        print(f"圖片: {article['image_link']}")
        print("==============================")

"""
程式功能總結：
1. 透過 requests 模組發送 GET 請求到 TVBS 即時新聞網址，並將回應內容以 UTF-8 解碼。
2. 使用 BeautifulSoup 解析 HTML，定位到新聞列表區塊，並進一步提取具體新聞內容。
3. 對每則新聞提取標題、連結、圖片以及發佈時間，並將新聞保存至 MySQL 資料庫。
4. 提供一個 API (/tvbs/scrape)，可手動觸發爬取操作，並返回已插入的新聞數量與詳細資訊。
"""