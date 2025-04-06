# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 17:06:59 2025

@author: OAP-0001
"""
import yt_dlp
from flask import Blueprint
import os
import requests


def install_chrome():
    os.system("apt-get update")
    os.system("apt-get install -y wget unzip")
    os.system("wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
    os.system("apt-get install -y ./google-chrome-stable_current_amd64.deb")

install_chrome()

youtube_bp = Blueprint('youtube', __name__)



def youtube_search(query="快訊", max_results=6):
    """使用 yt-dlp 爬取 YouTube 影片標題、連結與縮圖"""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'noplaylist': True,
        'age_limit': 18,
        'format': 'best',
        'outtmpl': '/dev/null',  # 不儲存影片檔案
        'sleep_interval': 8,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
        video_data = []
        if 'entries' in result:
            for video in result['entries']:
                thumbnail_url = video.get('thumbnail')
                video_data.append({
                    'title': video.get('title'),
                    'url': video.get('url'),
                    'image_link': thumbnail_url,
                })
        return video_data

# 🔥 測試爬取 YouTube 新聞影片標題、連結與縮圖
news_videos = youtube_search()
print(news_videos)

def youtube2_1_search(query="藝人", max_results=2):
    """使用 yt-dlp 爬取 YouTube 影片標題、連結與縮圖"""
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'age_limit': 18,
        'format': 'best',
        'outtmpl': '/dev/null',
        'sleep_interval': 5,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
        video_data = []
        if 'entries' in result:
            for video in result['entries']:
                if not video.get('id'):  # 🔥 影片沒有 ID，直接跳過
                    continue  
                
                thumbnail_url = video.get('thumbnail')
                if not thumbnail_url or thumbnail_url == "undefined":
                    continue  # 直接跳過該影片

                # 🔥 檢查縮圖是否失效，避免使用假的 `maxresdefault.jpg`
                if "maxresdefault.jpg" in thumbnail_url and requests.get(thumbnail_url).status_code == 404:
                    continue  # **直接跳過該影片**
                
                video_data.append({
                    'title': video.get('title'),
                    'url': video.get('webpage_url'),  # **使用正確的 YouTube 網頁連結**
                    'image_link': thumbnail_url,
                    'id': video.get('id')  # **明確提供 ID，前端解析更安全**
                })
        return video_data

def youtube2_2_search(query="演藝圈", max_results=2):
    """使用 yt-dlp 爬取 YouTube 影片標題、連結與縮圖"""
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'age_limit': 18,
        'format': 'best',
        'outtmpl': '/dev/null',
        'sleep_interval': 6,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
        video_data = []
        if 'entries' in result:
            for video in result['entries']:
                if not video.get('id'):  # 🔥 影片沒有 ID，直接跳過
                    continue  
                
                thumbnail_url = video.get('thumbnail')
                if not thumbnail_url or thumbnail_url == "undefined":
                    continue  # 直接跳過該影片

                # 🔥 檢查縮圖是否失效，避免使用假的 `maxresdefault.jpg`
                if "maxresdefault.jpg" in thumbnail_url and requests.get(thumbnail_url).status_code == 404:
                    continue  # **直接跳過該影片**
                
                video_data.append({
                    'title': video.get('title'),
                    'url': video.get('webpage_url'),  # **使用正確的 YouTube 網頁連結**
                    'image_link': thumbnail_url,
                    'id': video.get('id')  # **明確提供 ID，前端解析更安全**
                })
        return video_data

def youtube2_search():
    """合併 youtube2_1_search 和 youtube2_2_search 的結果"""
    video_data = []
    video_data.extend(youtube2_1_search())  # 直接調用，使用預設參數
    video_data.extend(youtube2_2_search())  # 直接調用，使用預設參數
    return video_data  # 返回合併後的結果

# 🔥 測試爬取 YouTube 新聞影片標題、連結與縮圖
news2_videos = youtube2_search()
print("-----------------------------")
print(news2_videos)
