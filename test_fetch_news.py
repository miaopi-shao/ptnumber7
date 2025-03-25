# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 21:25:00 2025

@author: OAP-0001
"""

# 檔案名稱:test_fetch_news.py 測試資料庫運行用

# from models import NewsArticle, db
# from flask import Flask
# from datetime import datetime

# # 創建 Flask 應用（因為直接執行時需要 app context）
# app = Flask(__name__)
# # 設定資料庫綁定
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new.db'  # 預設主資料庫
# app.config['SQLALCHEMY_BINDS'] = {  
#     'news': 'sqlite:///new.db'  # 確保 'news' 這個綁定存在
# }
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # 初始化 SQLAlchemy
# db.init_app(app)

# def fetch_news_data():
#     with app.app_context():  # 需要 Flask 應用上下文
#         news_list = NewsArticle.query.order_by(NewsArticle.published_at.desc()).all()

#         if not news_list:
#             print("❌ 沒有找到任何新聞資料！")
#             return

#         print("✅ 找到的新聞資料：")
#         for news in news_list[:5]:  # 只顯示前 5 筆
#             print(f"ID: {news.id}")
#             print(f"標題: {news.title}")
#             print(f"來源: {news.source}")
#             print(f"連結: {news.url}")
#             print(f"發布時間: {news.published_at.strftime('%Y-%m-%d %H:%M:%S')}")
#             print("-" * 50)

# # 執行測試
# if __name__ == "__main__":
#     fetch_news_data()