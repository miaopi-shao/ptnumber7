# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 21:23:02 2024

@author: USER
"""

# 城市名稱:udn.py
# ===============================
# 聯合新聞網爬蟲程式
# UDN News Scraper
# ===============================

import requests  # 匯入 requests 模組，用於發送 HTTP 請求
from flask import Blueprint, jsonify
from models import db, NewsArticle  # 引入資料庫與新聞模型
from database import db
from dateutil import parser  # 安裝依賴庫：pip install python-dateutil
from datetime import datetime  # 解析時間格式
import random  # 用於隨機內文生成

# 初始化 Blueprint
udn_bp = Blueprint('udn', __name__, url_prefix="/udn")

def fetch_udn_news():
    """
    從聯合新聞網 API 獲取即時新聞
    Fetch real-time news from UDN News API
    """
    # 設定 API 目標網址
    api_url = "https://udn.com/api/more?page=2&id=&channelId=1&cate_id=0&type=breaknews&totalRecNo=20752"
    headers = {
        "User-Agent": "Mozilla/5.0"  # 模擬瀏覽器請求
    }

    # 發送 API 請求
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"❌ 無法獲取新聞資料，HTTP 狀態碼：{response.status_code}")
        return []

    try:
        news_data = response.json()  # 將 API 回應轉為 JSON
    except Exception as e:
        print(f"❌ JSON 解析失敗：{e}")
        return []

    inserted_news = []  # 儲存成功插入的新聞
    source = "UDN"  # 新聞來源
    random_texts = ["前往觀看", "深入瞭解", "來去看看"]  # 隨機內文

    # 處理每筆新聞資料
    for index, news in enumerate(news_data.get("lists", []), start=1):
        title = news.get("title", "無標題")
        link = "https://udn.com" + news.get("url", "")
        content = news.get("content") or random.choice(random_texts)
        photo = "https://example.com/default-image.png"  # 預設圖片
        published_at = news.get("time", None)

        if published_at:
            try:
                published_at = parser.parse(published_at)
            except Exception:
                published_at = datetime.utcnow()
        else:
            published_at = datetime.utcnow()

        # 資料庫查重與插入
        existing = NewsArticle.query.filter_by(url=link).first()
        if not existing:
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


@udn_bp.route("/scrape", methods=["GET"])
def fetch_udn_api():
    """
    提供 API，手動觸發新聞爬取
    Provide an API for manually triggering news scraping
    """
    news = fetch_udn_news()
    return jsonify({"message": f"成功存入 {len(news)} 篇新聞", "data": news}), 200


"""
程式原理總結：
1. 本程式使用 requests 模組向聯合新聞網的指定 API 目標網址發送 GET 請求，並以 UTF-8 編碼解析回應的 HTML/JSON 資料。
2. 使用 BeautifulSoup 解析部分 HTML（雖然此程式主要從 API 取得 JSON 數據），並將數據存入 SQLite 資料庫中。資料庫連線使用 sqlite3 模組建立，並先創建一個名為 news 的資料表，該表包含新聞標題、連結與插入時間（自動生成）。
3. 程式逐筆處理 API 回傳的新聞數據，從每筆資料中提取標題與 URL，並將 URL 補全為完整的連結。
4. 在將新聞數據插入資料庫之前，先利用 SQL 查詢檢查是否已存在相同的新聞（根據連結判斷），以避免重複插入。
5. 成功插入新新聞後，程式提交交易並輸出提示；若新聞已存在，則輸出已存在的提示訊息。
6. 最後，程式關閉資料庫連線，完成新聞資料的爬取與儲存流程。
"""

# ===========================================================
# 註解區（舊版程式碼）
# Code Comment Section (Replaced code from previous version)
# ===========================================================

"""
    ### 被替換的程式碼部分 ###
    1. **SQLite 資料庫操作**：
       原本程式使用 SQLite 進行資料存取，已被替換為 SQLAlchemy 和 MySQL。
       以下為舊程式碼：
       
       # conn = sqlite3.connect("udn_news.db")  # 建立或連接 SQLite 資料庫
       # cursor = conn.cursor()
       # cursor.execute("" "
       #     CREATE TABLE IF NOT EXISTS news (
       #         id INTEGER PRIMARY KEY AUTOINCREMENT,
       #         platform TEXT,
       #         title TEXT UNIQUE,
       #         link TEXT,
       #         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       #     )
       # "" ")
       # conn.commit()
       # try:
       #     cursor.execute("INSERT INTO news (title, link) VALUES (?, ?)", (title, link))
       #     conn.commit()
       # except sqlite3.IntegrityError:
       #     print(f"⚠️ 重複新聞：{title}")
    
    2. **直接列印新聞內容**：
       原程式直接列印每則新聞，未整合至資料庫。
       以下為舊邏輯：
       
       # for index, news in enumerate(news_data.get("lists", []), start=1):
       #     print(f"{index}. {news.get('title', '無標題')}")
       #     print(f"   🔗 {news.get('url')}")

"""