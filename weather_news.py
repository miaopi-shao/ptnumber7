# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 22:40:56 2025

@author: OAP-0001
"""

# 程式名稱:weather_new.py 氣象新聞爬蟲

from flask import Blueprint, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(
    level=logging.INFO,  # 預設日誌級別（可以改為 DEBUG 或 WARNING）
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日誌格式
    handlers=[
        logging.StreamHandler()  # 日誌輸出到控制台
    ]
)

logger = logging.getLogger(__name__)  # 獲取日誌記錄器


weather_news_bp = Blueprint('weather_news', __name__, template_folder='templates')

def fetch_weather_news():
    url = "https://www.nownews.com/cat/life/weatherforecast/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    response = requests.get(url, headers=headers, timeout=15)

    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        #print(soup)
        #print("匯報完畢")
        news_items = []
        
        parent_div = soup.find('div', class_='listBlk horizontal')
        if parent_div:
            ul_element = parent_div.find('ul')
            if ul_element:
                list_block = ul_element.find_all('li')
                # 確保抓到 li
            else:
                logger.warning("找不到 <ul> 元素")
                #print("找不到 <ul>")
        else:
            logger.warning("找不到目標 <div> 元素")
            #print("找不到目標 <div> 元素")


        #print(list_block)
        #print("匯報完畢")
        

        for item in list_block:
            link = item.find('a', class_='trace-click')['href'] if item.find('a', class_='trace-click') else None
            
            title = item.find('h2')
            #print(title)
            print("匯報完畢")
            title_text = title.text.strip() if title else "無標題"
            
            image = item.find('img')
            img_url = image['src'] if image else None

            description = item.find('p')
            description_text = description.text.strip() if description else "無摘要"

            time = item.find('p', class_='time')
            publish_time = time.text.strip() if time else "無發布時間"
            
            source = "nownews"
            
            news_items.append({
                'title': title_text,
                'link': link,
                'image_link': img_url,
                'source': source,
                'description': description_text,
                'publish_time': publish_time
            })
        logger.info("新聞爬取完成")
        return news_items
    else:
        logger.info("新聞爬取失敗")
        #print("失敗")
        return []

# import time
# start = time.time()
# fetch_weather_news()
# end = time.time()
# print(f"爬取完成時間: {end - start} 秒")


@weather_news_bp.route("/news_block")
def fetch_news():
    news_items = fetch_weather_news()
    logger.info(f"fetch_news 路由抓取的資料: {news_items}")
    return render_template('news_block.html', news_items=news_items)

@weather_news_bp.route("/latest_news")
def latest_news():
    news_items = fetch_weather_news()  # 爬取新聞資料
    logger.info(f"抓取到的新聞: {news_items}")  # 調試檢查
    return render_template('index-3.html', news_items=news_items)  # 傳遞數據

@weather_news_bp.route("/news_items")
def get_news_items():
    news_items = fetch_weather_news()
    logger.debug("以 JSON 格式返回新聞資料")
    return jsonify(news_items)


# if __name__ == '__main__':
#     news = fetch_weather_news()
#     print(news)