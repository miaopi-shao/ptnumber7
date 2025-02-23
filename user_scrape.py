# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:05:52 2025

@author: OAP-0001
"""

# user_scrape.py 允許用戶自行輸入網址，並執行爬蟲程式。
from flask import Blueprint, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

user_scrape_bp = Blueprint('user_scrape', __name__)

def is_valid_url(url):
    """驗證網址格式"""
    pattern = re.compile(
        r'^(https?:\/\/)?'  # http:// or https:// (可選)
        r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6})'  # 網域名稱
        r'(:\d+)?(\/.*)?$'  # 連接埠(可選)和路徑(可選)
    )
    return bool(pattern.match(url))

@user_scrape_bp.route('/user_scrape', methods=['POST'])
def user_scrape():
    """初次爬取 (只回傳標題和前 500 字)"""
    url = request.json.get('url')
    
    if not url or not is_valid_url(url):
        return jsonify({"error": "請提供有效網址"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200 or not response.text:
            return jsonify({"error": f"爬取失敗，狀態碼: {response.status_code}"}), 500

        soup = BeautifulSoup(response.text, 'html.parser')

        # 初步回傳部分內容
        scraped_data = {
            "title": soup.title.string if soup.title else "無標題",
            "text": soup.get_text(strip=True)[:500],  # 只返回前500個字
            "url": url  # 保存URL，方便後續爬取完整內容
        }

        return jsonify(scraped_data)
    
    except requests.exceptions.Timeout:
        return jsonify({"error": "請求超時，請稍後再試"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"請求錯誤: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"爬蟲出錯: {str(e)}"}), 500

@user_scrape_bp.route('/user_scrape/full', methods=['POST'])
def user_scrape_full():
    """根據用戶選擇的範圍，爬取完整內容"""
    url = request.json.get('url')
    text_length = request.json.get('text_length', 1000)  # 預設返回 1000 字
    keyword = request.json.get('keyword', None)  # 可選的標題關鍵字篩選

    if not url or not is_valid_url(url):
        return jsonify({"error": "請提供有效網址"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200 or not response.text:
            return jsonify({"error": f"爬取失敗，狀態碼: {response.status_code}"}), 500

        soup = BeautifulSoup(response.text, 'html.parser')
        full_text = soup.get_text(strip=True)

        # 根據用戶選擇的關鍵字篩選標題
        title = soup.title.string if soup.title else "無標題"
        if keyword and keyword.lower() not in title.lower():
            return jsonify({"error": f"標題 '{title}' 不符合關鍵字篩選"}), 400

        return jsonify({
            "title": title,
            "text": full_text[:text_length]  # 根據用戶選擇的範圍返回內容
        })
    
    except requests.exceptions.Timeout:
        return jsonify({"error": "請求超時，請稍後再試"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"請求錯誤: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"爬蟲出錯: {str(e)}"}), 500
