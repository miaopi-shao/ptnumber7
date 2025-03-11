# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:08:53 2025

@author: OAP-0001
"""

# ========================================================
# A. 資料庫模型部分
# ========================================================

# A-1. 匯入必要模組與初始化資料庫 (Flask SQLAlchemy)
from flask_sqlalchemy import SQLAlchemy                      # 用於處理資料庫操作
from datetime import datetime                                # 處理日期和時間
from werkzeug.security import check_password_hash            # 用於密碼比對

# A-2. 其他外部模組（與爬蟲相關）
import requests                                              # 用於發送 HTTP 請求
import os
from bs4 import BeautifulSoup                                # 用於解析 HTML
import sqlite3                                               # 用於 SQLite 操作
import schedule                                              # 用於定時任務排程
import time                                                  # 用於定時任務延時
from fake_useragent import UserAgent                         # 創建虛擬環境

# A-3. 初始化 SQLAlchemy 資料庫對象
db = SQLAlchemy()

# ------------------- 用戶資料庫模型 -------------------
class User(db.Model):
    """ 定義用戶資料模型，用於存儲用戶的帳號、密碼、郵箱等資訊 """
    id = db.Column(db.Integer, primary_key=True)  # A-2-1: 主鍵，唯一識別用戶
    username = db.Column(db.String(100), unique=True, nullable=False)  # A-2-2: 用戶名，唯一且不可為空
    password = db.Column(db.String(200), nullable=False)  # A-2-3: 密碼（存放雜湊值），不能為空
    email = db.Column(db.String(120), unique=True, nullable=True)  # A-2-4: 電子郵件，唯一，可選
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # A-2-5: 用戶創建時間，預設為當前時間
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # A-2-6: 用戶資料更新時間，自動更新
    role = db.Column(db.String(20), default="user")  # A-2-7: 用戶角色，預設為普通用戶

    # A-2-8: 定義一個方法檢查密碼是否正確
    def check_password(self, password):
        """ 檢查密碼是否正確 """
        return check_password_hash(self.password, password)

# ------------------- 分數資料庫模型 -------------------
class Score(db.Model):
    """ 定義遊戲分數資料模型，用於存儲用戶的遊戲分數 """
    id = db.Column(db.Integer, primary_key=True)  # A-3-1: 主鍵，唯一識別分數
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # A-3-2: 與 User 模型關聯 (注意：資料表名稱默認為 user)
    game_name = db.Column(db.String(50), nullable=False)  # A-3-3: 遊戲名稱
    score = db.Column(db.Integer, nullable=False)  # A-3-4: 分數，不能為空
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # A-3-5: 記錄分數時間

# ========================================================
# B. Yahoo 新聞爬蟲及資料儲存部分
# ========================================================

# ------------------------------【Yahoo 新聞爬蟲】------------------------
def fetch_yahoo_news():
    """
    B-1. Yahoo 新聞爬蟲 (擴展版)
    - 爬取標題、圖片、內文、作者、發布時間、連結
    - 資料存入 SQLite 資料庫
    """
    url = "https://tw.news.yahoo.com/"
    
    # 初始化 UserAgent 实例
    ua = UserAgent()
    # 预设的 User-Agent
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    # 尝试使用随机 User-Agent

    # B-1-1: 避免多重執行，使用 lock 檔案控制
    lock_file = "yahoo_news.lock"
    if os.path.exists(lock_file):
        print("⚠️ 其他爬蟲正在運行，跳過本次爬取")
        return []
    open(lock_file, "w").close()  # 建立 lock 檔

    try:
        random_headers = {
            "User-Agent": ua.random
        }
        response = requests.get(url, headers=random_headers, timeout=10)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"❌ 隨機User-Agent請求失敗: {e}")
        
        # 删除锁文件
        try:
            os.remove(lock_file)
        except OSError as oe:
            print(f"❌ 删除锁文件失败: {oe}")
        # 尝试使用预设的 User-Agent
        try:
            response = requests.get(url, headers=default_headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"❌ 使用预设 User-Agent 请求失败: {e}")
            
            # 删除锁文件
            try:
                os.remove(lock_file)
            except OSError as oe:
                print(f"❌ 删除锁文件失败: {oe}")
            return None
 
    
    # B-1-2: 解析 HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    # B-1-3: 根據 HTML 結構抓取新聞區塊
    articles = soup.find_all('li', class_='js-stream-content')
    if not articles:
        print("⚠️ 找不到新聞區塊，可能是 HTML 結構變更")
        os.remove(lock_file)
        return []
    
    data_storage = []  # B-1-4: 初始化儲存資料列表
    
    # B-1-5: 迴圈處理每篇新聞
    for article in articles:
        title_tag = article.find('h3')
        a_tag = title_tag.find('a') if title_tag else None
        title = title_tag.get_text(strip=True) if title_tag else "無標題"
        link = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
        if link and link.startswith('/'):
            link = "https://tw.news.yahoo.com" + link  # 處理相對路徑

        img_tag = article.find('img')
        image = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None

        # B-1-6: 爬取新聞內頁詳細內容
        content, author, published_time = fetch_news_details(link) if link else (None, None, None)

        data_storage.append({
            'title': title,
            'image': image,
            'content': content,
            'author': author,
            'published_time': published_time,
            'url': link,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    print(f"✅ 成功抓取 {len(data_storage)} 篇新聞")
    if data_storage:
        print("📌 最後一篇新聞資料：", data_storage[-1])
    
    os.remove(lock_file)  # B-1-7: 移除 lock 檔
    return data_storage

def fetch_news_details(url):
    """
    B-2. 進入新聞內頁，爬取完整內文、作者與發布時間
    """
    if not url:
        return None, None, None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # B-2-1: 抓取內文（通常是 <p> 標籤內的內容）
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text(strip=True) for p in paragraphs]) if paragraphs else None

        # B-2-2: 抓取作者（根據 HTML 結構調整）
        author_tag = soup.find('span', class_='caas-attr-author')
        author = author_tag.get_text(strip=True) if author_tag else "未知作者"

        # B-2-3: 抓取發布時間（通常在 <time> 標籤）
        time_tag = soup.find('time')
        published_time = time_tag['datetime'] if time_tag and 'datetime' in time_tag.attrs else None

        return content, author, published_time
    except requests.RequestException as e:
        print(f"❌ 內頁請求失敗: {e}")
        return None, None, None

def save_all_to_db(data_storage):
    """
    B-3. 將爬取的新聞資料存入 SQLite 資料庫，並保留最新 100 筆
    """
    try:
        conn = sqlite3.connect('news.db', timeout=30)
        cursor = conn.cursor()

        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA cache_size=-64000;")

        # B-3-1: 建立新聞資料表（如果尚不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                image TEXT,
                content TEXT,
                author TEXT,
                published_time TEXT,
                url TEXT NOT NULL UNIQUE,
                date TEXT NOT NULL
            )
        ''')

        count = 0
        for data in data_storage:
            try:
                cursor.execute("INSERT OR REPLACE INTO news (title, image, content, author, published_time, url, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (data['title'], data['image'], data['content'], data['author'], data['published_time'], data['url'], data['date']))
                count += 1
            except sqlite3.IntegrityError:
                continue  # 避免重複資料

        # B-3-2: 保留最新 100 筆資料，其餘刪除
        cursor.execute("DELETE FROM news WHERE id NOT IN (SELECT id FROM news ORDER BY date DESC LIMIT 100)")
        conn.commit()
        print(f"✅ 成功存入 {count} 篇新聞")
    except sqlite3.OperationalError as e:
        print(f"❌ 資料庫錯誤: {e}")
    finally:
        conn.close()

def fetch_and_save():
    """
    B-4. 執行 Yahoo 新聞爬蟲並將資料存入資料庫
    """
    data_storage = fetch_yahoo_news()
    if data_storage:
        save_all_to_db(data_storage)

def schedule_task():
    """
    B-5. 定時任務：每小時爬取一次 Yahoo 新聞
    """
    schedule.every(1).hours.do(fetch_and_save)
    # B-5-1: 進入無限循環，定時執行爬蟲任務
    while True:
        schedule.run_pending()
        time.sleep(1)

# ========================================================
# C. 主程序運行順序
# ========================================================

if __name__ == "__main__":
    # C-1: 初次執行爬蟲，取得新聞資料並存入資料庫
    data = fetch_yahoo_news()
    if data:
        save_all_to_db(data)
    # C-2: 開始定時任務（每小時執行一次爬蟲）
    schedule_task()

"""
【整體程式運作順序說明】

