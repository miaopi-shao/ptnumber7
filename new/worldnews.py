# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 21:23:02 2024

@author: USER
"""
# 程式名稱:worldnews.py
# ===============================
# W 世界新聞網 網頁動態爬蟲
# W World News Dynamic Web Scraper
# ===============================

import os
from selenium import webdriver  # 匯入 Selenium WebDriver，用於瀏覽器自動化
# Import Selenium WebDriver for browser automation
from selenium.webdriver.common.by import By  # 使用 By 模組定位元素
# Use By module to locate elements
from selenium.webdriver.support.ui import WebDriverWait  # 匯入 WebDriver 顯式等待功能
# Import WebDriver explicit wait functionality
from selenium.webdriver.support import expected_conditions as EC  # 匯入條件，用於等待特定狀態
# Import conditions for waiting on specific states
from selenium.webdriver.chrome.options import Options  # 設定 Chrome 瀏覽器選項
# Configure Chrome browser options
from selenium.webdriver.chrome.service import Service  # 用於啟動 WebDriver 服務
# Used to start WebDriver service
import time  # 用於設定頁面等待時間
# For setting page wait times
from flask import Blueprint, jsonify
from models import db, NewsArticle  # 從 models 匯入資料庫與新聞模型
from database import db
# Import database and NewsArticle model from models.py
from dateutil import parser  # 用於解析日期
# For date parsing
from datetime import datetime  # 處理時間格式
# For date-time handling
import random  # 用於生成隨機內容
# For generating random content

# 初始化 Blueprint
# Initialize Blueprint
worldnews_bp = Blueprint('worldnews', __name__, url_prefix="/worldnews")


def fetch_worldnews_news():
    """
    爬取世界新聞網的即時新聞
    Fetch real-time news from World News website
    """
    max_news_count = 5  # 設定最大抓取數量限制
    news_count = 0  # 初始化已抓取新聞數量
    inserted_news = []  # 儲存成功插入的新聞
    source = "worldnews"  # 新聞來源
    random_texts = ["前往觀看", "深入瞭解", "來去看看"]  # 隨機內文
    today_date = datetime.today().strftime('%Y-%m-%d')  # 取得今天日期

    # 設定 Chrome 瀏覽器選項
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 無頭模式
    chrome_options.add_argument("--disable-gpu")  # 停用 GPU 加速
    chrome_options.add_argument("--window-size=1920x1080")  # 設定視窗大小
    chrome_options.add_argument("--no-sandbox")  # 停用沙箱模式
    chrome_options.add_argument("--disable-dev-shm-usage")  # 避免內存限制

    # 設定 WebDriver 路徑
    basedir = os.path.abspath(os.path.dirname(__file__))
    chromedriver_path = os.path.join(basedir, 'drivers', 'chromedriver.exe')
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 設定目標網址
    url = "https://www.worldjournal.com/wj/cate/breaking"  # 世界新聞網址
    driver.get(url)  # 打開網頁
    time.sleep(3)  # 等待初始頁面加載完成

    # 滾動抓取新聞
    while news_count < max_news_count:
        print("頁面滾動中...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 滾動到底部
        time.sleep(3)

        # 獲取新聞列表
        articles = driver.find_elements(By.CLASS_NAME, 'subcate-list__content-big')
        for item in articles:
            try:
                if news_count >= max_news_count:
                    print("已達到抓取數量上限")
                    break

                # 獲取圖片
                img = item.find_element(By.CLASS_NAME, 'lazyloaded')
                photo = img.get_attribute('src')

                # 獲取標題
                title = item.find_element(By.CLASS_NAME, 'subcate-list__link__title').text.strip()

                # 獲取連結
                alink = item.find_element(By.TAG_NAME, 'a')
                link = alink.get_attribute('href')

                # 獲取時間
                time_element = item.find_element(By.CLASS_NAME, 'subcate-list__time')
                news_time = time_element.text.strip() if time_element else "無時間資訊"

                # 解析時間
                try:
                    time_tag = parser.parse(news_time)
                except Exception:
                    time_tag = datetime.utcnow()

                # 確認是否為當天新聞
                if today_date in time_tag.strftime('%Y-%m-%d'):
                    content = random.choice(random_texts)  # 隨機生成內文
                    existing = NewsArticle.query.filter_by(url=link).first()  # 查詢是否已存在
                    if not existing:
                        news_article = NewsArticle(
                            title=title,
                            content=content,
                            source=source,
                            image_url=photo,
                            url=link,
                            published_at=time_tag
                        )
                        db.session.add(news_article)
                        db.session.commit()
                        inserted_news.append({"title": title, "link": link})

                news_count += 1

            except Exception as e:
                print(f"抓取錯誤: {e}")

    # 關閉瀏覽器
    driver.quit()
    return inserted_news


@worldnews_bp.route("/scrape", methods=["GET"])
def fetch_worldnews_api():
    """
    提供 API 以手動觸發新聞爬取
    Provide an API for manually triggering news scraping
    """
    news = fetch_worldnews_news()
    return jsonify({"message": f"成功存入 {len(news)} 篇新聞", "data": news}), 200


# ===========================================================
# 註解區（舊版程式碼）
# Code Comment Section (Replaced code from previous version)
# ===========================================================

"""
### 被替換的程式碼部分 ###
1. **滾動與等待邏輯**：
   原本使用簡單的滾動方式，未加入上限限制且頁面滾動邏輯過於冗長。
   以下為舊邏輯：
   
   # while True:
   #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
   #     time.sleep(3)
   #     current_height = driver.execute_script("return document.body.scrollHeight")
   #     if current_height == previous_height:
   #         break
   #     previous_height = current_height

2. **SQLite 資料庫操作**：
   原本使用 SQLite 游標進行資料儲存與查重，已改用 SQLAlchemy 和 MySQL。
   以下為舊邏輯：
   
   # conn = sqlite3.connect("news.db")
   # cursor = conn.cursor()
   # cursor.execute('''CREATE TABLE IF NOT EXISTS news (
   #                     id INTEGER PRIMARY KEY AUTOINCREMENT,
   #                     platform TEXT,
   #                     title TEXT,
   #                     time TEXT,
   #                     link TEXT,
   #                     photo TEXT)''')
   # cursor.execute("INSERT INTO news (platform, title, link, photo) VALUES (?, ?, ?, ?)", ("worldnews", title, link, photo))
   # conn.commit()
   # conn.close()

3. **未使用的變數與代碼**：
   原本有部分未被使用的變數或直接列印的新聞內容，已被移除或重構。
   以下為舊邏輯：
   
   # print(f"標題: {title}")
   # print(f"圖片: {photo}")
   # print(f"連結: {link}")
   # print(f"時間: {news_time}")
   # print("-" * 50)
"""