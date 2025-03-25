# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 19:13:21 2025

@author: OAP-0001
"""
#scheduled_scrape 定時爬蟲設定-google


import requests  # 匯入 requests 模組，用於發送 HTTP 請求
from bs4 import BeautifulSoup  # 匯入 BeautifulSoup，用於解析 HTML
from datetime import datetime  # 用於時間處理
from flask import Blueprint
from models import db, NewsArticle  # 引入資料庫與新聞模型
import random  # 啟用隨機模式，生成默認內容
from database import db

google_bp = Blueprint('google', __name__, url_prefix="/google")


# google爬蟲
def fetch_google_news():
    base_url = "https://news.google.com"
    url = "https://news.google.com/home?hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}

    try:
        print("嘗試連線至 Google News...")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("⚠️ Google News 爬取失敗")
            return {"error": "Google News 爬取失敗"}
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到父階層 id="c166-panel"
        articles = soup.find(id="c166-panel").find_all("div", class_="wkWCof")  # 根據實際子標籤修改
        print("==================================")
        print(f"共找到 {len(articles)} 則新聞文章")

        google_news = []
        random_texts = ["點擊查看全文", "探索新聞詳情", "快速瞭解更多"]  # 隨機摘要

        for idx, article in enumerate(articles, start=1):
            print(f"提取第 {idx} 則新聞")

            # 提取圖片
            image_tag = article.find("img", class_="Quavad vwBmvb")
            image_url = base_url + image_tag["src"] if image_tag and "src" in image_tag.attrs else "無圖片"

            # 提取標題與連結
            title_tag = article.find("a", class_="gPFEn")
            title = title_tag.text.strip() if title_tag else "無標題"
            link = base_url + title_tag["href"][1:] if title_tag and title_tag["href"].startswith("./") else title_tag["href"] if title_tag else "無連結"

            # 提取發佈時間
            time_tag = article.find("time", class_="hvbAAd")
            publish_time = time_tag["datetime"] if time_tag and "datetime" in time_tag.attrs else datetime.utcnow()

            # 使用隨機內文摘要
            content = random.choice(random_texts)

            # 檢查是否已存在於資料庫
            existing = NewsArticle.query.filter_by(url=link).first()
            if not existing:
                # 新增到資料庫
                news_article = NewsArticle(
                    title=title,
                    content=content,
                    source="Google News",
                    image_url=image_url,
                    url=link,
                    category="焦點",
                    published_at=publish_time,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(news_article)
                db.session.commit()
                google_news.append({"title": title, "link": link})

        return google_news

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return {"error": str(e)}







# 單獨測試
if __name__ == "__main__":
    # 測試 Yahoo 和 Google 新聞爬取功能
    print("\n測試 Google 新聞爬取...")
    google_news = fetch_google_news()
    print("Google 新聞爬取結果：", google_news)