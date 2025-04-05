# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 21:28:04 2024

@author: USER
"""


#今日新聞

import os
from selenium import webdriver                                    # 匯入 Selenium WebDriver 模組，用於模擬瀏覽器操作
from selenium.webdriver.common.by import By                       # 匯入 By 類別，用於定位 HTML 元素（例如根據標籤、類別、ID 等）
from selenium.webdriver.support.ui import WebDriverWait           # 匯入 WebDriverWait，用於進行顯式等待，確保元素出現
from selenium.webdriver.support import expected_conditions as EC  # 匯入預期條件 (Expected Conditions)，用於判斷特定元素狀態
from selenium.common.exceptions import NoSuchElementException     # 匯入 NoSuchElementException，用於處理找不到元素的例外
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from flask import Blueprint, jsonify
from models import db, NewsArticle
from datetime import datetime
from database import db

nownews_bp = Blueprint('nownews', __name__)

def fetch_nownews_news():

    
    # 設定目標網址（NOWnews 即時新聞）
    url = "https://www.nownews.com/cat/breaking/"  # 定義要爬取的新聞網頁 URL
    
    # 設定 Chrome 瀏覽器為無頭模式
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 啟用無頭模式
    chrome_options.add_argument("--disable-gpu")  # 避免某些系統的圖形錯誤
    chrome_options.add_argument("--window-size=1920x1080")  # 設定虛擬視窗大小
    chrome_options.add_argument("--disable-extensions")  # 禁用擴展以提高穩定性
    chrome_options.add_argument("--no-sandbox")  # 避免沙盒環境限制（部分系統需要）
    chrome_options.add_argument("--disable-dev-shm-usage")  # 避免共享內存空間問題
    
    # 啟動 WebDriver，傳入選項
    # 使用相對路徑取得 chromedriver 的位置，假設 chromedriver 放在專案中的 drivers 資料夾內
    basedir = os.path.abspath(os.path.dirname(__file__))
    chromedriver_path = os.path.join(basedir, 'drivers', 'chromedriver.exe')
    service = Service(executable_path=chromedriver_path)
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 設定顯式等待，最多等待 10 秒鐘
    wait = WebDriverWait(driver, 10)
    
    # 打開目標網頁-已變更為無頭模式
    driver.get(url)
    
    
    # 等待新聞區塊加載完成
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "blk")))  # 顯式等待，直到網頁中出現 class 為 "blk" 的元素
    except Exception as e:                                                  # 如果等待過程中出現例外
        print("❌ 未能載入新聞區塊:", e)                                     # 輸出錯誤訊息
        driver.quit()                                                       # 關閉瀏覽器
        driver.quit()
        return []                                                            # 返回空列表，表示爬取失敗
    
    # 抓取新聞區塊：尋找所有具有 class "blk" 的元素
    articles = driver.find_elements(By.CLASS_NAME, "blk")                   # 取得新聞區塊列表
    inserted_news = []  # 用於存儲成功插入的新聞
    # print(inserted_news)
    # 檢查是否抓取到新聞
    if articles:
        for article in articles:                                            # 逐一處理每一篇新聞
            try:
                # 抓取新聞標題與連結
                title_element = article.find_element(By.TAG_NAME, "a")      # 找到第一個 <a> 標籤，預期包含新聞標題
                title = title_element.text.strip()                          # 取得標題文字並移除首尾空白
                link = title_element.get_attribute("href")                  # 取得連結 URL
    
                
                # 抓取新聞圖片
                try:
                    img_element = article.find_element(By.TAG_NAME, "img")  # 嘗試尋找 <img> 標籤
                    image_url = img_element.get_attribute("src")            # 取得圖片的 src 屬性
                except NoSuchElementException:                              # 若找不到圖片元素
                    image_url = "無圖片"                                    # 設定預設值
                
                # 檢查資料庫中是否已存在
                existing = NewsArticle.query.filter_by(url=link).first()  # 查詢是否已存在
                if not existing:
                    published_at = datetime.utcnow()  # 默認使用當前時間作為發布時間
                    news_article = NewsArticle(
                        title=title,
                        content="",
                        source="NOWnews",
                        image_url=image_url,
                        url=link,
                        published_at=published_at
                    )
                    db.session.add(news_article)
                    db.session.commit()
                    inserted_news.append({"title": title, "link": link})
            
            except Exception as e:
               print(f"❌ 無法處理新聞: {e}")
    print(inserted_news)
    return inserted_news


@nownews_bp.route("/scrape", methods=["GET"])
def fetch_news_api():
    """ 提供 API，手動觸發新聞爬取 """
    news = fetch_nownews_news()
    print(news)
    return jsonify({"message": f"成功存入 {len(news)} 篇新聞"}), 200
nownews_news = fetch_nownews_news()
print(nownews_news)


"""
程式原理總結：
1. 透過 requests 及 Selenium 開啟 NOWnews 的即時新聞網頁。
2. 使用 WebDriverWait 等待網頁中含有 class "blk" 的新聞區塊加載完成。
3. 利用 Selenium 的 find_elements 方法抓取所有新聞區塊，並逐一解析：
   - 從新聞區塊中提取新聞標題與連結，並處理連結的補全（若為相對路徑）。
   - 嘗試抓取新聞圖片，若無圖片則設定預設值 "無圖片"。
