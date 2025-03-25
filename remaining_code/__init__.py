# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 15:47:15 2025

@author: OAP-0001
"""

# remaining_code資料夾套件化-自動運行代碼區，如天氣概況，及時爬蟲套件......

try:
    from .user_scrape import user_scrape_bp
except ImportError as e:
    print(f"Error importing user_scrape_bp: {e}")

try:
    from .weather import weather_bp
except ImportError as e:
    print(f"Error importing weather_bp: {e}")
    
try:
    from .scrape_news import scrape_news_bp
except ImportError as e:
    print(f"Error importing scrape_news_bp: {e}")
    
try:
    from .news_fetch import news_fetch_bp
except ImportError as e:
    print(f"Error importing news_fetch_bp: {e}")
    
try:
    from .external_search import external_search_bp
except ImportError as e:
    print(f"Error importing news_fetch_bp: {e}")    
    
try:
    from .search_engine import search_engine_bp
except ImportError as e:
    print(f"Error importing news_fetch_bp: {e}")        
 
# ...後續再導入其他模組的代碼

# 將所有藍圖組合成一個列表，方便在 app.py 中一次性註冊
all_remaining_code_blueprints = [
    user_scrape_bp,
    weather_bp,
    scrape_news_bp,
    news_fetch_bp,
    external_search_bp,
    search_engine_bp,
    # ...可以繼續加入其他藍圖
]
