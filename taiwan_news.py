# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 21:23:02 2024

@author: USER
"""
#====================
# 新聞綜合爬蟲程式-三立，TVBS
#====================

import requests                         # 匯入 requests 模組，用於發送 HTTP 請求
from bs4 import BeautifulSoup           # 從 bs4 模組匯入 BeautifulSoup，用於解析 HTML



from flask import Blueprint, jsonify
from datetime import datetime, timezone            # 解析時間格式，並替換 datetime.utcnow()內函式
import random                            # 用於啟用隨機模式

taiwan_news_bp = Blueprint(' taiwan_news ', __name__)


def fetch_setn_news():
    """
    爬取三立新聞網全部新聞，隨機抽取 5 則
    """
    # 設定要爬取的 URL
    url = "https://www.setn.com/ViewAll.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    
    # 發送 GET 請求並解析網頁
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 確認是否找到新聞列表
    all_news = soup.find(id='NewsList')
    if not all_news:
        print("❌ 找不到新聞列表！")
        return []
    
    # 找到所有新聞項目
    news_items = all_news.find_all(class_='col-sm-12 newsItems')
    if not news_items:
        print("❌ 找不到任何新聞項目！")
        return []

    # 儲存成功插入的新聞
    source = "SETN"
    all_fetched_news = []
    
    for row in news_items:
        # 處理發佈時間
        time_tag = row.find('time')
        if time_tag:
            try:
                published_at = datetime.strptime(time_tag.text.strip(), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                published_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            published_at = datetime.now(timezone.utc).replace(tzinfo=None)

        # 取得新聞標題與連結
        a_tags = row.find_all('a')
        if len(a_tags) < 2:
            continue
        category = a_tags[0].text.strip()
        title = a_tags[1].text.strip()
        link = a_tags[1].get('href')
        if not link.startswith("http"):
            link = "https://www.setn.com" + link

        # 設置預設圖片
        photo = "https://cdn.pixabay.com/photo/2025/02/25/10/07/pelican-9430027_1280.jpg"

        # 隨機內文或摘要
        ran_texts = ["前往觀看", "深入瞭解", "來去看看"]
        content_tag = row.find('p')
        content = content_tag.text.strip() if content_tag else random.choice(ran_texts)

        # 模擬插入資料庫（跳過真實資料庫邏輯）
        all_fetched_news.append({
            "title": title,
            "content": content,
            "source": source,
            "category": category,
            "image_url": photo,
            "url": link,
            "published_at": published_at
        })
    
    # 隨機選取 5 則新聞
    return random.sample(all_fetched_news, min(len(all_fetched_news), 5))


def fetch_tvbs_news():
    """
    爬取 TVBS 即時新聞，隨機抽取 5 則
    """
    # 設定目標網址與 Headers
    url = "https://news.tvbs.com.tw/realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    # 發送 GET 請求並解析網頁
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # 定位到新聞列表的區塊
    newslist = soup.find(class_='news_list')
    if not newslist:
        print("❌ 無法找到新聞列表區塊")
        return []

    # 定位到具體新聞內容
    news_section = newslist.find(class_='list')
    if not news_section:
        print("❌ 無法找到具體新聞內容")
        return []

    # 取得所有新聞項目
    li_items = news_section.find_all('li')
    if not li_items:
        print("❌ 無法找到任何新聞項目")
        return []

    all_fetched_news = []
    source = "TVBS"

    for row in li_items:
        # 取得新聞連結與圖片
        link_tag = row.find('a')
        if not link_tag:
            continue
        link = "https://news.tvbs.com.tw" + link_tag.get('href')
        photo = row.find('img').get('data-original') if row.find('img') else "https://pixabay.com/zh/photos/lawn-grass-field-trees-quiet-7728984/"

        # 取得新聞標題與摘要
        title = row.find('h2').text.strip() if row.find('h2') else "無標題"
        content_tag = row.find('p')
        content = content_tag.text.strip() if content_tag else random.choice(["點擊查看更多", "瞭解詳情", "快速瀏覽"])

        # 發布時間處理
        time_tag = row.find('time')
        try:
            published_at = datetime.strptime(time_tag.text.strip(), "%Y-%m-%d %H:%M:%S") if time_tag else datetime.utcnow()
        except ValueError:
            published_at = datetime.now(timezone.utc).replace(tzinfo=None)

        # 儲存抓取的新聞資料
        all_fetched_news.append({
            "title": title,
            "content": content,
            "source": source,
            "image_url": photo,
            "url": link,
            "published_at": published_at
        })

    # 隨機選取 5 則新聞
    return random.sample(all_fetched_news, min(len(all_fetched_news), 5))



# 整合隨機抓取各兩則新聞
def fetch_taiwan_news():
    # 從 BBC 和 Al Jazeera 各抓取兩則新聞
    setn_news = fetch_setn_news()
    tvbs_news = fetch_tvbs_news()
    all_taiwan_news = setn_news + tvbs_news
    fetch_taiwan_news= random.sample(all_taiwan_news, min(len(all_taiwan_news), 5))
    return fetch_taiwan_news


@taiwan_news_bp.route("/scrape", methods=["GET"])
def fetch_news_api():
    """
    提供 API，手動觸發新聞爬取
    """
    news = fetch_taiwan_news
    return jsonify({"message": f"成功存入 {len(news)} 篇新聞", "data": news}), 200


if __name__ == '__main__':
    # 測試輸出
    news = fetch_taiwan_news()
    print("=== 隨機抓取 5 則新聞 ===")
    for idx, article in enumerate(news, start=1):
        print(f"新聞 {idx}:")
        print(f"標題: {article['title']}")
        print(f"連結: {article['url']}")
        print(f"圖片: {article['image_url']}")
        print("==============================")


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