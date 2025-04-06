# -*- coding: utf-8 -*-
"""
Created on Sun Apr  6 16:34:01 2025

@author: OAP-0001
"""
#程式名稱:vogue.py 娛樂網專用

import requests
from bs4 import BeautifulSoup
import random

def vogue_news():
    """ 爬取 Vogue Taiwan 名人新聞，返回新聞資訊列表 """
    
    base_url = "https://www.vogue.com.tw"
    news_url = f"{base_url}/entertainment/celebritynews"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(news_url, headers=headers)
    news_list = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        container = soup.find("div", class_="SummaryCollectionGridItems-DZShR eNzUZM hide-read-more-ad")

        if container:
            articles = container.find_all("a")

            for article in articles:
                title = article.get_text().strip()
                # 如果沒有標題，則跳過此文章
                if not title:
                    continue

                link = article["href"]
                full_link = link if link.startswith("http") else base_url + link

                # 進一步爬取新聞詳細資訊
                article_response = requests.get(full_link, headers=headers)
                if article_response.status_code == 200:
                    article_soup = BeautifulSoup(article_response.text, "html.parser")

                    # 抓取圖片
                    img_tag = article_soup.find("meta", property="og:image")
                    img_url = img_tag["content"] if img_tag else "無圖片"

                    # 抓取作者
                    author_tag = article_soup.find("span", {"data-testid": "BylineName"}) 
                    if not author_tag:  # 如果第一個方法找不到，就嘗試 class 選擇器
                        author_tag = article_soup.find("span", class_="BylineName-kwmrLn cYaBcc byline__name")  
                    
                    author = author_tag.get_text().strip() if author_tag else "未知作者"
                    author = author.replace("By", "發布者 : ").strip()  # 🔥 移除 "BY"
                    
                    summary = "請點選內容前往察看\n原文提供更多內容"

                    # 抓取日期
                    date_tag = article_soup.find("time")
                    date = date_tag.get_text().strip() if date_tag else "未知日期"

                    news_list.append({
                        "title": title,
                        "link": full_link,
                        "image_link": img_url,
                        "summary": summary,
                        "author": author,
                        "date": date,
                    })

    # 如果爬取到的新聞超過 3 筆，隨機選出 3 筆返回
    if len(news_list) > 9:
        news_list = random.sample(news_list, 9)
    
    return news_list



if __name__ == "__main__":
    news = vogue_news()
    for item in news:
        print(f"📰 標題: {item['title']}\n🔗 連結: {item['link']}\n🖼 圖片: {item['image_link']}\n✍ 作者: {item['author']}\n📅 日期: {item['date']}\n")
