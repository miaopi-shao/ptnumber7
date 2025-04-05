# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 17:06:59 2025

@author: OAP-0001
"""
import yt_dlp
from flask import Blueprint
import os

def install_chrome():
    os.system("apt-get update")
    os.system("apt-get install -y wget unzip")
    os.system("wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
    os.system("apt-get install -y ./google-chrome-stable_current_amd64.deb")

install_chrome()

youtube_bp = Blueprint('youtube', __name__)



def youtube_search(query="快訊", max_results=2):
    """使用 yt-dlp 爬取 YouTube 影片標題、連結與縮圖"""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'noplaylist': True,
        'age_limit': 18,
        'format': 'best',
        'outtmpl': '/dev/null',  # 不儲存影片檔案
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
        video_data = []
        if 'entries' in result:
            for video in result['entries']:
                video_data.append({
                    'title': video.get('title'),
                    'url': video.get('url'),
                    'image_link': video.get('thumbnail'),
                })
        return video_data

# 🔥 測試爬取 YouTube 新聞影片標題、連結與縮圖
news_videos = youtube_search()
print(news_videos)
