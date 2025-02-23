# -*- coding: utf-8 -*-
"""
天氣資訊 API 模組
"""
# -*- coding: utf-8 -*-
"""
天氣資訊 API 模組
"""
import os
import requests
from flask import Blueprint, jsonify, request

# 建立 Blueprint
weather_bp = Blueprint("weather", __name__)

# API 金鑰（應該放到環境變數）
API_KEY = os.getenv("CWB_API_KEY", "CWA-6C6AA47F-5E18-41C3-A3E9-A7D5ED720777")

# 支援的縣市列表
CITY_LIST = [
    "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
    "基隆市", "新竹市", "新竹縣", "苗栗縣", "彰化縣", "南投縣",
    "雲林縣", "嘉義市", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣",
    "澎湖縣", "金門縣", "連江縣"
]

# 取得天氣資訊的函數
def get_weather(city):
    if city not in CITY_LIST:
        return {"error": "不支援的城市"}

    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={API_KEY}&format=JSON"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "無法取得天氣資料"}

    data = response.json()
    weather_info = {}

    for loc in data["records"]["location"]:
        if loc["locationName"] == city:
            weather_info["city"] = city
            weather_info["condition"] = loc["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            weather_info["temperature"] = loc["weatherElement"][4]["time"][0]["parameter"]["parameterName"]
            return weather_info

    return {"error": "找不到指定城市的天氣資訊"}

# 設定 API 端點，讓前端可以請求不同城市的天氣
@weather_bp.route("/api/weather", methods=["GET"])
def weather_api():
    city = request.args.get("city", "臺北市")  # 預設為臺北市
    return jsonify(get_weather(city))
