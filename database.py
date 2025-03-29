# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 04:04:13 2025

@author: OAP-0001
"""

# 程式名稱: database.py 負責所有擴展的初始化邏輯
# Program Name: database.py Responsible for initializing all extensions

# 引入 Flask 擴展
# Importing Flask extensions
from flask_sqlalchemy import SQLAlchemy  # 資料庫操作擴展

from sqlalchemy import inspect, create_engine  # 資料庫檢查表單

from flask_jwt_extended import JWTManager

from sqlalchemy import create_engine


# Database extension
from flask_login import LoginManager  # 用戶登入管理擴展
# Login manager extension
from flask_mail import Mail  # 郵件處理擴展
# Mail handling extension

import logging
logging.basicConfig(level=logging.INFO)  # 配置全局日誌級別

def initialize_database(uri, sql_file):
    engine = create_engine(uri)
    with engine.connect() as connection:
        with open(sql_file, "r") as file:
            setup_script = file.read()
            connection.execute(setup_script)



# 初始化 Flask 擴展
# Initialize Flask extensions
db = SQLAlchemy()  # 資料庫
login_manager = LoginManager()  # 登入管理器
mail = Mail()  # 郵件管理器
jwt = JWTManager()


def init_extensions(app):
    if not hasattr(app, 'extensions_initialized'):  # 自定義屬性，標記擴展是否已初始化
       
        try:
            # 初始化資料庫擴展
            db.init_app(app)
            with app.app_context():
                inspector = inspect(db.engine)
                if not inspector.get_table_names():  # 確認資料表是否已存在
                    db.create_all()
            #開始初始化
            logging.info("初始化檔 database.py-系統正在初始化")
            login_manager.init_app(app)  # 初始化登入管理器
            login_manager.login_view = "auth.login"  # 未登入時的跳轉頁面
            
            login_manager.login_message = "請先登入才能訪問此頁面"
            logging.info("登入管理器初始化完成")

            jwt.init_app(app) # 初始化生成、驗證和解析管理器
            logging.info("JWT 管理器初始化完成")
            
            mail.init_app(app)  # 初始化郵件管理器
            logging.info("郵件管理器初始化完成")
            
            app.extensions_initialized = True  # 設置標記，表示擴展已初始化
            logging.info("初始化檔 database.py-所有擴展已成功初始化")

        except Exception as e:
            logging.error(f"擴展初始化過程中出現錯誤: {e}")
            raise  # 遇到致命錯誤時，阻止應用啟動

    else:
        print("初始化檔 database.py擴展已初始化，跳過重複執行")

