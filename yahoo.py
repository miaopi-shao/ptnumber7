# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:04:24 2025

@author: OAP-0001
"""

# 程式名稱:yahoo.py
# ===============================
# YAHOO新聞爬蟲程式
# Yahoo News Scraper
# ===============================

import requests  # 匯入 requests 模組，用於發送 HTTP 請求
from bs4 import BeautifulSoup  # 匯入 BeautifulSoup，用於解析 HTML
from dateutil import parser  # 匯入日期解析器，處理 ISO 時間格式
from datetime import datetime  # 用於時間處理
from flask import Blueprint, jsonify
from models import db, NewsArticle  # 引入資料庫與新聞模型
import random  # 啟用隨機模式，生成默認內容
from database import db



yahoo_bp = Blueprint('yahoo', __name__)

#yahoo爬蟲
def fetch_yahoo_news():
    url = "https://tw.news.yahoo.com/sports/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    
    print("正在嘗試爬取 Yahoo News...")
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print("⚠️ YAHOO新聞 連接失敗")
            return {"error": "YAHOO News 連接失敗"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
    
        # 找到所有新聞的父容器
        articles = soup.select("div.C(#959595).Fz(13px).D(ib)")
        print("==================================")
        print(f"共找到 {len(articles)} 則新聞文章")
    
        news_nownews = []
        source = "YAHOO"  # 新聞來源
        for article in articles:
            print(f"提取區塊 {article}")
    
            title_tag = article.find("span")
            title = title_tag.text.strip() if title_tag else "無標題"
    
            time_tag = article.find("div", class_="C(#959595) Fz(13px)")
            publish_time = parser.parse(time_tag.text.strip()) if time_tag else datetime.utcnow()
    
            image_tag = article.find("img")
            image_link = image_tag.get("src") or image_tag.get("data-src") if image_tag else "無圖片連結"
    
            link_tag = article.find("a")
            link = link_tag["href"] if link_tag else "無連結"
            
            # 提取摘要
            random_texts = ["點擊查看全文", "探索新聞詳情", "快速瞭解更多"]
            content_tag = article.find("p", class_="Mt(12px) Lh(1.4) Fz(16px) C($c-fuji-grey-l) LineClamp(2,44px) M(0)")
            content = content_tag.text.strip() if content_tag else random.choice(random_texts)# 提取摘要

    
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
                    category = "運動",
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

@yahoo_bp.route("/scrape", methods=["GET"])
def fetch_news_api():
    """
    提供 API 以手動觸發新聞爬取
    Provide an API for manually triggering news scraping
    """
    news = fetch_yahoo_news()
    return jsonify({"message": f"成功存入 {len(news)} 篇新聞", "data": news}), 200

# 單獨測試
if __name__ == "__main__":
    print("測試 Yahoo 新聞爬取...")
    yahoo_news = fetch_yahoo_news()
    print("Yahoo 新聞爬取結果：", yahoo_news)
    print("+++++++++++++++++++++++++++++++++++++")
    
"""
如果相對路徑是 ./read/...，將去掉 ./，並在前面加上 Base URL。 例如：

python
base_url = "https://news.google.com"
relative_path = "./read/CBMiU..."
absolute_path = base_url + relative_path[1:]  # 去掉 "./"
print(absolute_path)  # 輸出完整的絕對路徑
"""