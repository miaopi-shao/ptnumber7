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
# Database extension
from flask_login import LoginManager  # 用戶登入管理擴展
# Login manager extension
from flask_mail import Mail  # 郵件處理擴展
# Mail handling extension

# 初始化 Flask 擴展
# Initialize Flask extensions
db = SQLAlchemy()  # 資料庫
login_manager = LoginManager()  # 登入管理器
mail = Mail()  # 郵件管理器

def init_extensions(app):
    """統一初始化所有擴展"""
    # Unified initialization of all extensions
    try:
        db.init_app(app)  # 初始化資料庫
        login_manager.init_app(app)  # 初始化登入管理器
        mail.init_app(app)  # 初始化郵件管理器
        print("所有擴展已成功初始化")  # 確認初始化成功
        print("All extensions have been successfully initialized")  # Confirmation of initialization success
    except Exception as e:
        # 捕捉初始化錯誤
        print(f"初始化擴展時發生錯誤: {e}")  # 顯示錯誤訊息
        print(f"An error occurred while initializing extensions: {e}")  # Display error message
