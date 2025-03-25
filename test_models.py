# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 04:20:00 2025

@author: OAP-0001
"""

# 程式名稱: test_models.py
# Program Name: test_models.py
# 依照 models.py 的定義，創建 MySQL 資料庫
# Creates MySQL databases based on definitions in models.py

# ========================================================
# 匯入所需模組與設定
# Import necessary modules and configurations
# ========================================================

from app import app  # 匯入主應用程式
# Import the main application
from database import db  # 引入資料庫擴展
# Import the database extension from database.py
from models import User, AuthUser, Score, NewsArticle
# 從 models.py 匯入定義的資料表模型
# Import data models from models.py

# ========================================================
# 資料庫創建邏輯
# Database creation logic
# ========================================================
def create_databases():
    """依據資料表模型創建 MySQL 資料庫"""
    # Create MySQL databases based on data table models
    try:
        with app.app_context():  # 進入 Flask 應用上下文
            # Enter the Flask application context
            db.metadata.clear()  # 清理重複定義的資料表結構
            # Clear duplicate table definitions
            
            # 遍歷每個資料庫綁定並創建
            # Iterate over each database binding and create tables
            for bind_key, db_uri in app.config['SQLALCHEMY_BINDS'].items():
                print(f"開始創建資料表 (綁定鍵: {bind_key}, URI: {db_uri})")
                # Print starting message for table creation
                engine = db.engines[bind_key]  # 根據綁定鍵獲取資料庫引擎
                # Get database engine based on binding key
                db.metadata.create_all(bind=engine)  # 創建表結構
                # Create table structures
                print(f"成功創建資料表 (綁定鍵: {bind_key})")
                # Print success message for table creation
    except Exception as e:
        # 捕捉創建資料庫時的錯誤
        # Catch errors during database creation
        print(f"創建資料庫失敗: {e}")
        # Print error message

# ========================================================
# 主程序執行
# Main program execution
# ========================================================

if __name__ == "__main__":
    print("初始化資料庫...")
    # Start database initialization
    create_databases()
    print("資料庫初始化完成！")
    # Database initialization completed
