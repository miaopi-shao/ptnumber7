# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 21:28:04 2024

@author: USER
"""

# 程式名稱:cts.py
# ===============================
# 華視新聞爬蟲程式
# CTS News Scraper
# ===============================

import requests  # 匯入 requests 模組，用於發送 HTTP 請求
from bs4 import BeautifulSoup  # 匯入 BeautifulSoup，用於解析 HTML
from dateutil import parser  # 匯入日期解析器，處理 ISO 時間格式
from datetime import datetime  # 用於時間處理
from flask import Blueprint, jsonify
from models import db, NewsArticle  # 引入資料庫與新聞模型
import random  # 啟用隨機模式，生成默認內容
from database import db

# 初始化 Blueprint
cts_bp = Blueprint('cts', __name__)

def fetch_cts_news():
    """
    從華視新聞網爬取即時新聞
    Fetch real-time news from CTS News website
    """
    url = "https://news.cts.com.tw/real/index.html"  # 華視新聞網址
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}

    # 發送 HTTP GET 請求
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')  # 解析 HTML
    
    # 定位新聞列表區塊
    news_section = soup.find(id='newslist-top')

    inserted_news = []  # 成功新增新聞的列表
    source = "CTS"  # 新聞來源
    
    # 隨機內文文本
    random_texts = ["點擊查看全文", "探索新聞詳情", "快速瞭解更多"]

    if news_section:
        articles = news_section.find_all('a')  # 找到所有新聞<a>標籤

        for row in articles:
            # 提取新聞標題
            title = row.get('title') or (row.find('h2') or row.find('p')).text.strip() if (row.find('h2') or row.find('p')) else "無標題"
            
            # 提取新聞連結
            link = row.get('href')
            if not link or link == "#":
                continue
            if not link.startswith("http"):
                link = "https://news.cts.com.tw" + link
            
            # 提取新聞圖片
            img_tag = row.find('img')
            photo = img_tag.get('src') or img_tag.get('data-src') if img_tag else "https://www.cts.com.tw/images/2018cts/cts-logo.png"

            # 處理發佈時間
            time_tag = row.find('time', class_="hvbAAd")
            published_at = parser.parse(time_tag['datetime']) if time_tag and 'datetime' in time_tag.attrs else datetime.utcnow()
            
            # 提取內文摘要
            content_tag = row.find('p')
            content = content_tag.text.strip() if content_tag else random.choice(random_texts)

            # 檢查是否已存在
            existing = NewsArticle.query.filter_by(url=link).first()
            if not existing:
                # 新增新聞到資料庫
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


@cts_bp.route("/scrape", methods=["GET"])
def fetch_news_api():
    """
    提供 API 以手動觸發新聞爬取
    Provide an API for manually triggering news scraping
    """
    news = fetch_cts_news()
    return jsonify({"message": f"成功存入 {len(news)} 篇新聞", "data": news}), 200


"""
程式原理總結：
這段程式碼主要的功能是爬取華視新聞網的首頁內容並將新聞資料存入 SQLite 資料庫。其運作流程如下：
1. 利用 requests 模組發送 HTTP GET 請求，取得目標 URL 的 HTML 內容。
2. 使用 BeautifulSoup 解析取得的 HTML，尋找 id 為 "newslist-top" 的區塊，該區塊包含所有新聞項目。
3. 在找到的新聞列表中，依據每個 <a> 標籤提取新聞標題（從 title 屬性或內部的 <h2>/<p> 標籤）、新聞連結和新聞圖片（從 <img> 標籤）。
4. 為了避免重複儲存新聞，程式會先檢查資料庫中是否已存在該新聞（透過連結作為唯一標識）。
5. 若新聞不存在，則將新聞來源（CTS）、標題、連結及圖片資訊插入資料庫，並提交交易。
6. 最後，關閉資料庫連線，結束爬蟲程式。
"""


# ===========================================================
# 註解區（舊版程式碼）
# Code Comment Section (Replaced code from previous version)
# ===========================================================

"""
### 第一段舊程式碼 ###
原因：該段程式用於提取新聞標題、連結和圖片，邏輯尚未整合資料庫操作，並且有部分重複工作已被優化。

# if news_section:
#     articles = news_section.find_all('a')

#     for row in articles:
#         # 取得標題
#         title = row.get('title')
#         if not title:  # 如果 a 標籤內沒有 title，從內部 h2 或 p 抓
#             title_tag = row.find('h2') or row.find('p')
#             title = title_tag.text.strip() if title_tag else None

#         # 取得連結
#         link = row.get('href')
#         if not link or link == "#":  # 過濾無效連結
#             continue
#         if not link.startswith("http"):
#             link = "https://news.cts.com.tw" + link  # 補全網址
#         img_tag = row.find('img')
#         if img_tag:
#             photo = img_tag.get('src') or img_tag.get('data-src') or "https://www.cts.com.tw/images/2018cts/cts-logo.png"
#         else:
#             photo = "https://www.cts.com.tw/images/2018cts/cts-logo.png"

