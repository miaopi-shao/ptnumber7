# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 17:06:59 2025

@author: OAP-0001
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from flask import Blueprint

youtube_bp = Blueprint('youtube', __name__)

def youtube_search(query="快訊", max_results=2):
    """使用 Selenium 爬取 YouTube 新聞影片標題、連結與縮圖"""

    # 設定 WebDriver 服務
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 啟用無界面模式，不打開瀏覽器

    # 正確初始化 WebDriver
    driver = webdriver.Chrome(service=service, options=options)

    # 打開 YouTube 搜尋結果頁面
    search_url = f"https://www.youtube.com/results?search_query={query}"
    driver.get(search_url)

    # 等待頁面載入
    driver.implicitly_wait(5)

    # 抓取影片標題與連結
    videos = driver.find_elements(By.CSS_SELECTOR, "a#video-title")
    video_data = []

    for video in videos[:max_results]:
        video_url = video.get_attribute("href")
        if video_url and "watch?v=" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]  # 獲取影片 ID
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            video_data.append({
                "title": video.text.strip(),
                "url": video_url,
                "image_link": thumbnail_url
            })

    # 關閉瀏覽器
    driver.quit()

    return video_data

# 🔥 測試爬取 YouTube 新聞影片標題、連結與縮圖
news_videos = youtube_search()
print(news_videos)