A. 資料庫模型部分（A-1 ~ A-3）
    A-1: 匯入必要模組並初始化資料庫
    A-2: 定義 User 模型（用於處理用戶資料與密碼驗證）
    A-3: 定義 Score 模型（用於儲存遊戲分數）

B. Yahoo 新聞爬蟲部分（B-1 ~ B-5）
    B-1: fetch_yahoo_news()：爬取 Yahoo 新聞列表與基本資料
    B-2: fetch_news_details(url)：進入新聞內頁爬取完整內文、作者、發布時間
    B-3: save_all_to_db(data_storage)：將爬取的新聞資料存入 SQLite 資料庫，並保留最新 100 筆
    B-4: fetch_and_save()：整合爬蟲與存儲功能
    B-5: schedule_task()：每小時定時執行爬蟲任務（併行持續運行）

C. 主程序（C-1, C-2）
    C-1: 初次爬取新聞資料並存入資料庫
    C-2: 啟動 schedule_task() 進入定時爬蟲循環

【與其他檔案的聯繫】
- app.py：使用 User 與 Score 模型處理用戶註冊、登入、查詢與遊戲分數儲存。
- auth.js：前端處理用戶註冊、登入，透過 POST 請求與後端互動。
- index.html：前端頁面顯示註冊、登入表單，與 auth.js 配合傳送資料。
- tetris_game.html、parkour_game.html：遊戲頁面用來提交分數，後端使用 Score 模型儲存數據。
"""
