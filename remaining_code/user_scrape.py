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
from urllib.parse import urlparse   # URL 驗證加強
import time
import random
import logging

# 與 app.py 連動：藍圖 (Blueprint) 註冊部分
user_scrape_bp = Blueprint('user_scrape', __name__)
# 設定日誌文件
logging.basicConfig(level=logging.INFO, filename='user_scrape.log', format='%(asctime)s - %(message)s')


def is_valid_url(url):
    """驗證網址格式"""
    pattern = re.compile(
        r'^(https?:\/\/)?'  # http:// 或 https:// (可選)
        r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6})'  # 網域名稱
        r'(:\d+)?(\/.*)?$'  # 連接埠(可選)和路徑(可選)
    )
    """驗證網址格式是否有效"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])  # 必須包含協議與主機名
    except ValueError:
        return False
    return bool(pattern.match(url))

def extract_text(soup):
    """嘗試提取主要內容"""
    paragraphs = soup.find_all(['p', 'div'], string=True)  # 找出所有 <p> 或 <div> 標籤的文字
    main_text = ' '.join(p.get_text(strip=True) for p in paragraphs if p)  # 過濾空白文字
    return main_text[:500]  # 返回前 500 個字


@user_scrape_bp.route('/user_scrape', methods=['POST'])
def user_scrape():
    """初次爬取 (只回傳標題和前 500 字)"""
    url = request.json.get('url')
    
    sections = request.json.get('sections', [])  # 用戶指定的區域，如 ['title', 'main_text']
    
    if not url or not is_valid_url(url):
        return jsonify({"error": "請提供有效網址"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    try:
        # 延遲爬蟲，防止被封
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=headers, timeout=5)
        print(f"HTTP Response Status Code: {response.status_code}")  # 調試信息

        if response.status_code != 200 or not response.text:
            return jsonify({"error": f"爬取失敗，狀態碼: {response.status_code}"}), 500

        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {
            "url": url,  # 保存 URL，方便後續使用
            "title": soup.title.string if soup.title else "無標題",
            "main_text": extract_text(soup)
        }
        
        # 根據 sections 的需求篩選
        filtered_result = {}
        if 'title' in sections:
            filtered_result['title'] = result['title']
        if 'main_text' in sections:
            filtered_result['main_text'] = result['main_text']
        
        # 返回篩選後的結果
        return jsonify(filtered_result if filtered_result else result)  # 若未指定 sections，返回完整 result
    
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"請求錯誤: {str(e)}"}), 500
    
    except requests.exceptions.Timeout:
        logging.error(f"請求超時：{url}")
        return jsonify({"error": "請求超時，請稍後再試"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"請求錯誤: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"爬蟲出錯：{url}, 錯誤：{e}")
        return jsonify({"error": f"爬蟲出錯: {str(e)}"}), 500



@user_scrape_bp.route('/user_scrape/full', methods=['POST'])
def user_scrape_full():
    """根據用戶選擇的範圍爬取完整內容"""
    url = request.json.get('url')  # 從用戶請求中獲取 URL
    text_length = request.json.get('text_length', 1000)  # 預設返回的字數（默認 1000 字）
    keywords = request.json.get('keywords', [])  # 可選的多個關鍵字篩選（默認為空）

    # 驗證 URL 的有效性
    if not url or not is_valid_url(url):
        return jsonify({"error": "請提供有效網址"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    try:
        # 發送 HTTP 請求以取得網頁內容
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200 or not response.text:
            return jsonify({"error": f"爬取失敗，狀態碼: {response.status_code}"}), 500

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取標題
        title = soup.title.string if soup.title else "無標題"

        # 提取頁面全文
        full_text = soup.get_text(strip=True)

        # 關鍵字篩選邏輯
        if keywords:  # 若提供了關鍵字，進行篩選
            matched_keywords = [kw for kw in keywords if kw.lower() in title.lower()]
            if not matched_keywords:  # 若未匹配到任何關鍵字
                return jsonify({"error": f"標題 '{title}' 不包含任何指定關鍵字"}), 400

        # 返回指定範圍內的全文內容
        return jsonify({
            "title": title,
            "text": full_text[:text_length]  # 返回用戶選擇範圍內的內容
        })

    # 捕捉各種異常並回傳錯誤訊息
    except requests.exceptions.InvalidURL:
        return jsonify({"error": "提供的 URL 無效"}), 400
    except requests.exceptions.Timeout:
        return jsonify({"error": "請求超時，請稍後再試"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"請求錯誤: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"爬蟲出錯: {str(e)}"}), 500