4. 使用 SQLite 連線檢查資料庫中是否已存在該新聞（根據連結判斷），若不存在則插入新新聞記錄。
5. 最後，提交所有交易並關閉瀏覽器與資料庫連線。
這個程式利用 Selenium 模擬瀏覽器操作與 BeautifulSoup 解析 HTML，並將爬取到的新聞資料保存到 SQLite 資料庫中，確保新聞資料的持久化存儲與避免重複儲存。
"""

# ===========================================================
# 註解區（舊版程式碼）
# Code Comment Section (Replaced code from previous version)
# ===========================================================

"""
### 第一段舊程式碼 ###
#import sqlite3                                                    # 匯入 sqlite3 模組，用於操作 SQLite 資料庫
#import time                                                       # 匯入 time 模組，用於延時等待
    # 連接 SQLite 資料庫，資料庫檔案名稱為 "news.db"
    # conn = sqlite3.connect("news.db")  # 建立與 news.db 的連線
    # cursor = conn.cursor()             # 創建資料庫游標，後續用來執行 SQL 語句
    
        #廢案，改無頭模式
    # # 啟動 WebDriver，預設使用 Chrome 瀏覽器
    # driver = webdriver.Chrome()                    # 啟動 Chrome 瀏覽器驅動程式
    # # 設定顯式等待，最多等待 10 秒鐘
    # wait = WebDriverWait(driver, 10)               # 建立一個 WebDriverWait 實例，等待特定條件達成
    # # 打開目標網頁
    # driver.get(url)                                # 使用瀏覽器打開指定的新聞網址
    
    
        #conn.close()                                                        # 關閉資料庫連線
        #exit()                                                              # 結束程式執行
        
        
        
    #             # 檢查資料庫中是否已存在該新聞（依據連結判斷）
    #             cursor.execute("SELECT * FROM news WHERE link = ?", (link,))  # 執行 SQL 查詢
    #             if cursor.fetchone():                                         # 如果查詢到資料，表示新聞已存在
    #                 print(f"❌ 已存在: {title}")                              # 輸出提示訊息
    #                 print("❌ =======並未新增=======❌ ") 
                    
    #             else:
    #                 # 若新聞不存在，則插入新新聞到資料庫
    #                 cursor.execute("INSERT INTO news (platform, title, link, photo) VALUES (?, ?, ?, ?)",
    #                                ("NOWnews", title, link, image_url))       # 插入新聞來源、標題、連結與圖片
    #                 conn.commit()                                             # 提交交易，保存變更到資料庫
    #                 print(f"✅ 新增新聞: {title}")                            # 輸出新增成功的訊息
    #                 print("✅=======已新增新聞=======✅")
    
    #         except NoSuchElementException as e:                               # 處理新聞元素中找不到關鍵子元素的情況
    #             print("❌ 找不到新聞元素:", e)                                 # 輸出錯誤訊息
    
    # else:
    #     print("❌ 未找到任何新聞")                                             # 若沒有抓取到任何新聞，輸出提示訊息
    
    
    
    # # 關閉瀏覽器與資料庫連線
    # driver.quit()                   # 關閉 Selenium 控制的瀏覽器
    # conn.close()                    # 關閉 SQLite 資料庫連線
    # # 此盧爬蟲結束

"""