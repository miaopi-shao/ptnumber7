# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 18:52:16 2025

@author: OAP-0001
"""

# 程式名稱:Ettoday2.PY 喧染頁面用

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from flask import Blueprint, jsonify
import random

# 定義 Flask Blueprint
ettoday2_bp = Blueprint("ettoday2", __name__)

def fetch_ettoday2_news():
    try:
        # 設定目標網址與 HTTP 請求頭
        url = "https://www.ettoday.net/news/hot-news.htm"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        print("嘗試連線至 ETtoday News...")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"⚠️ HTTP 狀態碼 {response.status_code}")
            return []

        print("✅ 成功連接至 ETtoday News，開始解析 HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')
        # 限定範圍 - 從最外層父類逐步縮小範圍到最底層
        parent_block = soup.select_one('.block_content .part_pictxt_3')  # 確保選擇正確的上層
        if parent_block:
            articles = parent_block.select('.piece.clearfix')  # 提取目標內容
            for article in articles:
                print(article.text)  # 或者提取你需要的其他屬性
        else:
            print("未找到指定的父元素")

        # articles = soup.select(".clearfix")  # 使用正確的 CSS 選擇器
        print(f"共找到 {len(articles)} 則新聞文章")

        news_nownews = []
        for idx, article in enumerate(articles):
            print(f"--- 提取第 {idx} 則新聞 ---")

            # 提取資訊
            title = article.find("h3").text.strip() if article.find("h3") else "無標題"
            link = article.find("a")["href"] if article.find("a", class_="pic") else "無連結"
            content = article.find("p", class_="summary").text.strip() if article.find("p", class_="summary") else random.choice(["點擊查看全文", "探索新聞詳情", "快速瞭解更多"])
            image_link_tag = article.find("img")
            image_link = image_link_tag["src"] if image_link_tag and "src" in image_link_tag.attrs else "無圖片連結"
            publish_time = datetime.now(timezone.utc).isoformat()

            print(f"標題：{title}")
            print(f"連結：{link}")
            print(f"摘要：{content}")
            print(f"圖片連結：{image_link}")
            print(f"發布時間：{publish_time}")

            # 整理新聞資料
            news_data = {
                "title": title,
                "link": link,
                "content": content,
                "image_link": image_link,
                "publish_time": publish_time,
            }
            news_nownews.append(news_data)

        print(f"✅ 成功抓取 {len(news_nownews)} 則新聞")
        return news_nownews

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        return []
    



# API 端點，手動觸發爬蟲
@ettoday2_bp.route("/scrape", methods=["GET"])
def fetch_news_api():
    """ 提供 API，手動觸發新聞爬取 """
    ettoday2_items = fetch_ettoday2_news()
    # 隨機選擇 5 則 ETtoday 新聞
    if len(ettoday2_items) > 5:
        ettoday2_items = random.sample(ettoday2_items, 5)
    news = ettoday2_items
    # 直接返回爬取的新聞數據 JSON，供頁面使用
    return jsonify({
        "message": f"成功抓取 {len(news)} 篇新聞",
        "data": news
    }), 200


# 運行程式並打印結果
if __name__ == '__main__':
    news = fetch_ettoday2_news()
    print("=== 爬取結果 ===")
    for idx, article in enumerate(news, start=1):
        print(f"{idx}. 標題: {article['title']}")
        print(f"   連結: {article['link']}")
        print(f"   圖片: {article['image_link']}")
        print(f"   摘要: {article['content']}")
        print(f"   發布時間: {article['publish_time']}")
        print("================================")