#         # 只顯示有標題或圖片的新聞
#         if title or photo:
#             print(f"標題: {title if title else '無標題'}")
#             print(f"圖片: {photo}")
#             print(f"連結: {link}")
#             print("-" * 50)

# else:
#     print("找不到新聞列表")
"""

"""
### 第二段舊程式碼 ###
原因：此段程式為單純的 HTTP 請求測試，已包含在新的新聞爬取函式中，具備更高效能與錯誤處理能力。

# import requests
# from bs4 import BeautifulSoup

# url = "https://news.cts.com.tw/real/index.html"

# # 發送請求
# response = requests.get(url)
# response.encoding = 'utf-8'
# html = response.text

# # 解析 HTML
# soup = BeautifulSoup(html, 'html.parser')

# # 找到新聞列表
# news_section = soup.find(id='newslist-top')
"""

"""
### 第三段舊程式碼 ###
原因：原先基於 SQLite 的邏輯已完全移除，現在改用 MySQL 與 SQLAlchemy 處理資料庫交互，提升維護性與效率。

# # 連接 SQLite 資料庫
# conn = sqlite3.connect("news.db")
# cursor = conn.cursor()

# # 建立 news 資料表（如果不存在的話）
# cursor.execute('''CREATE TABLE IF NOT EXISTS news (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     platform TEXT,
#                     title TEXT,
#                     time TEXT,
#                     link TEXT,
#                     photo TEXT)''')

# # 找到新聞列表所在區塊
# news_section = soup.find(id='newslist-top')

# # 插入新聞邏輯（已整合至新程式碼中）
# cursor.execute("INSERT INTO news (platform, title, link, photo) VALUES (?, ?, ?, ?)", ("CTS", title, link, photo))
# conn.commit()
# conn.close()


    
        # =========================================================================================
    # # 連接 SQLite 資料庫
    # conn = sqlite3.connect("news.db")       # 連接或建立名為 news.db 的 SQLite 資料庫
    # cursor = conn.cursor()                  # 創建游標以便執行 SQL 語句
    
    # # 建立 news 資料表（如果不存在的話）-1.自動遞增的主鍵 2.新聞來源平台 3.新聞標題 4.新聞時間 5.新聞連結（唯一標識）
    # cursor.execute('''CREATE TABLE IF NOT EXISTS news (
    #                     id INTEGER PRIMARY KEY AUTOINCREMENT,  
    #                     platform TEXT,                          
    #                     title TEXT,                             
    #                     time TEXT,                              
    #                     link TEXT,                              
    #                     photo TEXT)''')                        # 新聞圖片 URL
    
    # # 找到新聞列表所在區塊，根據 id="newslist-top"
    # news_section = soup.find(id='newslist-top')  # 在解析的 HTML 中尋找 id 為 "newslist-top" 的元素
        #==========================================================================================
    
    

        #=================================================================================
    #         # 檢查資料庫中是否已存在相同的新聞（根據連結判斷）
    #         cursor.execute("SELECT * FROM news WHERE link = ?", (link,))  # 執行 SQL 查詢檢查是否已有此連結的新聞
    #         if cursor.fetchone():  # 如果查詢結果不為空，表示該新聞已存在
    #             print(f"❌ 已存在: {title}")  # 輸出提示，該新聞已存在
    #             print("❌ =======並未新增=======❌ ")
                
    #         else:
    #             # 插入新新聞資料到資料庫
    #             cursor.execute("INSERT INTO news (platform, title, link, photo) VALUES (?, ?, ?, ?)",
    #                            ("CTS", title, link, photo))  # 將新聞來源、標題、連結與圖片插入資料庫
    #             conn.commit()  # 提交變更，保存新新聞資料
    #             print(f"✅ 新增新聞: {title}")  # 輸出新增成功的提示
    #             print("✅=======已新增新聞=======✅")
    #         if not cursor.fetchone():  # 如果該新聞不存在
    #             cursor.execute("INSERT INTO news (platform, title, link, photo) VALUES (?, ?, ?, ?)",
    #                            ("CTS", title, link, photo))
    #             conn.commit()
    #             inserted_news.append({"title": title, "link": link})  # 添加成功插入的新聞
    #     conn.close()
    #     return inserted_news  # 返回成功插入的新聞列表
    
    # else:
    #     print("❌ 找不到新聞列表")  # 如果未找到新聞列表區塊，輸出錯誤提示
    
    # # 關閉 SQLite 連線
    # conn.close()  # 關閉與 SQLite 資料庫的連線
        #==================================================================================

"""