# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 17:06:59 2025

@author: OAP-0001
"""
import yt_dlp
import json
import os
import time
import random
import requests
from flask import Blueprint

CACHE_FILE = "/static/tmp/youtube_cache.json"  # 快取檔案名稱
CACHE_EXPIRY = 86400  # 24 小時 (每天只爬一次)
RETRY_DELAY = 10800  # 3 小時 (秒) 如果 API 被鎖則延遲爬取
RETRY_DELAY2 = 11800  # 3 小時 (秒) 如果 API 被鎖則延遲爬取
RETRY_DELAY3 = 10100  # 3 小時 (秒) 如果 API 被鎖則延遲爬取

def is_cache_valid():
    """檢查快取是否有效 (每天更新一次)"""
    if not os.path.exists(CACHE_FILE):
        return False
    last_modified = os.path.getmtime(CACHE_FILE)
    return (time.time() - last_modified) < CACHE_EXPIRY


def install_chrome():
    os.system("apt-get update")
    os.system("apt-get install -y wget unzip")
    os.system("wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
    os.system("apt-get install -y ./google-chrome-stable_current_amd64.deb")

install_chrome()

youtube_bp = Blueprint('youtube', __name__)



def fetch_youtube(query="快訊", max_results=6):
    """使用 yt-dlp 爬取 YouTube 影片標題、連結與縮圖"""
    sleep_time = random.uniform(5, 10)  # 🔥 加入隨機延遲，降低 API 被鎖風險
    time.sleep(sleep_time)

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'noplaylist': True,
        'age_limit': 18,
        'format': 'best',
        'outtmpl': '/dev/null',
        'sleep_interval': 8,
    }
    try:
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
    except yt_dlp.utils.DownloadError as e:
        if "429" in str(e):  # 🔥 API 被鎖，延遲 3 小時再爬
            print("API 被鎖定，等待 3 小時後再嘗試...")
            time.sleep(RETRY_DELAY2)
            return fetch_youtube(query, max_results)
        else:
            print(f"爬取時發生錯誤：{e}")
            return []

def youtube_search():
    """檢查快取，僅在快取過期時爬取資料"""
    try:
        if is_cache_valid():  # 🔥 如果快取有效，直接返回快取資料
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        # 爬取新資料
        video_data = fetch_youtube()

        # 🔥 存入快取
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(video_data, f, ensure_ascii=False, indent=4)

        return video_data
    except Exception as e:
        print(f"錯誤發生：{e}")
        return [
            {"title": "API遭鎖，導向其他網站", "url": "https://www.example.com",
             "image_link": "https://www.example.com/placeholder.jpg"}
        ]

# 🔥 測試爬取 YouTube 新聞影片標題、連結與縮圖
news_videos = youtube_search()
print(news_videos)


# def youtube2_1_search(query="藝人", max_results=2):
#     sleep_time = random.uniform(5, 10)  # 🔥 加入隨機延遲，降低 API 被鎖風險
#     time.sleep(sleep_time)
#     """使用 yt-dlp 爬取 YouTube 影片標題、連結與縮圖"""
#     ydl_opts = {
#         'quiet': True,
#         'noplaylist': True,
#         'age_limit': 18,
#         'format': 'best',
#         'outtmpl': '/dev/null',
#         'sleep_interval': 5,
#     }
#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             result = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
#             video_data = []
#             if 'entries' in result:
#                 for video in result['entries']:
#                     if not video.get('id'):  #  影片沒有 ID，直接跳過
#                         continue  
                    
#                     thumbnail_url = video.get('thumbnail')
#                     if not thumbnail_url or thumbnail_url == "undefined":
#                         continue  # 直接跳過該影片
    
#                     #  檢查縮圖是否失效，避免使用假的 `maxresdefault.jpg`
#                     if "maxresdefault.jpg" in thumbnail_url and requests.get(thumbnail_url).status_code == 404:
#                         continue  # **直接跳過該影片**
                    
#                     video_data.append({
#                         'title': video.get('title'),
#                         'url': video.get('webpage_url'),  # **使用正確的 YouTube 網頁連結**
#                         'image_link': thumbnail_url,
#                         'id': video.get('id')  # **明確提供 ID，前端解析更安全**
#                     })
#             return video_data
#     except yt_dlp.utils.DownloadError as e:
#         if "429" in str(e):  # 🔥 API 被鎖，延遲 3 小時再爬
#             print("API 被鎖定，等待 3 小時後再嘗試...")
#             time.sleep(RETRY_DELAY)
#             return fetch_youtube(query, max_results)
#         else:
#             print(f"爬取時發生錯誤：{e}")
#             return []

# def youtube2_2_search(query="演藝圈", max_results=2):
#     sleep_time = random.uniform(5, 10)  # 🔥 加入隨機延遲，降低 API 被鎖風險
#     time.sleep(sleep_time)
#     """使用 yt-dlp 爬取 YouTube 影片標題、連結與縮圖"""
#     try:
#         ydl_opts = {
#             'quiet': True,
#             'noplaylist': True,
#             'age_limit': 18,
#             'format': 'best',
#             'outtmpl': '/dev/null',
#             'sleep_interval': 6,
#         }
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             result = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
#             video_data = []
#             if 'entries' in result:
#                 for video in result['entries']:
#                     if not video.get('id'):  #  影片沒有 ID，直接跳過
#                         continue  
                    
#                     thumbnail_url = video.get('thumbnail')
#                     if not thumbnail_url or thumbnail_url == "undefined":
#                         continue  # 直接跳過該影片
    
#                     #  檢查縮圖是否失效，避免使用假的 `maxresdefault.jpg`
#                     if "maxresdefault.jpg" in thumbnail_url and requests.get(thumbnail_url).status_code == 404:
#                         continue  # **直接跳過該影片**
                    
#                     video_data.append({
#                         'title': video.get('title'),
#                         'url': video.get('webpage_url'),  # **使用正確的 YouTube 網頁連結**
#                         'image_link': thumbnail_url,
#                         'id': video.get('id')  # **明確提供 ID，前端解析更安全**
#                     })
#             return video_data
#     except yt_dlp.utils.DownloadError as e:
#         if "429" in str(e):  # 🔥 API 被鎖，延遲 3 小時再爬
#             print("API 被鎖定，等待 3 小時後再嘗試...")
#             time.sleep(RETRY_DELAY3)
#             return fetch_youtube(query, max_results)
#         else:
#             print(f"爬取時發生錯誤：{e}")
#             return []

# def youtube2_search():
#     """合併 youtube2_1_search 和 youtube2_2_search 的結果"""
#     try:
#         video_data = []
#         video_data.extend(youtube2_1_search())  # 直接調用，使用預設參數
#         video_data.extend(youtube2_2_search())  # 直接調用，使用預設參數
#         return video_data if video_data else  [
#                     {
#                         "title": "API遭鎖，導向youtube首頁",
#                         "url": "https://www.youtube.com/",  # 🔥 這裡可以指向一個替代資訊頁面
#                         "image_link": "https://pngimg.com/download/20645",  # 🔥 替代圖片，不會顯示錯誤
#                         "id": "N/A"  # 🔥 ID 直接設為 "N/A"，避免解析錯誤
#                     }
#                 ]  # 返回合併後的結果
#     except Exception as e:
#         print(f"錯誤：{e}")  
#         return [
#             {
#                 "title": "API遭鎖，導向youtube首頁",
#                 "url": "https://www.youtube.com/",  # 🔥 這裡可以指向一個替代資訊頁面
#                 "image_link": "https://pngimg.com/download/20645",  # 🔥 替代圖片，不會顯示錯誤
#                 "id": "N/A"  # 🔥 ID 直接設為 "N/A"，避免解析錯誤
#             }
#         ]


# #  測試爬取 YouTube 新聞影片標題、連結與縮圖
# news2_videos = youtube2_search()
# print("-----------------------------")
# print(news2_videos)
