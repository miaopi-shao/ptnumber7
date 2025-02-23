# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:04:24 2025

@author: OAP-0001
"""

from flask import Blueprint, jsonify
import requests
from bs4 import BeautifulSoup

scheduled_scrape_bp = Blueprint('scheduled_scrape', __name__)

def fetch_yahoo_news():
    url = "https://tw.news.yahoo.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": "Yahoo News 爬取失敗"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select("a[href][title]")[:5]  # 取前 5 則新聞
        
        news_list = []
        for article in articles:
            title = article.get("title")
            link = article.get("href")
            if title and link:
                if not link.startswith("http"):
                    link = "https://tw.news.yahoo.com" + link  # 確保完整連結
                news_list.append({"title": title, "link": link})
        
        return news_list
    except Exception as e:
        return {"error": f"Yahoo 爬取錯誤: {str(e)}"}


def fetch_google_news():
    url = "https://news.google.com/home?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": "Google News 爬取失敗"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select("article h3 a")[:5]  # 取前 5 則新聞
        
        news_list = []
        for article in articles:
            title = article.text.strip()
            link = article.get("href")
            if link and title:
                if link.startswith("/articles/"):
                    link = "https://news.google.com" + link[1:]  # 修正 Google 新聞連結
                news_list.append({"title": title, "link": link})
        
        return news_list
    except Exception as e:
        return {"error": f"Google 爬取錯誤: {str(e)}"}


@scheduled_scrape_bp.route('/scrape', methods=['GET'])
def scrape():
    yahoo_news = fetch_yahoo_news()
    google_news = fetch_google_news()
    
    return jsonify({
        "yahoo_news": yahoo_news,
        "google_news": google_news
    })
