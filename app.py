# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:07:53 2025

@author: OAP-0001
"""

#整合用主程式

# app.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# 導入各個 Blueprint
from auth import auth_bp                           #引入註冊帳號模組
from external_search import external_search_bp     #引入站外搜尋模組
from search_engine import search_bp                #引入站內搜尋模組
from scheduled_scrape import scheduled_scrape_bp   #引入定時爬蟲模組
from user_scrape import user_scrape_bp             #引入自訂爬蟲模組
from weather import weather_bp                     #引入天氣概況模組

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)



# 註冊 Blueprint
app.register_blueprint(auth_bp)               #auth.py          帳號註冊用函式
app.register_blueprint(external_search_bp)    #external_search  處理站外搜尋
app.register_blueprint(search_bp)             #search           處理站內搜尋
app.register_blueprint(scheduled_scrape_bp)   #scheduled_scrape 定時爬蟲設定
app.register_blueprint(user_scrape_bp)        #user_scrape      用戶自定義爬蟲
app.register_blueprint(weather_bp)            #weather.py       天氣資訊 API

@app.route('/')
def home():
    return render_template('index.html')  # 假設你的首頁是 'index.html'


if __name__ == '__main__':
    app.run(debug=True)
