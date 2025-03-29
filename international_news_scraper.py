import requests
from bs4 import BeautifulSoup
import random
from flask import Blueprint, jsonify

# 定義 Blueprint，提供國際新聞的 API 路由
international_news_bp = Blueprint("international_news", __name__)

# 爬取 BBC 新聞
def fetch_bbc_news():
    url = "https://www.bbc.com/news"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到父元素
    articles = soup.find_all("div", class_="sc-c6f6255e-0 eGcloy")  # 確保選中正確的父容器
    if articles:
        selected_articles = random.sample(articles, min(2, len(articles)))  # 隨機選擇兩則新聞
        results = []
        for article in selected_articles:
            # 提取標題
            title_tag = article.find("h2")
            title = title_tag.text.strip() if title_tag else "無標題"
            
            # 提取摘要
            summary_tag = article.find("p")
            summary = summary_tag.text.strip() if summary_tag else "無摘要"
            
            # 提取圖片連結
            image_tag = article.find("img", class_="sc-a34861b-0 efFcac")
            image_link = image_tag["src"] if image_tag and image_tag.get("src") else "https://via.placeholder.com/150"

            # 提取新聞連結
            link_tag = article.find("a")
            link = "https://www.bbc.com" + link_tag["href"] if link_tag and link_tag.get("href") else "#"
            
            results.append({
                "title": title,
                "link": link,
                "summary": summary,
                "image_link": image_link,
            })
        return results
    else:
        return [{"title": "無法獲取 BBC 新聞", "link": "#", "summary": "無摘要", "image_link": "https://via.placeholder.com/150"}]

# 爬取 Al Jazeera 新聞
def fetch_aljazeera_news():
    url = "https://www.aljazeera.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到父容器 class="hp-featured-second-stories__item"
    articles = soup.find_all("li", class_="hp-featured-second-stories__item")
    if articles:
        selected_articles = random.sample(articles, min(2, len(articles)))  # 隨機選擇兩則新聞
        results = []
        for article in selected_articles:
            # 提取標題
            title_tag = article.find("h3", class_="article-card__title")
            title = title_tag.text.strip() if title_tag else "無標題"

            # 提取圖片連結
            image_tag = article.find("img", class_="article-card__image")
            image_link = image_tag["src"] if image_tag and image_tag.get("src") else "https://via.placeholder.com/150"

            # 提取新聞連結
            link_tag = article.find("a")
            link = "https://www.aljazeera.com" + link_tag["href"] if link_tag and link_tag.get("href") else "#"
            
            results.append({
                "title": title,
                "link": link,
                "image_link": image_link,
            })
        return results
    else:
        return [{"title": "無法獲取 Al Jazeera 新聞", "link": "#", "image_link": "https://via.placeholder.com/150"}]

# 整合隨機抓取各兩則新聞
def fetch_international_news():
    # 從 BBC 和 Al Jazeera 各抓取兩則新聞
    bbc_news = fetch_bbc_news()
    aljazeera_news = fetch_aljazeera_news()
    return bbc_news + aljazeera_news

# API 路由，提供國際新聞資料
@international_news_bp.route("/scrape", methods=["GET"])
def fetch_news_api():
    """ 提供 API，返回隨機各兩則國際新聞 """
    try:
        news = fetch_international_news()
        return jsonify({"message": "成功抓取國際新聞", "data": news}), 200
    except Exception as e:
        return jsonify({"error": f"抓取新聞失敗: {str(e)}"}), 500

# 運行程式並打印結果
if __name__ == '__main__':
    news = fetch_international_news()
    print("=== 隨機抓取各兩則新聞 ===")
    for idx, article in enumerate(news, start=1):
        print(f"新聞 {idx}:")
        print(f"標題: {article['title']}")
        print(f"連結: {article['link']}")
        print(f"圖片: {article['image_link']}")
        print("==============================")