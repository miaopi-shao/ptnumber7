# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 21:23:02 2024

@author: USER
"""
#====================
# 三立新聞爬蟲程式
#====================

import requests                         # 匯入 requests 模組，用於發送 HTTP 請求
from bs4 import BeautifulSoup           # 從 bs4 模組匯入 BeautifulSoup，用於解析 HTML



from flask import Blueprint, jsonify
from models import db, NewsArticle
from database import db
from datetime import datetime            # 解析時間格式，並替換 datetime.utcnow()內函式
import random                            # 用於啟用隨機模式

setn_bp = Blueprint(' setn', __name__)

def fetch_setn_news():

    # 設定要爬取的 URL
    # URL to scrape
    url = "https://www.setn.com/ViewAll.aspx"  # 指定三立新聞全部新聞頁面的 URL
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        }
    
    
    data = requests.get(url, headers=headers)  # 發送 GET 請求以取得網頁資料
    data.encoding = 'utf-8'                    # 設定回應資料的編碼為 UTF-8
    #data = data.text                           # 轉換回應資料為純文字格式
    
    soup = BeautifulSoup(data.text, 'html.parser')  # 使用 BeautifulSoup 解析 HTML，解析器設定為 html.parser
    
    
    
    all_News = soup.find(id='NewsList')         # 在解析後的 HTML 中尋找 id 為 "NewsList" 的區塊，該區塊包含所有新聞項目
    # 在 allNews 區塊中尋找所有 class 為 "col-sm-12 newsItems" 的 div，代表單筆新聞項目
    if not all_News:
        print("❌ 找不到新聞列表！")
        return []

    # 找到所有單個新聞項目
    news_items = all_News.find_all(class_='col-sm-12 newsItems')
    
    inserted_news = []  # 儲存成功插入的新聞
    
    # 資料庫選取
    source = "SETN"  # 三立新聞
    
    
    for row in news_items:                           # 迭代每一個新聞項目
        
        time_tag = row.find('time')
        if time_tag:
            # 嘗試將時間轉換為 datetime 對象
            try:
                published_at = datetime.strptime(time_tag.text.strip(), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(f"⚠️ 時間解析失敗，使用當前時間: {time_tag.text.strip()}")
                published_at = datetime.utcnow()  # 如果解析失敗，使用當前時間
        else:
            print(f"⚠️ 未發現時間格式，使用當前時間: {time_tag.text.strip()}")
            published_at = datetime.utcnow()  # 如果時間標籤不存在，使用當前時間
            
        a_tags = row.find_all('a')                 # 在每個新聞項目中找到所有 <a> 標籤
        if len(a_tags) < 2:
            continue  # 如果沒有足夠的連結，略過該新聞
        
        item = a_tags[0].text                      # 取得第一個 <a> 的文字（新聞分類，例如：娛樂、健康、政治、生活等）
        
        link = a_tags[1].get('href')               # 從第二個 <a> 標籤中提取新聞連結
        if not link.startswith("http"):
            link = "https://www.setn.com" + link  # 補全相對路徑
        
        photo = "https://attach.setn.com/images/2018_logo_B.png"  # 指定一個預設的圖片 URL
    
        if not ('https' in link):                        # 檢查連結是否包含 "https"，若否則表示為相對路徑
            link = "https://www.setn.com" + link         # 補全連結，使其成為完整的絕對路徑
        title = a_tags[1].text.strip()  # 提取新聞標題    # 取得第二個 <a> 的文字，作為新聞標題
        
        # 隨機內文的文本參考
        ran_texts = ["前往觀看", "深入瞭解", "來去看看"]
        # 嘗試提取內文摘要
        content_tag = row.find('p')  # 假設 <p>改item 標籤包含新聞摘要
        if content_tag:
            content = content_tag.text.strip()  # 提取摘要
        else:
            # 如果提取失敗，隨機選擇一段文字作為內文
            content = random.choice(ran_texts)
        
        
        # 資料庫匯入
        existing = NewsArticle.query.filter_by(url=link).first()  # 查詢是否已存在
        if not existing:
            news_article = NewsArticle(
                title=title,
                content=content,
                source=source,
                image_url=photo,
                category=item,
                url=link,
                published_at=time_tag
            )
            db.session.add(news_article)
            db.session.commit()
            inserted_news.append({"title": title, "link": link})
    return inserted_news
        


@ setn_bp.route("/scrape", methods=["GET"])
def fetch_news_api():
    """ 提供 API，手動觸發新聞爬取 """
    news = fetch_setn_news()
    return jsonify({"message": f"成功存入 {len(news)} 篇新聞"}), 200


"""
這段程式碼的原理如下：
1. 使用 requests 模組從三立新聞的指定 URL 抓取 HTML 網頁資料，並將回應內容的編碼設為 UTF-8。
2. 利用 BeautifulSoup 解析 HTML，從中找到 id 為 "NewsList" 的區塊，該區塊包含所有新聞項目。
3. 透過 find_all 方法，依據 class 名稱 "col-sm-12 newsItems" 取得每筆新聞項目的 DOM 元素。
4. 在迭代每筆新聞時，從每個新聞項目中提取新聞標題、連結與預設圖片（若連結為相對路徑則補全）。
5. 將新聞資料存入 SQLite 資料庫前，先查詢該新聞連結是否已存在，避免重複插入。
6. 如果該新聞不存在，則執行 INSERT 語句將新聞資訊（包括來源、標題、連結、圖片）存入資料庫，並提交交易。
7. 最後關閉資料庫連線，結束爬取過程。

