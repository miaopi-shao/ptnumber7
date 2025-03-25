# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 21:28:04 2024

@author: USER
"""

# 新聞雲爬蟲程式，用於從 ETtoday 熱門新聞頁面抓取新聞資訊並存入 SQLite 資料庫


import requests                         # 匯入 requests 模組，用於發送 HTTP 請求
from bs4 import BeautifulSoup           # 匯入 BeautifulSoup，用於解析 HTML 資料
#配合 Flask-SQLAlchemy，統一用 SQLAlchemy 來操作資料庫

# 開啟前後端-連動功能
from flask import Blueprint, jsonify
from datetime import datetime
#因py檔結構並未同一區，更改方法
from models import db, NewsArticle       # 確保 models.py 內部有定義 NewsArticle 模型
from database import db
import random                            # 用於啟用隨機模式

# 定義 Flask Blueprint
ettoday_bp = Blueprint("ettoday", __name__, url_prefix="/ettoday")

def fetch_ettoday_news():
    

    # 設定目標網址與 HTTP 請求頭
    url = "https://www.ettoday.net/news/hot-news.htm"  # 定義要爬取的 ETtoday 熱門新聞頁面 URL
    headers = {                               # 設定 HTTP 請求的 header，模擬瀏覽器行為
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    
    # 發送 GET 請求並取得網頁內容
    response = requests.get(url, headers=headers)  # 使用 GET 方法請求指定 URL，並傳送 headers
    
    # 設定回應編碼為 UTF-8，避免中文亂碼
    response.encoding = 'utf-8'
    
    # 將轉換方式合併解析
    # 解析 HTML
    soup = BeautifulSoup(response.text, "html.parser") # 使用 BeautifulSoup 解析 HTML，指定解析器為 html.parser
    
    # 將方法直接合併進for迴圈內
    # # 抓取新聞列表：使用 CSS 選擇器抓取包含熱門新聞的區塊
    # 設定空串列，並逐筆處理抓取到的新聞資料
    news_list = []
    
    source="ETtoday"                          # 新聞來源
    #for news in news_list:                   # 對每個新聞元素進行迭代處理
    # 將select合併進迴圈內運作
    for news in soup.select(".block.block_1.hot-newslist .piece"):
        
        
        
        # 獲取新聞標題與連結
        title_tag = news.select_one("h3 a")   # 在新聞元素中選取第一個 <h3> 下的 <a> 標籤
        title = title_tag.text.strip() if title_tag else "無標題"  # 取得 <a> 標籤內文字並去除多餘空白，若不存在則設定為 "無標題"
        title = title.replace("\u3000", " ")  # 替換標題中的全形空格為半形空格
        link = title_tag["href"] if title_tag else "無連結"  # 取得 <a> 標籤的 href 屬性作為新聞連結
    
        # 確保新聞連結為完整 URL
        if not link.startswith("https"):      # 若連結不是以 "https" 開頭，表示為相對路徑
            link = "https://www.ettoday.net" + link  # 補全連結，變為絕對 URL
        
        
        
        
        #更改圖片邏輯，有圖片抓圖片
        image_tag = news.select_one("h3 a img")  # 在 <a> 標籤內找到 <img> 標籤
        image_url = image_tag["src"] if image_tag else "https://static.ettoday.net/style/ettoday2017/images/logo_ettoday_v4.png"  # 取得圖片的 src 屬性，若沒有則使用預設新聞圖片（ETtoday 的 logo）     
        # 如果圖片是相對路徑，將其轉換為絕對 URL
        if not image_url.startswith("https"):
            image_url = "https://www.ettoday.net" + image_url    
        
        
        
        # 獲取新聞時間（如果有提供）
        time_tag = news.select_one(".date")   # 在新聞元素中選取 class 為 "date" 的元素
        # 更改值的取用方式
        try:
            published_at = datetime.strptime(time_tag.text.strip(), "%Y/%m/%d %H:%M")
        except ValueError:
            published_at = datetime.utcnow()  # 如果格式錯誤則使用當前時間
        
        
        # 隨機內文的文本參考
        ran_texts = ["前往觀看", "深入瞭解", "來去看看"]
        # 嘗試提取內文摘要
        content_tag = news.find('p')  # 假設 <p> 標籤包含新聞摘要
        if content_tag:
            content = content_tag.text.strip()  # 提取摘要
        else:
            # 如果提取失敗，隨機選擇一段文字作為內文
            content = random.choice(ran_texts)
        
    
        # 檢查新聞是否已存在
        existing_news = NewsArticle.query.filter_by(url=link).first()
        if not existing_news:
            news_entry = NewsArticle(
                title=title,
                content=content,  # 這裡可以額外爬取內文
                source=source,
                url=link,
                image_url=image_url,
                published_at=published_at
            )
            db.session.add(news_entry)
            news_list.append(news_entry)
    
    db.session.commit()
    return news_list

@ettoday_bp.route("/scrape", methods=["GET"])
def fetch_news_api():
    """ 提供 API，手動觸發新聞爬取 """
    news = fetch_ettoday_news()
    return jsonify({"message": f"成功存入 {len(news)} 篇新聞"}), 200

# # 單獨測試
# if __name__ == "__main__":
#     # 測試 Yahoo 和 Google 新聞爬取功能
#     print("測試 Yahoo 新聞爬取...")
#     news = fetch_news_api()
#     print("Yahoo 新聞爬取結果：", news)


"""
程式原理總結：
1. 本程式首先使用 requests 模組向 ETtoday 熱門新聞頁面發送 GET 請求，並將回應內容的編碼設定為 UTF-8，以避免中文亂碼。
2. 利用 BeautifulSoup 解析取得的 HTML 內容，透過 CSS 選擇器 (.block.block_1.hot-newslist .piece) 來抓取包含新聞資訊的區塊。
3. 對於每一筆新聞，程式從中提取標題、連結、新聞時間（若有）以及預設的新聞圖片（ETtoday logo），並確保新聞連結為完整的 URL。
4. 程式接著連接到 SQLite 資料庫，並檢查資料庫中是否已存在該新聞（根據新聞連結判斷）。
5. 若新聞尚未存在，則將新聞資料（包含來源、標題、連結與圖片）插入資料庫並提交交易；否則，跳過該筆新聞。
6. 最後，程式關閉資料庫連線，完成整個新聞爬取與儲存的流程。
"""

# ===========================================================
# 註解區（舊版程式碼）
# Code Comment Section (Replaced code from previous version)
# ===========================================================

"""
### 第一段舊程式碼 ###
#import sqlite3                          # 匯入 sqlite3 模組，用於操作 SQLite 資料庫
    #html = response.text                      # 將回應內容轉換為純文字
    
    # 廢棄的sqlite3方式
    # 連接 SQLite 資料庫
    # conn = sqlite3.connect("news.db")         # 建立或連接到名為 "news.db" 的 SQLite 資料庫
    # cursor = conn.cursor()                    # 建立資料庫游標，用於執行 SQL 語句
    
    
    # # 使用 .select 方法選取 class 為 "piece" 的元素，這些元素位於 class 為 "block block_1 hot-newslist" 的容器中
    # news_list = soup.select(".block.block_1.hot-newslist .piece")  
    
    #time = time_tag.text.strip() if time_tag else "無時間"  # 取得時間文字，若不存在則設定為 "無時間"

         ## 檢查資料庫中是否已存在該新聞（根據連結唯一判斷）
        # cursor.execute("SELECT * FROM news WHERE link = ?", (link,))  # 執行 SQL 查詢，檢查連結是否已存在
        # if cursor.fetchone():                 # 如果查詢結果不為空，表示新聞已存在
        #     print(f"❌ 已存在: {title}")       # 輸出提示訊息：該新聞已存在
        #     print("❌ =======並未新增=======❌ ")
        # else:
    
            # #插入新新聞資料到資料庫
    
            # cursor.execute("INSERT INTO news (platform, title, link, photo) VALUES (?, ?, ?, ?)",
            #                ("ETtoday", title, link, img))  # 執行 SQL INSERT 語句，將新聞來源、標題、連結與圖片資訊插入資料庫
            # conn.commit()                   # 提交資料庫交易，保存資料
            # print("✅=======已新增新聞=======✅")
            # print(f"✅ 新增新聞: {title}")     # 輸出提示訊息：成功新增新聞
    
    
    # # 若未找到新聞列表，則輸出錯誤訊息
    # if not news_list:
    #     print("❌ 找不到新聞列表")
    
    
    # # 關閉 SQLite 資料庫連線
    # conn.close()                             # 關閉與資料庫的連線
    

"""