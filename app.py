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

# 匯入資料庫模型，管理數據結構
# Import database models to manage data structures
from models import User, AuthUser, Score, NewsArticle    # 專案的模型模組，定義用戶、分數和新聞的數據表結構
print(User)  # 應該輸出 <class 'models.User'>，確認模型匯入成功
print(Score)  # 應該輸出 <class 'models.Score'>，確認模型匯入成功
print(NewsArticle)  # 應該輸出 <class 'models.NewsArticle'>，確認模型匯入成功

# 專案模組匯入，所有Blueprint 模組，用於模組化路由
# Import all Blueprint modules for modular routing within the project
from auth import all_auth_blueprints                      # 負責處理帳號驗證邏輯
from new import all_new_blueprints                        # 負責定時爬取新聞的邏輯
from game import all_game_blueprints                      # 負責處理遊戲相關邏輯
from remaining_code import all_remaining_code_blueprints  # 包含其餘功能的邏輯
from remaining_code.scrape_news import run_scheduler      # 定時執行新聞爬蟲

# 引入 HTTP 請求模組，用於與外部 API 通訊
# Import HTTP request library for external API communication
import requests  # 程式庫的模組，用於執行 HTTP 請求操作

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

# 配置多資料庫綁定
# Configure multi-database bindings
if os.environ.get("FLASK_ENV") == "development":  # 判斷環境是否是開發模式
    base_path = "D:/PTtest/instance/"  # 開發模式下的資料庫路徑
else:
    base_path = "instance/"  # 雲端環境下的資料庫路徑

# 設定主資料庫與多綁定資料庫
# Set main database and multi-bind databases
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Psy481705=..@localhost/main_database_name'  # 程式庫設定，主資料庫連接 URI
app.config['SQLALCHEMY_BINDS'] = {  # 程式庫設定，其他綁定資料庫的連接 URI
    'user': 'mysql+pymysql://root:Psy481705=..@localhost/user_database_name',  # 專案資料庫，預設執行檔案
    'auth': 'mysql+pymysql://root:Psy481705=..@localhost/auth_database_name',  # 專案資料庫，帳號相關資料
    'game': 'mysql+pymysql://root:Psy481705=..@localhost/game_database_name',  # 專案資料庫，遊戲分數相關資料
    'news': 'mysql+pymysql://root:Psy481705=..@localhost/news_database_name'   # 專案資料庫，新聞爬蟲相關資料
}

# 調整資料庫文件的讀寫權限
# Adjust read/write permissions for database files
db_files = ["auth.db", "game.db", "new.db"]  # 專案資料庫文件列表
for db_file in db_files:  # 遍歷所有資料庫文件
    db_path = os.path.join(base_path, db_file)  # 程式庫模組，用於拼接文件路徑
    if os.path.exists(db_path):  # 檢查文件是否存在
        os.chmod(db_path, 0o777)  # 程式庫模組，修改文件的權限
        print(f"已更改權限: {db_path}")  # 輸出更新權限的文件路徑

# 禁用資料庫追蹤修改，提高效能
# Disable database modification tracking to enhance performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 程式庫設定，禁用資料庫的追蹤
# 配置應用的密鑰，用於加密和安全操作
# Configure application secret key for encryption and security
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")  # 程式庫設定，應用的密鑰配置

# ========================================================
# 初始化擴展及功能
# Extension initialization and functionality
# ========================================================

# 統一初始化擴展
# Unified initialization of extensions
init_extensions(app)  # 專案模組，統一初始化資料庫、登入管理等功能

# 啟動定時任務
# Start scheduled tasks
run_scheduler()  # 專案模組，負責啟動定時爬取新聞的功能

# 註冊 Blueprint，分別加載各功能模組
# Register Blueprints to load functionality modules
for blueprint in all_auth_blueprints + all_new_blueprints + all_game_blueprints + all_remaining_code_blueprints:
    app.register_blueprint(blueprint)  # 專案模組，註冊各功能模組的路由

# 登入管理的加載回調函數，根據用戶 ID 查找用戶
# Login manager's user loader callback function to find a user by ID
@login_manager.user_loader
def load_user(user_id):  # 專案邏輯，設定用戶的登錄驗證
    return User.query.get(int(user_id))  # 專案模組，查詢用戶資料

# ========================================================
# 創建資料表
# Create database tables
# ========================================================

# 建立資料表（僅執行一次）
# Create tables (execute only once)

with app.app_context():
    db.metadata.clear()  # 清理重複定義的表結構
    for bind_key in app.config['SQLALCHEMY_BINDS']:
        try:
            engine = db.engines[bind_key]  # 使用新的方式獲取引擎
            db.metadata.create_all(engine)  # 創建資料表
            print(f"成功創建資料表 (綁定鍵: {bind_key})")
        except Exception as e:
            print(f"創建資料表失敗 (綁定鍵: {bind_key}): {e}")




# ========================================================
# 路由及功能
# Routes and functionality
# ========================================================
# 定義路由，渲染首頁模板
@app.route('/')
def home():  # 程式庫邏輯，定義首頁路由
    return render_template('index.html')  # 專案邏輯，渲染首頁 HTML 文件

# 其他靜態頁面路由
@app.route('/index-1.html')
def index1():  # 程式庫邏輯，定義休息園地路由
    return render_template('index-1.html')  # 專案邏輯，渲染休息園地 HTML 文件

@app.route('/index-1-1.html')
def index11():  # 程式庫邏輯，定義原始網站路由
    return render_template('index-1-1.html')  # 專案邏輯，渲染原始網站 HTML 文件

@app.route('/index-2.html')
def index2():  # 程式庫邏輯，定義焦點新聞路由
    return render_template('index-2.html')  # 專案邏輯，渲染焦點新聞 HTML 文件

@app.route('/index-3.html')
def index3():  # 程式庫邏輯，定義運動新聞路由
    return render_template('index-3.html')  # 專案邏輯，渲染運動新聞 HTML 文件

@app.route('/index-4.html')
def index4():  # 程式庫邏輯，定義娛樂新聞 HTML 文件
    return render_template('index-4.html')  # 專案邏輯，渲染娛樂新聞 HTML 文件
@app.route('/index-5.html')
def index5():
    return render_template('index-5.html')  # 專案邏輯，渲染氣象特報 HTML 文件




if __name__ == '__main__':
    # 從環境變數讀取 PORT，預設值為 10000
    port = int(os.environ.get('PORT', 10000))
    # 設定 host 為 0.0.0.0，讓外部可訪問
    app.run(debug=False,host='127.0.0.1', port=port)#debug=True, 


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