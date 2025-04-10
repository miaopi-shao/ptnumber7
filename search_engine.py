# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:02:11 2025

@author: OAP-0001
"""

# 程式名稱: search_engine.py 提供資料庫進行搜尋
from flask import Blueprint, request, render_template
from models import NewsArticle  # 從模型中匯入資料庫與新聞模型
from database import db         # 統一執行初始化及連接模式

# 建立 Flask Blueprint，負責處理站內搜尋
search_engine_bp = Blueprint('search_engine', __name__)

#------------------------【將字典轉為字串】------------------------
def format_general_results(results):
    return [{
        "title": r.title,
        "source": r.source,
        "category": r.category,
        "url": r.url,
        "published_at": r.published_at
    } for r in results]

def format_image_results(results):
    return [{
        "image_url": r.image_url,
        "image_file": r.image_file,
        "title": r.title,
        "url": r.url
    } for r in results]

# # 使用這些函數：
# if search_type == "general":
#     return format_general_results(results_query.limit(limit).all())
# elif search_type == "image":
#     return format_image_results(results_query.limit(limit).all())


#------------------------【Flask 站內搜尋功能】------------------------
def search_news(query, category="all", search_type="general", limit=50):
    """
    從資料庫中搜尋新聞資訊，並依據分類與搜尋類型返回對應結果
    - query: 用戶輸入的搜尋關鍵字
    - category: 新聞分類，預設為 "all"
    - search_type: 搜尋類型，"general" 或 "image"
    - limit: 返回的新聞數量上限
    """
    # 確認查詢是否有效，避免空輸入
    if not query or len(query.strip()) < 1:
        return []
    query = f"%{query.strip().replace('%', '').replace('_', '')}%"  # 避免用戶輸入特殊符號影響查詢
    
    
    filters = [
        (NewsArticle.title.ilike(query)) | (NewsArticle.content.ilike(query))  # 模糊匹配
    ]
    
    valid_categories = ["sports", "entertainment", "politics", "technology", "business", "health"]  # 可用分類
    if category in valid_categories:
        filters.append(NewsArticle.category == category)
    
    # 執行查詢
    results_query = NewsArticle.query.filter(*filters).order_by(NewsArticle.published_at.desc())

    # 根據搜尋類型，返回不同欄位結果
    # 返回全部搜尋(字串喧染)-程式用第一種返回方式
    if search_type == "general":
        #依賴上方函式表達
        return format_general_results(results_query.limit(limit).all())
    
    # 返回圖片搜尋(圖片喧染)-第二種返回方式
    elif search_type == "image":
        # 圖片搜尋：提取圖片、標題、連結
        results = results_query.with_entities(
            NewsArticle.image_url,
            NewsArticle.image_file,
            NewsArticle.title,
            NewsArticle.url
        ).limit(limit).all()

        # 格式化結果
        return format_image_results(results)
        # return [{
        #     "image_url": r.image_url,
        #     "image_file": r.image_file,
        #     "title": r.title,
        #     "url": r.url
        # } for r in results]
        # 直接調用函式方式
        # return format_image_results(results_query.limit(limit).all())
    # 預設返回空結果
    return []


# 處理站內搜尋請求
@search_engine_bp.route('/internal_search', methods=['GET'])
def internal_search():
    """
    處理站內搜尋請求
    """
    # 取得用戶的搜尋請求與參數
    query = request.args.get('query', '').strip()
    category = request.args.get('category', 'all')  # 預設分類為 "all"
    search_type = request.args.get('type', 'general')  # 預設搜尋類型為 "general"（一般搜尋）
    limit = int(request.args.get('limit', 50))  # 動態控制返回數量，預設 50 條

    # 如果沒有輸入關鍵字，返回空結果並提示
    if not query:
        message = "請輸入關鍵字進行搜尋。"
        return render_template('search_results.html', query=query, category=category, search_type=search_type, results=[], message=message)

    # 執行站內搜尋
    results = search_news(query=query, category=category, search_type=search_type, limit=limit)

    # 如果沒有搜尋到結果，給出提示
    message = None if results else "沒有找到相關結果，請嘗試其他關鍵字。"
    return render_template('search_results.html', query=query, category=category, search_type=search_type, results=results, message=message)
    
    
"""

1.資料庫互動

    將 SQLite 的查詢邏輯替換為 SQLAlchemy ORM 方法，並使用 ilike 進行不區分大小寫的模糊匹配。
    
    1.查詢條件包含： 
        1- title 或 content 包含用戶的搜尋關鍵字。
        2- 如果指定分類（category != "all"），則加入分類過濾條件。
    
    2.查詢結果按發佈時間（published_at）降序排列。

2.搜尋類型分類

    1.一般搜尋：
       1- 提供以下欄位：title（標題）、source（來源）、category（分類）、url（連結）、published_at（時間）。
       2- 查詢結果會將 標題 和 摘要 的超連結設置為新聞的 url。
    
    1.圖片搜尋：
       1- 提供以下欄位：image_url（圖片網址）、image_file（圖片檔案路徑）、title（標題）、url（連結）。
       2- 用戶點擊 圖片 或 標題 可以跳轉到相應的新聞頁面。
    
3.Blueprint 路由
    
    /internal_search:
    
       1- 接收來自前端的參數：
            1_query: 搜尋的關鍵字。
            2_category: 新聞分類。
            3_type: 搜尋類型（"general" 或 "image"）。
        
       2- 調用 search_news 方法獲取搜尋結果，並將其反饋到前端模板中（search_results.html）。

4.查詢結果限制

    預設每次返回最多 50 條結果，可根據需求調整。

"""