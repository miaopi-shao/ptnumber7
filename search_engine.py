# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:02:11 2025

@author: OAP-0001
"""

# search_engine.py 負責處理站內搜尋邏輯，並提供給 Flask 來處理請求。

from flask import Blueprint, request, render_template
"""
import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime
import sqlite3
"""


# 建立 Flask Blueprint，負責處理站內搜尋
search_bp = Blueprint('search', __name__)
internal_search_bp = Blueprint('internal_search', __name__)

#------------------------【Flask 站內搜尋功能】------------------------
@search_bp.route('/internal_search', methods=['GET'])
def internal_search():
    """
    用戶在搜尋欄輸入關鍵字後，觸發此函式來處理站內搜尋。
    """

    # 31-1: 取得用戶的搜尋請求 (query: 關鍵字, category: 分類)
    query = request.args.get('query', '').strip()
    category = request.args.get('category', 'all')

    # 32-1: 引入站內搜尋函式 (確保 search_internal 已經被實作)
    from search_engine import search_internal

    # 33-1: 如果有輸入關鍵字，則執行站內搜尋
    if query:
        results = search_internal(query)  # 執行內部搜尋
        return render_template('search_results.html', query=query, results=results)

    # 34-1: 若未輸入關鍵字，則回傳空結果
    return render_template('search_results.html', query=query, category=category, results=[])



"""
#------------------------【Yahoo 新聞爬蟲】------------------------

# 儲存爬取的資料 (這裡是簡單儲存為清單，實際可以存入資料庫)
data_storage = []

def fetch_yahoo_news():
    ""
    31-2: 爬取 Yahoo 新聞首頁，取得最新新聞標題及連結。
    ""

    url = "https://tw.news.yahoo.com/"  # Yahoo 台灣新聞首頁
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 32-2: 抓取 Yahoo 新聞標題和其對應的連結
    articles = soup.find_all('a', {'class': 'Fw(b)'})  # 假設這是新聞標題的 CSS 類名

    for article in articles:
        title = article.get_text()  # 取得新聞標題
        link = article['href']  # 取得連結

        # 33-2: 若為相對網址，補全成絕對網址
        if link.startswith('/'):
            link = "https://tw.news.yahoo.com" + link

        # 34-2: 將爬取的新聞存入 data_storage 清單
        data_storage.append({
            'title': title,
            'url': link,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    print(f"抓取時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 成功抓取 {len(articles)} 篇文章")
    print("資料已更新：", data_storage[-1])  # 顯示最後一筆更新資料


def save_to_db(title, url, date):
    try:
        ""
        35-2: 將爬取到的新聞資料存入 SQLite 資料庫。
        ""
    
        # 36-2: 連接到 SQLite 資料庫 (若無則會自動創建)
        conn = sqlite3.connect('news.db', timeout=30)#讓程式等待 30 秒後再嘗試存取
        cursor = conn.cursor()
    
        # 37-2: 檢查資料庫內是否已經存在該 URL
        cursor.execute("SELECT 1 FROM news WHERE url = ?", (url,))
        exists = cursor.fetchone()  # 若已存在，回傳 (1,)
        
        # 38-2: 確保資料表 news 存在 (如果尚未建立則創建)
        cursor.execute('''CREATE TABLE IF NOT EXISTS news (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT,
                            url TEXT UNIQUE,  -- 設定 URL 為唯一，避免重複插入
                            date TEXT)''')
    
    
        # 39-2: 只有當 URL 不存在時，才執行插入
        if not exists:
            cursor.execute("INSERT INTO news (title, url, date) VALUES (?, ?, ?)", (title, url, date))
            conn.commit()  # 確保資料儲存
            print(f"✅ 資料已存入：{title}")
        else:
            print(f"⚠️ 跳過重複資料：{title}")
    
    # 40-2: 關閉資料庫連線
    except sqlite3.OperationalError as e:
        print(f"❌ 資料庫錯誤: {e}")
    
    finally:
        conn.close()  # 確保無論如何都關閉資料庫


# 每小時執行一次爬蟲並儲存資料到資料庫
def fetch_and_save():
    ""
    41-2: 進行 Yahoo 新聞爬取，並存入資料庫。
    ""
    fetch_yahoo_news()  # 執行爬蟲抓取
    save_to_db()  # 儲存資料到資料庫

def schedule_task():
    ""
    42-2: 設定定時執行爬蟲，每小時抓取一次 Yahoo 新聞。
    ""
    
    schedule.every(1).hours.do(fetch_and_save)  # 每小時執行一次爬蟲

    while True:
        schedule.run_pending()  # 43-2: 執行排程中的任務
        time.sleep(1)  # 44-2: 每秒檢查一次是否有待執行的任務

#------------------------【程式進入點】------------------------

if __name__ == "__main__":
    ""
    這段程式碼的主要作用：
    1. 伺服器啟動時，先爬取一次 Yahoo 新聞 (44-2)。
    2. 之後開始定時每小時爬取一次 (45-2)。
    3. Flask 伺服器負責處理用戶請求 (站內搜尋) (46-1)。
    ""
    
    fetch_yahoo_news()  # 45-2: 首次執行 Yahoo 新聞爬取
    schedule_task()  # 46-2: 啟動 Yahoo 爬蟲排程
"""