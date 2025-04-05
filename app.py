# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:07:53 2025

@author: OAP-0001
"""

#fcaibi@gmail.com 導師信箱

#整合用主程式
# Main program for project integration
# 引入 Flask 框架，用於建立 Web 應用
# Import Flask framework for building web applications
from flask import Flask, render_template, jsonify  # 程式庫的模組，提供輕量級的 Web 服務功能
import random

# 匯入資料庫模型，管理數據結構
# Import database models to manage data structures
from models import User, AuthUser, Score, NewsArticle    # 專案的模型模組，定義用戶、分數和新聞的數據表結構
print(User)  # 應該輸出 <class 'models.User'>，確認模型匯入成功
print(Score)  # 應該輸出 <class 'models.Score'>，確認模型匯入成功
print(NewsArticle)  # 應該輸出 <class 'models.NewsArticle'>，確認模型匯入成功

# 引入 HTTP 請求模組，用於與外部 API 通訊
# Import HTTP request library for external API communication
import requests  # 程式庫的模組，用於執行 HTTP 請求操作
from flask_mail import Mail
from flask_cors import CORS 

# ========================================================
# 專案模組匯入，所有Blueprint 模組
# Import all Blueprint modules for modular routing within the project
# ========================================================
from auth import auth_bp                                  # 負責帳戶資訊
from external_search import external_search_bp            # 負責站外搜尋
from news_fetch import news_fetch_bp                      # 負責站內搜尋
from search_engine import search_engine_bp
from user_scrape import user_scrape_bp
from weather import weather_bp                            # 負責氣象資訊
from weather_news import weather_news_bp                  # 負責氣象新聞
from cts import cts_bp
from ettoday import ettoday_bp
from ettoday2 import ettoday2_bp
from google import google_bp
from nownews import nownews_bp
from nownews2 import nownews2_bp
from setn import setn_bp
from tvbs import tvbs_bp
from worldnews import worldnews_bp
from udn import udn_bp
from yahoo import yahoo_bp
from database import mail
from scrape_news import scrape_news_bp                     # 負責運行定時任務    
from datetime import timedelta
from youtube import youtube_search

import Page_Noiser                                         # 三網站爬蟲混合展示
import udn2                                                # 聯合新聞網爬蟲


from game import save_score_bp

# ========================================================
# 初始化應用及配置
# Application initialization and configuration
# ========================================================

# 建立 Flask 應用程序的實例
# Create a Flask application instance
app = Flask(__name__)  # 程式庫的模組，主應用程序初始化

# 匯入擴展功能，集中管理應用
# Import extensions for centralized management
from database import login_manager, init_extensions, db  # 專案的模組，用於統一初始化資料庫、登入管理等擴展功能
from dotenv import load_dotenv  # 程式庫的模組，用於加載 .env 環境變數
import os  # 程式庫模組，負責操作系統功能（例如文件路徑）
# 加載 .env 文件中的變數
# Load environment variables from .env file
load_dotenv()  # 調用程式庫模組，用於將 .env 文件中的變數載入到系統環境

# 嘗試加載 .env 文件
if load_dotenv():
    print("✅ .env 文件成功加載")
else:
    print("⚠️ 無法加載 .env 文件，請檢查路徑或文件格式")

# 配置多類型資料庫綁定
FLASK_ENV = os.environ.get("FLASK_ENV", "local_mysql")#-----------------------------------------------------注意替換-------------------------------
print("*********************************")
print(f"FLASK_ENV 設定為: {FLASK_ENV}")
print("*********************************")

if FLASK_ENV == "production":
    DATABASE_URI = os.getenv("AWS_MAIN_URI")
    print("使用雲端 MySQL 資料庫")
elif FLASK_ENV == "local_mysql":
    DATABASE_URI = os.getenv("DB_MAIN_URI")
    print("使用本地 MySQL 資料庫")
elif FLASK_ENV == "development":
    DATABASE_URI = os.getenv("DB_MAIN_URI")
    print("使用本地 MySQL 資料庫")
else:
    raise ValueError("未定義的 FLASK_ENV，請檢查環境變數")
    
# 統一配置 Flask 的 SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

# 綁定多個資料庫（依據環境設定）
if FLASK_ENV == "production":
    # 雲端 MySQL 資料庫
    app.config['SQLALCHEMY_BINDS'] = {
        'user': os.getenv('AWS_USER_URI'),
        'auth': os.getenv('AWS_AUTH_URI'),
        'game': os.getenv('AWS_GAME_URI'),
        'news': os.getenv('AWS_NEWS_URI'),
    }
    print("綁定至雲端 MySQL 資料庫")
elif FLASK_ENV == "local_mysql":
    # 本地 MySQL 資料庫
    app.config['SQLALCHEMY_BINDS'] = {
        'user': os.getenv('DB_USER_URI'),
        'auth': os.getenv('DB_AUTH_URI'),
        'game': os.getenv('DB_GAME_URI'),
        'news': os.getenv('DB_NEWS_URI'),
    }
    print("綁定至本地 MySQL 資料庫")
else:
    # 預設綁定本地 MySQL（包含開發環境）
    app.config['SQLALCHEMY_BINDS'] = {
        'user': os.getenv('DB_USER_URI'),
        'auth': os.getenv('DB_AUTH_URI'),
        'game': os.getenv('DB_GAME_URI'),
        'news': os.getenv('DB_NEWS_URI'),
    }
    print("綁定至本地 MySQL（默認環境） 資料庫")


# 設定主資料庫與多綁定資料庫-因應雲端環境更改2025/03/29
# Set main database and multi-bind databases
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_MAIN_URI') # 程式庫設定，主資料庫連接 URI
# app.config['SQLALCHEMY_BINDS'] = {  # 程式庫設定，其他綁定資料庫的連接 URI
#     'user': os.getenv('DB_USER_URI'),  # 專案資料庫，預設執行檔案
#     'auth': os.getenv('DB_AUTH_URI'),  # 專案資料庫，帳號相關資料
#     'game': os.getenv('DB_GAME_URI'),  # 專案資料庫，遊戲分數相關資料
#     'news': os.getenv('DB_NEWS_URI')   # 專案資料庫，新聞爬蟲相關資料 
# }

CORS(app, supports_credentials=True)
# 配置 Session
app.config["SESSION_PERMANENT"] = True  # 設置 Session 為永久
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)  # Session 有效期為 7 天
app.config["SESSION_TYPE"] = "filesystem"  # 使用文件系統來存儲 Session

app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # 替換成安全的 JWT 密鑰


# 調整資料庫文件的讀寫權限-本地開發時
# Adjust read/write permissions for database files
if FLASK_ENV in ["development", "local_mysql"]:
    db_files = ["user.db", "auth.db", "game.db", "new.db"]  # 專案資料庫文件列表
    for db_file in db_files:
        db_path = os.path.join(DATABASE_URI, db_file)  # 拼接文件路徑
        if os.path.exists(db_path):
            os.chmod(db_path, 0o777)  # 修改文件的權限
            print(f"已更改權限: {db_path}")
else:
    print("雲端環境，不需處理本地資料庫文件的權限")


# 禁用資料庫追蹤修改，提高效能
# Disable database modification tracking to enhance performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 程式庫設定，禁用資料庫的追蹤
# 配置應用的密鑰，用於加密和安全操作
# Configure application secret key for encryption and security
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")  # 程式庫設定，應用的密鑰配置


# ========================================================
# E-mail功能擴建
# ========================================================

# 配置 Flask-Mail 的參數-注意!!!正式上線的服務不能直接使用.evn的數據，會影響保密程度
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', "smtp.gmail.com")          # SMTP 伺服器
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))    # SMTP 埠，默認 587
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'  # 是否啟用 TLS
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true' # 是否啟用 SSL
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER', 'oaplookout@gmail.com')      # 發送郵件的帳號
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')      # 發送郵件的密碼
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER', 'oaplookout@gmail.com')  # 預設的寄件人


# 統一初始化
# Unified initialization of extensions
print("==========統一初始化===============")
init_extensions(app)  # 專案模組，統一初始化資料庫、登入管理等功能
mail.init_app(app)
print("Flask-Mail 是否正確初始化:", mail)


# ========================================================
# 初始化擴展及功能app.register_blueprint
# Extension initialization and functionality
# ========================================================
print("=======初始化擴展及功能 app.register_blueprint============")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(external_search_bp, url_prefix="/external_search")
app.register_blueprint(news_fetch_bp, url_prefix="/news_fetch")
app.register_blueprint(search_engine_bp, url_prefix="/search_engine")
app.register_blueprint(user_scrape_bp, url_prefix="/user_scrape")
app.register_blueprint(weather_bp, url_prefix="/weather")  # 負責氣象資訊
app.register_blueprint(weather_news_bp, url_prefix="/weather_news")  # 負責氣象新聞
app.register_blueprint(cts_bp, url_prefix="/cts")
app.register_blueprint(ettoday_bp, url_prefix="/ettoday")
app.register_blueprint(ettoday2_bp, url_prefix="/ettoday2")
app.register_blueprint(google_bp, url_prefix="/google")
app.register_blueprint(nownews_bp, url_prefix="/nownews")
app.register_blueprint(nownews2_bp, url_prefix="/nownews2")
app.register_blueprint(setn_bp, url_prefix="/setn")
app.register_blueprint(tvbs_bp, url_prefix="/tvbs")
app.register_blueprint(worldnews_bp, url_prefix="/worldnews")
app.register_blueprint(udn_bp, url_prefix="/udn")
app.register_blueprint(yahoo_bp, url_prefix="/yahoo")
app.register_blueprint(scrape_news_bp, url_prefix="/scrape_news") # 啟動定時任務

app.register_blueprint(save_score_bp, url_prefix="/game") #遊戲酷邏輯

# 登入管理的加載回調函數，根據用戶 ID 查找用戶
# Login manager's user loader callback function to find a user by ID
# @login_manager.user_loader
# def load_user(user_id):  # 專案邏輯，設定用戶的登錄驗證
#     return User.query.get(int(user_id))  # 專案模組，查詢用戶資料
@login_manager.user_loader
def load_user(user_id):
    return AuthUser.query.get(int(user_id))  # 確保使用 AuthUser




# ========================================================
# 創建資料表
# Create database tables
# ========================================================

# 建立資料表（僅執行一次）
# Create tables (execute only once)
# 建立資料表（僅執行一次，適用於綁定資料庫）
with app.app_context():
    db.metadata.clear()  # 清理重複定義的表結構
    if FLASK_ENV in ["development", "local_mysql"]:
        # 僅在本地環境中創建資料表
        for bind_key, bind_uri in app.config['SQLALCHEMY_BINDS'].items():
            try:
                engine = db.create_engine(bind_uri)
                db.metadata.create_all(engine)
                print(f"成功創建資料表 (綁定鍵: {bind_key})")
            except Exception as e:
                print(f"創建資料表失敗 (綁定鍵: {bind_key}): {e}")
    else:
        print("跳過雲端資料表創建邏輯")

Page_Noiser_news = Page_Noiser.fetch_news()
udn2_news = udn2.fetch_udn2_news()

try:
    # 直接使用 fetch_weather_news 函數來獲取數據
    from weather_news import fetch_weather_news
    weather_news = fetch_weather_news()
except Exception as e:
    print(f"⚠️ 錯誤: {e}")
    weather_news = []  # 當爬取失敗時返回空資料
    
try:
    # 直接使用 fetch_weather_news 函數來獲取數據
    from ettoday2 import fetch_ettoday2_news
    ettoday2_items = fetch_ettoday2_news()
except Exception as e:
    print(f"⚠️ 錯誤: {e}")
    ettoday2_items = []  # 當爬取失敗時返回空資料

try:
    # 匯入 fetch_international_news 函數
    from international_news_scraper import fetch_international_news  # 確保檔案名稱正確
    international_news = fetch_international_news()  # 調用函數獲取新聞資料
except Exception as e:
    print(f"⚠️ 錯誤: {e}")
    international_news = []  # 當爬取失敗時返回空資料
try:
    # 匯入 fetch_international_news 函數
    from taiwan_news import fetch_taiwan_news  # 確保檔案名稱正確
    taiwan_news = fetch_taiwan_news()  # 調用函數獲取新聞資料
except Exception as e:
    print(f"⚠️ 錯誤: {e}")
    taiwan_news = []  # 當爬取失敗時返回空資料
    
def normalize_news(news_list):
    """標準化新聞欄位名稱"""
    for news in news_list:
        # 確保圖片欄位完整
        news.setdefault("image_link", news.get("photo", news.get("image_link", news.get("url", "static/images/default_news.png"))))

        # 統一時間欄位
        news.setdefault("published_at", news.get("publish_time", news.get("time", {}).get("date", "未知時間")))

        # 確保摘要存在
        news.setdefault("summary", news.get("content", news.get("description", news.get("paragraph", "沒有摘要"))))

        # 確保新聞連結完整
        news.setdefault("url", news.get("link", news.get("titleLink", "#")))

        # 增加新聞來源
        news.setdefault("source", news.get("source", "未知來源"))

        # 增加瀏覽次數（如果存在）
        news.setdefault("views", news.get("view", 0))

        # 確保分類存在
        news.setdefault("category", news.get("story_list", "未分類"))

        # 確保內容可讀等級
        news.setdefault("content_level", news.get("content_level", "未知狀態"))
        
normalize_news(ettoday2_items)
normalize_news(weather_news)
normalize_news(taiwan_news)
normalize_news(udn2_news)

"""
{
    "title": "新聞標題",
    "url": "新聞連結",
    "image_link": "新聞圖片",
    "summary": "新聞摘要",
    "published_at": "發布時間",
    "source": "新聞來源"
}
"""

new2 = ettoday2_items + weather_news + taiwan_news + udn2_news

if len(new2) >= 6:
    selected_news = random.sample(new2, 6)  # 隨機選 8 則
else:
    selected_news = new2  # 若新聞數量不足 8 則，直接使用全部新聞

print(selected_news)

# ========================================================
# 路由及功能
# Routes and functionality
# ========================================================
# 定義路由，渲染首頁模板
@app.route('/')
def home():  # 程式庫邏輯，定義首頁路由
    print("首頁加載中")
    
    return render_template(
        'index.html', 
        ettoday2_items=ettoday2_items, 
        weather_news=weather_news, 
        international_news=international_news, 
        taiwan_news=taiwan_news,
        udn2_news=udn2_news)  # 專案邏輯，渲染首頁 HTML 文件

# 其他靜態頁面路由
@app.route('/index-1.html')
def index1():  # 程式庫邏輯，定義休息園地路由
    print("休息園地加載中")
    return render_template('index-1.html')  # 專案邏輯，渲染休息園地 HTML 文件

@app.route('/index-1-1.html')
def index11():  # 程式庫邏輯，定義原始網站路由
    print("原始網站加載中")
    return render_template('index-1-1.html')  # 專案邏輯，渲染原始網站 HTML 文件

@app.route('/index-2.html')
def index2():  # 程式庫邏輯，定義焦點新聞路由
    print("焦點新聞加載中")
    youtube = youtube_search()
    return render_template('index-2.html', Page_Noiser_news=Page_Noiser_news, new2=selected_news, youtube = youtube)  # 專案邏輯，渲染焦點新聞 HTML 文件

@app.route('/index-3.html')
def index3():  # 程式庫邏輯，定義氣象新聞路由
    print("氣象新聞加載中")
    return render_template('index-3.html', weather_news=weather_news)# 渲染 index-3.html 並傳遞數據


@app.route('/index-4.html')
def index4():  # 程式庫邏輯，定義娛樂新聞 HTML 文件
    print("創建資料表加載中")
    return render_template('index-4.html')  # 專案邏輯，渲染娛樂新聞 HTML 文件

@app.route('/index-5.html')
def index5():# 程式庫邏輯，定義運動新聞 HTML 文件
    print("創建資料表加載中")
    return render_template('index-5.html', 
    ettoday2_items=ettoday2_items,)  # 專案邏輯，渲染運動新聞 HTML 文件



from flask_mail import Message


@app.route('/test-email', methods=['GET', 'POST'])
def test_email():
    try:
        msg = Message(
            subject="聯成學員-妙齊測試郵件",
            sender=os.getenv('MAIL_DEFAULT_SENDER'),  # 明確指定寄件人
            recipients=["aaappphh174805@gmail.com"],  # 替換為測試用的收件人
            body="老師您好，這是一封測試郵件，用於確認 Flask-Mail 功能是否正常運作。"
        )
        mail.send(msg)
        return jsonify({"message": "郵件已成功發送！"}), 200
    except Exception as e:
        return jsonify({"error": f"郵件發送失敗: {str(e)}"}), 500




if __name__ == '__main__':
    
    # 從環境變數讀取 PORT，預設值為 10000
    port = int(os.environ.get('PORT', 10000))
    # 設定 host 為 0.0.0.0，讓外部可訪問
    app.run(debug=True,host='127.0.0.1', port=port)#debug=False, 


"""


with app.app_context():  # 程式庫設定，應用上下文
    db.metadata.clear()  # 專案模組，清理重複定義的表結構
    for bind_key, db_uri in app.config['SQLALCHEMY_BINDS'].items():  # 遍歷每個資料庫綁定
        try:
            engine = db.engines(app, bind=bind_key)  # 專案模組，獲取資料庫的引擎
            db.metadata.create_all(bind=engine)  # 專案模組，為綁定的資料庫創建表
            print(f"成功創建資料表 (綁定鍵: {bind_key}, URI: {db_uri})")  # 輸出成功訊息
        except Exception as e:
            print(f"創建資料表失敗 (綁定鍵: {bind_key}): {e}")  # 輸出錯誤訊息


with app.app_context():
    db.create_all(bind='user')
    db.create_all(bind='auth')
    db.create_all(bind='game')
    db.create_all(bind='news')


"""