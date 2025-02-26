# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:07:53 2025

@author: OAP-0001
"""

#整合用主程式

# app.py
from flask import Flask, render_template          #輕量級Web框架  模板文件渲染頁面
from flask_login import LoginManager, UserMixin   #管理用戶登入狀態 用戶模型的輔助類別
from flask_sqlalchemy import SQLAlchemy           #定義資料庫操作


# 導入各個 Blueprint
from auth import auth_bp                           #引入註冊帳號模組
from external_search import external_search_bp     #引入站外搜尋模組
from search_engine import search_bp                #引入站內搜尋模組
from scheduled_scrape import scheduled_scrape_bp   #引入定時爬蟲模組
from user_scrape import user_scrape_bp             #引入自訂爬蟲模組
from weather import weather_bp                     #引入天氣概況模組
from game import save_score_bp                     #引入娛樂遊戲模組

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = 'your_secret_key'  # 這是必須的，確保你的 Flask app 有 secret_key
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


# 註冊 Blueprint
app.register_blueprint(auth_bp)               #auth.py          帳號註冊用函式
app.register_blueprint(external_search_bp)    #external_search  處理站外搜尋
app.register_blueprint(search_bp)             #search           處理站內搜尋
app.register_blueprint(scheduled_scrape_bp)   #scheduled_scrape 定時爬蟲設定
app.register_blueprint(user_scrape_bp)        #user_scrape      用戶自定義爬蟲
app.register_blueprint(weather_bp)            #weather.py       天氣資訊 API
app.register_blueprint(save_score_bp)         #ave_score        遊戲介面設定


class User(db.Model, UserMixin):  # 繼承 UserMixin 提供 login_required 所需的方法
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)



@app.route('/')
def home():
    return render_template('index.html')  # 假設你的首頁是 'index.html'
# 設置用戶的加載回調函數


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # 假設你的用戶模型是 User，並且使用 ID 查詢




if __name__ == '__main__':
    app.run(debug=True)


# ... 執行測試 ...
import os
del os.environ["JWT_SECRET"]  # 測試完成後刪除環境變數
del os.environ["JWT_SECRET"]
del os.environ["EMAIL_USER"]
del os.environ["EMAIL_PASS"]
del os.environ["SMTP_SERVER"]
