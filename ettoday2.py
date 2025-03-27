# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 18:52:16 2025

@author: OAP-0001
"""

# 新聞爬蟲程式
import requests  # 匯入 requests 模組，用於發送 HTTP 請求
from bs4 import BeautifulSoup  # 匯入 BeautifulSoup，用於解析 HTML
from dateutil import parser  # 匯入日期解析器，處理 ISO 時間格式
from datetime import datetime  # 用於時間處理
from flask import Blueprint, jsonify
from models import db, NewsArticle  # 引入資料庫與新聞模型
import random  # 啟用隨機模式，生成默認內容
from database import db



# 新聞雲爬蟲程式，用於從 ETtoday 熱門新聞頁面抓取新聞資訊並存入 SQLite 資料庫
# 定義 Flask Blueprint
ettoday2_bp = Blueprint("ettoday2", __name__)

def fetch_ettoday2_news():
    

    # 設定目標網址與 HTTP 請求頭
    url = "https://www.ettoday.net/news/hot-news.htm"  # 定義要爬取的 ETtoday 熱門新聞頁面 URL
    headers = {                               # 設定 HTTP 請求的 header，模擬瀏覽器行為
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print("嘗試連線至 ETtoday News...")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print("⚠️ 新聞雲 連接失敗")
            return {"error": "新聞雲 連接失敗"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
    
        # 找到所有新聞的父容器
        articles = soup.select("part_pictxt_3")
        print("==================================")
        print(f"共找到 {len(articles)} 則新聞文章")
    
        news_nownews = []
        source = "ETtoday"  # 新聞來源
        for idx, article in enumerate(articles, start=1):
            print(f"提取區塊 {idx}")
    
            # 提取圖片連結
            image_link_tag = article.find("img")
            if image_link_tag and "src" in image_link_tag.attrs:  # 確保 src 存在
                if image_link_tag["src"].startswith("./"):  # 如果是相對路徑
                    image_link = url + image_link_tag["src"][1:]  # 修正為絕對路徑
                else:
                    image_link = image_link_tag["src"]  # 已是絕對路徑
            else:
                image_link = "無圖片連結"
    
            # 提取圖片新聞的標題與連結
            a_tag = article.find("a", class_="pic")
            if a_tag:
                link = url + a_tag["href"][1:] if a_tag["href"].startswith("./") else a_tag["href"]
            else:
                link = "無連結"
            
            # 提取圖片新聞的標題及摘要
            random_texts = ["點擊查看全文", "探索新聞詳情", "快速瞭解更多"]
            title_tag = article.find("h3")
            title = title_tag.text.strip() if title_tag else "無標題"
            content_tag = article.find("p", class_="summary")
            content = content_tag.text.strip() if content_tag else random.choice(random_texts)# 提取摘要
            
            # 提取新聞時間
            time_tag = article.find("span", class_="date")
            if time_tag and "datetime" in time_tag.attrs:
                publish_time = parser.parse(time_tag["datetime"])
            else:
                publish_time = datetime.utcnow()  # 默認為當前時間

    
            # 檢查是否已存在
            existing = NewsArticle.query.filter_by(url=link).first()
            if not existing:
                # 新增新聞到資料庫
                news_article = NewsArticle(
                    title = title,
                    content = content,
                    source = source,
                    image_url = image_link,
                    url = link,
                    category = "焦點",
                    published_at = publish_time,
                    created_at = datetime.utcnow(),
                    updated_at = datetime.utcnow()
                )
                db.session.add(news_article)
                db.session.commit()
                news_nownews.append({"title": title, "link": link})
    
        return news_nownews
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return []

@ettoday2_bp.route("/scrape", methods=["GET"])
def fetch_news_api():
    """ 提供 API，手動觸發新聞爬取 """
    news = fetch_ettoday2_news()
    return jsonify({"message": f"成功存入 {len(news)} 篇新聞"}), 200