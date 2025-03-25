# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 17:03:02 2025

@author: OAP-0001
"""

# 綜合型爬蟲與定時任務（scrape_news.py）

from flask import Blueprint, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from models import NewsArticle, db
from database import db
from new.cts import fetch_cts_news
from new.ettoday import fetch_ettoday_news
from new.nownews import fetch_nownews_news
from new.setn import fetch_setn_news
from new.tvbs import fetch_tvbs_news
from new.udn import fetch_udn_news
from new.worldnews import fetch_worldnews_news
from new.yahoo import fetch_yahoo_news
from new.google import fetch_google_news
from datetime import datetime, timedelta
import requests

# 定義 Blueprint
scrape_news_bp = Blueprint('scrape_news', __name__, url_prefix='/scrape_news')

def fetch_all_news():
    """統一執行所有新聞爬取邏輯"""
    for fetcher, name in [
        (fetch_cts_news, "CTS"),
        (fetch_ettoday_news, "ETtoday"),
        (fetch_nownews_news, "Nownews"),
        (fetch_setn_news, "Setn"),
        (fetch_tvbs_news, "TVBS"),
        (fetch_udn_news, "UDN"),
        (fetch_worldnews_news, "WorldNews"),
        (fetch_yahoo_news, "Yahoo"),
        (fetch_google_news, "Google"),
    ]:
        try:
            print(f"開始爬取 {name} 資訊...")
            fetcher()
        except Exception as e:
            print(f"{name} 資訊爬取失敗：{e}")
            with open("error_log.txt", "a") as log_file:
                log_file.write(f"{datetime.utcnow()} - {name} 資訊爬取失敗：{e}\n")
    print("新聞爬取完畢！")

def delete_old_news():
    """刪除過期新聞"""
    cutoff_date = datetime.utcnow() - timedelta(days=7)  # 刪除 7 天前的新聞
    old_news = NewsArticle.query.filter(NewsArticle.published_at < cutoff_date).all()
    if old_news:  # 確認是否有需要刪除的資料
        for news in old_news:
            db.session.delete(news)
        db.session.commit()
        print("過期新聞刪除完成！")
    else:
        print("無過期新聞需要刪除！")


def run_scheduler():
    """啟動定時任務"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_all_news, 'interval', hours=1)  # 每小時執行一次爬取
    scheduler.add_job(delete_old_news, 'interval', days=1)  # 每日清理過期新聞
    scheduler.start()


# def fetch_all_news():
#     """統一執行所有新聞爬取邏輯，並進行錯誤捕捉"""
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


# 定義 HTTP API 接口
@scrape_news_bp.route('/fetch', methods=['POST'])
def trigger_fetch_all_news():
    """排程新聞爬取開始!!!"""
    fetch_all_news()
    return jsonify({"message": "新聞爬取完畢！"})

@scrape_news_bp.route('/delete_old', methods=['POST'])
def trigger_delete_old_news():
    """排程刪除過期新聞中...."""
    delete_old_news()
    return jsonify({"message": "過期新聞刪除完成！"})


@scrape_news_bp.route('/trigger_scrape', methods=['POST'])
def trigger_scrape():
    """手動觸發新聞爬取（相當於調用 /fetch）"""
    response = requests.post("http://127.0.0.1:5000/scrape_news/fetch")  # 內部請求
    return jsonify(response.json())  # 轉發 fetch API 的回應


