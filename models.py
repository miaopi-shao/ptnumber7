# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:08:53 2025

@author: OAP-0001
"""

# models.py 用戶資料庫模型

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 記錄用戶創建時間
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新用戶資料時記錄時間
    role = db.Column(db.String(20), default="user")  # 角色：預設為普通用戶，可擴展為 "admin"、"moderator" 等