此程式碼的設計可以避免重複儲存新聞，並確保資料的持久化存儲，便於後續資料查詢與處理。
"""


# ===========================================================
# 註解區（舊版程式碼）
# Code Comment Section (Replaced code from previous version)
# ===========================================================


"""
### 第一段舊程式碼 ###
# import requests

# from bs4 import BeautifulSoup

# url = "https://www.setn.com/ViewAll.aspx"

# data = requests.get(url)
# data.encoding= 'utf-8'
# data = data.text

# soup = BeautifulSoup(data,'html.parser')

# allNews = soup.find(id='NewsList')

# div = allNews.find_all(class_='col-sm-12 newsItems')

# for row in div:
#     time = row.find('time').text
#     a = row.find_all('a')
#     item = a[0].text
#     link = a[1].get('href')
    
#     photo = "https://attach.setn.com/images/2018_logo_B.png"
    
#     if not ('https' in link):
#         link = "https://www.setn.com" + link
#     title = a[1].text
#     print(title)
#     print(time)
#     # print(item)
#     print(link)
#     print(photo)
#     print()


"""

"""
### 第二段舊程式碼 ###
#import sqlite3                          # 匯入 sqlite3 模組，用於操作 SQLite 資料庫

# # 建立 SQLite 資料庫連線
# # SQLite database connection
# conn = sqlite3.connect("news.db")
# cursor = conn.cursor()

#    #div = all_News.find_all(class_='col-sm-12 newsItems')

        # =====================================================================================
    #     cursor.execute("SELECT * FROM news WHERE link = ?", (link,))  # 在資料庫中查詢該新聞連結是否已存在
    #     if cursor.fetchone():                 # 如果查詢結果存在資料，則表示該新聞已經儲存過
    #         print(f"❌ 已存在: {title}")       # 輸出提示：新聞已存在
    #         print("❌ =======並未新增=======❌ ")
            
    #     else:
    #         # 將新的新聞資料插入資料庫
    #         cursor.execute("INSERT INTO news (platform, title, link, photo) VALUES (?, ?, ?, ?)",
    #                        ("SETN", title, link, photo))  # 插入新聞來源、標題、連結及圖片資訊
    #         conn.commit()                                 # 提交資料庫交易，保存變更
    #         print(f"✅ 新增新聞: {title}")                # 輸出提示：成功新增新聞
    #         print("✅=======已新增新聞=======✅")
         # =======================================================================================
    
    # # Commit the transaction and close the connection
    # # 提交所有交易並關閉資料庫連線
    # conn.close()                                          # 關閉與 SQLite 資料庫的連線


"""