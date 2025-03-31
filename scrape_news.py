# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 17:03:02 2025

@author: OAP-0001
"""

# 綜合型爬蟲與定時任務（scrape_news.py）

from flask import Blueprint, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from models import NewsArticle
from database import db
from cts import fetch_cts_news
from ettoday import fetch_ettoday_news
from nownews import fetch_nownews_news
from setn import fetch_setn_news
from tvbs import fetch_tvbs_news
from udn import fetch_udn_news
from worldnews import fetch_worldnews_news
from yahoo import fetch_yahoo_news
from google import fetch_google_news
from datetime import datetime, timedelta
import requests

# 定義 Blueprint
scrape_news_bp = Blueprint('scrape_news', __name__)

def fetch_news_batch(fetchers):
    """執行一批新聞爬取"""
    for fetcher, name in fetchers:
        try:
            print(f"開始爬取 {name} 資訊...")
            fetcher()
        except Exception as e:
            print(f"{name} 資訊爬取失敗：{e}")
            with open("error_log.txt", "a") as log_file:
                log_file.write(f"{datetime.utcnow()} - {name} 資訊爬取失敗：{e}\n")
    print("該批新聞爬取完畢！")


def schedule_news_fetching():
    """將所有爬取分成多個批次並定時執行"""
    # 定義每批次要爬取的來源
    batches = [
        [(fetch_cts_news, "CTS"), (fetch_ettoday_news, "ETtoday")],
        [(fetch_nownews_news, "Nownews"), (fetch_setn_news, "Setn")],
        [(fetch_tvbs_news, "TVBS"), (fetch_udn_news, "UDN")],
        [(fetch_worldnews_news, "WorldNews"), (fetch_yahoo_news, "Yahoo")],
        [(fetch_google_news, "Google")],
    ]
    # 定時執行每批次
    scheduler = BackgroundScheduler()
    for index, batch in enumerate(batches):
        scheduler.add_job(lambda: fetch_news_batch(batch), 'interval', minutes=30, id=f'batch_{index}')
    scheduler.start()


def delete_old_news():
    """刪除過期新聞"""
    cutoff_date = datetime.utcnow() - timedelta(days=3)  # 刪除 7 天前的新聞
    old_news = NewsArticle.query.filter(NewsArticle.published_at < cutoff_date).all()
    if old_news:  # 確認是否有需要刪除的資料
        for news in old_news:
            db.session.delete(news)
        db.session.commit()
        print("過期新聞刪除完成！")
    else:
        print("無過期新聞需要刪除！")


# 在 Blueprint 註冊的地方啟動定時任務
@scrape_news_bp.before_app_request
def before_request():
    """在應用第一次請求之前啟動定時任務"""
    schedule_news_fetching()
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_old_news, 'interval', days=1, id='delete_old_news')  # 每日清理過期新聞
    scheduler.start()




"""
# def fetch_all_news():
#     ""統一執行所有新聞爬取邏輯，並進行錯誤捕捉"
#     try:
#         print("開始爬取 CTS 資訊...")
#         fetch_cts_news()
#     except Exception as e:
#         print(f"CTS 資訊爬取失敗：{e}")

#     try:
#         print("開始爬取 ETtoday 資訊...")
#         fetch_ettoday_news()
#     except Exception as e:
#         print(f"ETtoday 資訊爬取失敗：{e}")

#     try:
#         print("開始爬取 Nownews 資訊...")
#         fetch_nownews_news()
#     except Exception as e:
#         print(f"Nownews 資訊爬取失敗：{e}")
        
#     try:    
#         print("開始爬取 Setn 資訊...")
#         fetch_seth_news()
#     except Exception as e:
#         print(f"Setn 資訊爬取失敗：{e}")
        
#     try:
#         print("開始爬取 TVBS 資訊...")
#         fetch_tvbs_news()
#     except Exception as e:
#         print(f"TVBS 資訊爬取失敗：{e}")
        
#     try:
#         print("開始爬取 UDN 資訊...")
#         fetch_udn_news()
#     except Exception as e:
#         print(f"UDN 資訊爬取失敗：{e}")
        
#     try:
#         print("開始爬取 WorldNews 資訊...")
#         fetch_worldnews_news()
#     except Exception as e:
#         print(f"WorldNews 資訊爬取失敗：{e}")
        
#     try:
#         print("開始爬取 Yahoo 資訊...")
#         fetch_yahoo_news()
#     except Exception as e:
#         print(f"Yahoo 資訊爬取失敗：{e}")
        
#     try:
#         print("開始爬取 Google 資訊...")
#         fetch_google_news()
#     except Exception as e:
#         print(f"Google 資訊爬取失敗：{e}")
    
    
#     print("新聞爬取完畢！")
"""
