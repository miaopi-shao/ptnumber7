# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 15:47:15 2025

@author: OAP-0001
"""

# new資料夾套件化-新聞資料爬蟲區

from .cts import cts_bp
from .ettoday import ettoday_bp
from .nownews import nownews_bp
from .nownews2 import nownews2_bp
from .yahoo import yahoo_bp
from .google import google_bp
from .setn import  setn_bp
from .tvbs import tvbs_bp
from .udn import udn_bp
from .worldnews import worldnews_bp
from .ettoday2 import ettoday2_bp


from remaining_code.news_fetch  import fetch_individual_news, fetch_random_news, fetch_news_with_images

__all__ = [
    'fetch_individual_news',
    'fetch_random_news',
    'fetch_news_with_images',
]

# # ...後續再導入其他模組的代碼
# # 將所有爬取函數組合
# def scrape_news():
#     """統一觸發所有新聞爬取"""
#     print("開始爬取 CTS 資訊...")
#     scrape_cts()  # 執行 CTS 的爬取邏輯

#     print("開始爬取 ETtoday 資訊...")
#     scrape_ettoday()  # 執行 ETtoday 的爬取邏輯

#     print("開始爬取 Nownews 資訊...")
#     scrape_nownews()  # 執行 Nownews 的爬取邏輯

#     print("開始爬取 Setn 資訊...")
#     scrape_setn()  # 執行 Setn 的爬取邏輯

#     print("開始爬取 TVBS 資訊...")
#     scrape_tvbs()  # 執行 TVBS 的爬取邏輯

#     print("開始爬取 UDN 資訊...")
#     scrape_udn()  # 執行 UDN 的爬取邏輯

#     print("開始爬取 WorldNews 資訊...")
#     scrape_worldnews()  # 執行 WorldNews 的爬取邏輯

#     print("開始爬取 Yahoo/Google 資訊...")
#     scrape_yahoo_google()  # 執行 Yahoo/Google 的爬取邏輯


# 將所有藍圖組合成一個列表，方便在 app.py 中一次性註冊
all_new_blueprints = [
    cts_bp,
    ettoday_bp,
    nownews_bp,
    nownews2_bp,
    yahoo_bp,
    google_bp,
     setn_bp,
    udn_bp,
    tvbs_bp,
    worldnews_bp,
    ettoday2_bp,
    # ...可以繼續加入其他藍圖
]