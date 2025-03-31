
# 程式名稱: news_fetch.py 版面喧染
# 此檔案用來從資料庫中提取新聞資料，並提供給前端模板進行渲染
# 我們使用 Flask 的 Blueprint 來定義路由，並延遲導入模型以避免循環依賴

import os
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, render_template, jsonify

from database import db
from models import NewsArticle

# 建立 Blueprint，設定路徑前綴為 /news_fetch
news_fetch_bp = Blueprint('news_fetch', __name__)


# ------------------------------
# 定義新聞提取函數
# ------------------------------

def fetch_individual_news(source_name, limit=10):
    """
    根據來源名稱提取新聞資料
    :param source_name: 新聞來源，例如 SETN、TVBS 等
    :param limit: 返回新聞數量上限，預設 10 篇
    :return: 一個列表，每篇新聞以字典形式儲存所需資訊
    """
    news_articles = NewsArticle.query.filter_by(source=source_name)\
                                       .order_by(NewsArticle.published_at.desc())\
                                       .limit(limit).all()
    # 轉換成字典列表，方便在模板中使用
    return [{
        "title": article.title,
        "content": article.content,
        "source": article.source,
        "image_url": article.image_url,
        "url": article.url,
        "published_at": article.published_at
    } for article in news_articles]


def fetch_random_news(limit=10):
    """
    隨機提取新聞資料
    :param limit: 返回新聞數量上限，預設 10 篇
    :return: 一個包含隨機新聞的列表，每篇新聞以字典形式儲存
    """
    news_articles = NewsArticle.query.order_by(db.func.rand()).limit(limit).all()
    return [{
        "title": article.title,
        "content": article.content,
        "source": article.source,
        "image_url": article.image_url,
        "url": article.url,
        "published_at": article.published_at
    } for article in news_articles]


def fetch_news_with_images(limit=10):
    """
    篩選出具有圖片的新聞資料
    :param limit: 返回新聞數量上限，預設 10 篇
    :return: 一個包含有圖片新聞的列表，每篇新聞以字典形式儲存
    """
    # 檢查 image_url 既非 None 亦非空字串
    news_articles = NewsArticle.query.filter(
        NewsArticle.image_url.isnot(None),
        NewsArticle.image_url != ''
    ).order_by(NewsArticle.published_at.desc()).limit(limit).all()
    return [{
        "title": article.title,
        "content": article.content,
        "source": article.source,
        "image_url": article.image_url,
        "url": article.url,
        "published_at": article.published_at
    } for article in news_articles]

# ------------------------------
# 定義路由部分
# ------------------------------

@news_fetch_bp.route('/individual/<source>', methods=['GET'])
def individual_news(source):
    """
    路由：顯示指定來源的新聞
    :param source: 新聞來源參數
    :return: 使用 individual_news.html 模板渲染的新聞列表
    """
    news = fetch_individual_news(source_name=source, limit=10)
    return render_template('individual_news.html', news=news)


@news_fetch_bp.route('/random', methods=['GET'])
def random_news():
    """
    路由：顯示隨機新聞
    :return: 使用 random_news.html 模板渲染的新聞列表
    """
    news = fetch_random_news(limit=10)
    return render_template('random_news.html', news=news)


@news_fetch_bp.route('/with_images', methods=['GET'])
def news_with_images():
    """
    路由：顯示附有圖片的新聞
    :return: 使用 news_with_images.html 模板渲染的新聞列表
    """
    try:
        news = fetch_news_with_images(limit=10)
        print(news)  # 確認返回的資料
        return render_template('news_with_images.html', news=news)
    except Exception as e:
            print(f"Error occurred: {e}")
            return "Internal Server Error", 500


# ------------------------------
# 生成頭條新聞的 HTML 結構
# ------------------------------

def generate_headline_html():
    """
    生成靜態 HTML 結構，用於替換輪播區內容
    :return: 渲染 index.html 模板並傳入生成的 HTML 內容
    """
    from models import NewsArticle
    import random
    # 提取所有帶圖片的新聞
    news_articles = NewsArticle.query.filter(
        NewsArticle.image_url.isnot(None),
        NewsArticle.image_url != ''
    ).all()
    # 隨機打亂新聞順序
    random.shuffle(news_articles)
    # 選取前 5 條新聞
    selected_articles = news_articles[:5]
    # 依照原有格式手動拼接 HTML 結構
    html_content = ""
    for article in selected_articles:
        html_content += f"""
        <div data-thumb="{article.image_url}" 
             data-src="{article.image_url}" 
             data-time="1500" data-trasPeriod="4000" data-link="{article.url}" data-target="_blank">
            <div class="camera_caption fadeIn">
                <div class="slider-text">
                    <div class="inside">{article.title} <a href="{article.url}">去看看</a></div>
                </div>
            </div>
        </div>
        """
    # 返回渲染後的 index.html 模板，其中 html_content 為輪播區內容
    return render_template('index.html', html_content=html_content)

