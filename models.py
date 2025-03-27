# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:08:53 2025

@author: OAP-0001
"""

# ========================================================
# 資料庫模型部分
# ========================================================

# 匯入必要模組與初始化資料庫 (Flask SQLAlchemy)
from flask import Flask
from database import db  # 引入已初始化的資料庫對象
from datetime import datetime  # 處理日期和時間
from sqlalchemy.sql import func  # 支援更精確的時間戳處理
from werkzeug.security import generate_password_hash, check_password_hash  # 密碼加密與驗證


# ------------------- 預設x資料庫模型 (user.db) -------------------
class User(db.Model):
    """ 用於主程式的訪客模式與用戶基礎數據 """
    __bind_key__ = 'user'  # 綁定至 MySQL 的 user 資料庫
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="guest")  # 預設為訪客
    cookie = db.Column(db.String(300), nullable=True)  # 記錄裝置 Cookie
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# ------------------- 授權資料庫模型 (auth.db) -------------------
class AuthUser(db.Model):
    """ 處理帳戶創建、登入及狀態切換 """
    __bind_key__ = 'auth'
    __tablename__ = 'auth_users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    # Flask-Login 要求的屬性與方法
    @property
    def is_active(self):
        # 判斷用戶是否活躍，通常返回 True 表示用戶有效
        return True
    def get_id(self):
        # 返回用戶的唯一標識符
        return str(self.user_id)

# ------------------- 分數資料庫模型 -------------------
class Score(db.Model):
    """ 定義遊戲分數資料模型 """
    __bind_key__ = 'game'
    __tablename__ = 'game_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    game_name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ------------------- 新聞爬蟲模型 -------------------
class NewsArticle(db.Model):
    """ 定義新聞爬蟲資料模型 """
    __bind_key__ = 'news'
    __tablename__ = 'news_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    image_file = db.Column(db.String(300), nullable=True)
    url = db.Column(db.String(300), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    published_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
