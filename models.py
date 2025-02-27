# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:08:53 2025

@author: OAP-0001
"""

# 從 Flask 框架中匯入 SQLAlchemy 來處理資料庫操作
from flask_sqlalchemy import SQLAlchemy
# 從 datetime 模組匯入 datetime 類別，用來處理日期和時間
from datetime import datetime

# 初始化 SQLAlchemy 資料庫對象
db = SQLAlchemy()

# ------------------- 用戶資料庫模型 -------------------

class User(db.Model):
    """ 定義用戶資料模型，用於存儲用戶的帳號、密碼、郵箱等資訊 """
    id = db.Column(db.Integer, primary_key=True)  # 主鍵，唯一識別用戶
    
    username = db.Column(db.String(100), unique=True, nullable=False)  # 用戶名，唯一且不可為空
    
    password = db.Column(db.String(200), nullable=False)  # 密碼，不能為空
    
    email = db.Column(db.String(120), unique=True, nullable=True)  # 電子郵件，唯一，可選
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 用戶創建時間，預設為當前時間
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 用戶資料更新時間，每次更新時自動修改
    
    role = db.Column(db.String(20), default="user")  # 用戶角色，預設為普通用戶，可擴展為 "admin"、"moderator" 等



# ------------------- 分數資料庫模型 -------------------

class Score(db.Model):
    """ 定義遊戲分數資料模型，用於存儲用戶的遊戲分數 """
    id = db.Column(db.Integer, primary_key=True)  # 主鍵，唯一識別分數
    username = db.Column(db.String(80), nullable=False)  # 用戶名，不能為空
    score = db.Column(db.Integer, nullable=False)  # 分數，不能為空



# ----------------------------------------------------------------

# 用戶資料庫模型會與以下檔案進行聯繫：

# 1. app.py 連接資料庫，並處理註冊、登入等操作時，會使用到 User 模型。
# 2. auth.js 用於進行前端的註冊、登入操作，向後端發送請求，後端會用 User 模型來檢查帳號密碼。
# 3. index.html 會顯示註冊、登入頁面，與 auth.js 配合，通過 POST 請求將資料提交到後端。
# 4. tetris_game.html 和 parkour_game.html：遊戲頁面會用到 Score 模型來保存和顯示遊戲分數。

# 其中：
# - app.py: 使用 User 和 Score 模型來處理登入、註冊、遊戲分數的儲存和查詢。
# - auth.js: 前端處理帳號註冊、登入，並將資料提交到後端，後端根據 User 模型進行操作。
# - index.html: 前端頁面顯示登入、註冊表單，並與 auth.js 配合發送請求。
# - tetris_game.html 和 parkour_game.html: 用來顯示遊戲，並將遊戲分數提交給後端，使用 Score 模型儲存分數。


"""
如何在不同檔案中使用這些模型：
    1. app.py（後端主檔案）
       使用 User 模型來進行用戶的註冊、登入、資料查詢等操作。
       使用 Score 模型來儲存和查詢遊戲分數。
      
    2. auth.js（後端帳號用 JS 檔）
       前端處理用戶的註冊、登入，並發送請求給後端。
       當用戶註冊或登入成功後，後端會使用 User 模型來查詢資料，並返回成功或失敗的結果。
    
    3. index.html（前端 HTML 檔）
       用戶進行註冊、登入操作，並通過 auth.js 提交資料給後端。
       可以顯示用戶的註冊、登入頁面。
    
    4. tetris_game.html 和 parkour_game.html（遊戲頁面）
       當用戶遊玩完遊戲後，前端會將分數提交給後端。
       後端會使用 Score 模型來儲存用戶的分數。


程式碼執行步驟：
 1. index.html 提供註冊和登入頁面，使用 auth.js 來處理表單提交。
 2. auth.js 將使用者資料提交到後端的 app.py。
 3. app.py 接收資料並與 User 模型進行資料庫操作（如註冊、登入、查詢）。
 4. 當用戶成功登入後，會進入遊戲頁面 tetris_game.html 或 parkour_game.html。
 5. 遊戲結束後，遊戲分數會通過後端保存到 Score 模型中。
 
"""



