import requests
from bs4 import BeautifulSoup
import random
from flask import Blueprint, jsonify

# 定義 Blueprint，提供國際新聞的 API 路由
international_news_bp = Blueprint("international_news", __name__)

# 爬取 BBC 新聞
import requests
from bs4 import BeautifulSoup
import random

def fetch_bbc_news():
    url = "https://www.bbc.com/news"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到父元素
    articles = soup.find_all("div", class_="sc-c6f6255e-0 eGcloy")

    # **🔥 先篩選出有圖片的新聞**
    filtered_articles = []
    for article in articles:
        image_tag = article.find("img", class_="sc-a34861b-0 efFcac")
        image_link = image_tag["src"] if image_tag and image_tag.get("src") else None

        if image_link:  # 只有有圖片的新聞才加入
            filtered_articles.append(article)

    # **🔥 再從有圖片的新聞隨機選擇兩則**
    selected_articles = random.sample(filtered_articles, min(2, len(filtered_articles))) if filtered_articles else []

    # 組合結果
    results = []
    for article in selected_articles:
        title_tag = article.find("h2")
        title = title_tag.text.strip() if title_tag else "無標題"

        summary_tag = article.find("p")
        summary = summary_tag.text.strip() if summary_tag else "Maybe you should check it out ?"

        link_tag = article.find("a")
        link = "https://www.bbc.com" + link_tag["href"] if link_tag and link_tag.get("href") else "#"

        results.append({
            "title": title,
            "link": link,
            "summary": summary,
            "image_link": image_link,  # 🔥 確保圖片已存在
            "source": "BBC",
        })

    return results if results else [{"title": "無法獲取 BBC 新聞", "link": "#", "summary": "請稍後再試", "image_link": "https://via.placeholder.com/150", "source": "BBC"}]

# 爬取 Al Jazeera 新聞
def fetch_aljazeera_news():
    url = "https://www.aljazeera.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到新聞區塊
    articles = soup.find_all("article", class_="gc u-clickable-card gc--type-post gc--with-image")
    # print("✅ 找到:", articles)
    # print("✅✅✅✅✅✅✅✅ ")

     # **🔥 先篩選出有圖片的新聞**
    filtered_articles = []
    for article in articles:
        image_tag = article.find("img", class_="article-card__image gc__image")
        # print("✅ 找到圖片:", image_tag)  # Debug: 確認圖片解析成功
        # print("✅✅---------✅✅ ")

        # **🔥 使用 `srcset` 或 `src` 來獲取圖片**
        if image_tag and image_tag.has_attr("src"):
            image_link = image_tag["src"]
        else:
            image_link = None

        # 拼接完整圖片網址
        if image_link and image_link.startswith("/"):
            image_link = "https://www.aljazeera.com" + image_link
            # print(image_link)
            # print("✅-✅-✅-✅-✅ ")
        # 此處應該添加:
        if image_link:
            filtered_articles.append((article, image_link))

    # **🔥 從有圖片的新聞隨機選擇兩則**
    selected_articles = random.sample(filtered_articles, min(2, len(filtered_articles))) if filtered_articles else []
    # print("-----找到:---", selected_articles,"-----------")
    # print("XXXXXXXXXXXXXXXXXXX ")
    

    # **🔥 組合結果**
    results = []
    for article, image_link in selected_articles:
        title_tag = article.find("h3", class_="gc__title")
        title = title_tag.text.strip() if title_tag else "無標題"
        # print("✅ 找到標題:", title)  # Debug: 確認標題解析成功
        
        link_tag = article.find("a", class_="u-clickable-card__link")
        link = "https://www.aljazeera.com" + link_tag["href"] if link_tag and link_tag.get("href") else "#"
        # print("✅ 找到連結:", link)  # Debug: 確認新聞連結解析成功
        
        summary_tag = article.find("p", class_="gc__excerpt")
        summary = summary_tag.text.strip() if summary_tag else "Let's take a look at this report !"
        # print("✅ 找到摘要:", summary)  # Debug: 確認摘要解析成功
        
        
        results.append({
            "title": title,
            "link": link,
            "summary": summary,
            "image_link": image_link,  
            "source": "Al Jazeera",
        })
    # print("🔥 最終新聞列表:", results)  # Debug: 確認 `results` 列表不為空

    return results if results else [{"title": "無法獲取 Al Jazeera 新聞", "link": "#", "summary": "請稍後再試", "image_link": "https://via.placeholder.com/150", "source": "Al Jazeera"}]

# 整合隨機抓取各兩則新聞
def fetch_international_news():
    # 從 BBC 和 Al Jazeera 各抓取兩則新聞
    bbc_news = fetch_bbc_news()
    aljazeera_news = fetch_aljazeera_news()
    return aljazeera_news + bbc_news

# API 路由，提供國際新聞資料
@international_news_bp.route("/scrape", methods=["GET"])
def fetch_news_api():
    """ 提供 API，返回隨機各兩則國際新聞 """
    try:
        news = fetch_international_news()
        return jsonify({"message": "成功抓取國際新聞", "data": news}), 200
    except Exception as e:
        return jsonify({"error": f"抓取新聞失敗: {str(e)}"}), 500

# # 運行程式並打印結果
# if __name__ == '__main__':
#     news = fetch_international_news()
#     print("=== 隨機抓取各兩則新聞 ===")
#     for idx, article in enumerate(news, start=1):
#         print(f"新聞 {idx}:")
#         print(f"標題: {article['title']}")
#         print(f"連結: {article['link']}")
#         print(f"摘要: {article['summary']}")
#         print(f"圖片: {article['image_link']}")
#         print(f"圖片: {article['source']}")
#         print("==============================")