# -*- coding: utf-8 -*-
"""
天氣資訊 API 模組
"""
# -*- coding: utf-8 -*-
"""
天氣資訊 API 模組
"""
import json#爬取成果測試

import os
import requests
from flask import Blueprint, jsonify, request
from datetime import datetime

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


# 取得日出日落資訊的函數
def get_sunrise_sunset(city, date):
    try:
       # 日出日落 API URL
       SUN_API_URL = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/A-B0062-001?Authorization={API_KEY}&format=JSON"
       response = requests.get(SUN_API_URL)
       response.raise_for_status()  # 確保 API 回應成功 (HTTP 200)

       # 解析 API 回傳的 JSON 資料
       data = response.json()
       #print("日出日落 API 回應資料：", json.dumps(data, indent=1, ensure_ascii=False))
       
       #print("日出日落 API 回應資料：", data)
       locations = data.get("records", {}).get("locations", {}).get("location", [])
       # 假設目標節點是 locations
       #print(json.dumps(locations[:10], indent=4, ensure_ascii=False))  # 只顯示前10筆資料
       
       # 儲存 API 回傳的完整 JSON 資料到檔案
       # with open("sunrise_sunset_debug.json", "w", encoding="utf-8") as f:
       #     json.dump(data, f, ensure_ascii=False, indent=4)
       # print("完整 JSON 資料已儲存到 sunrise_sunset_debug.json")
       
       #print(f"正在尋找 {city} 的日出日落資料，日期為 {date}...")
       #print("locations:", locations)
       for location in locations:
           #print(f"正在檢查的縣市名稱：{location.get('CountyName')}")
           # 匹配縣市名稱
           if location.get("CountyName") == city:
               #print(f"匹配到縣市：{city}")
               target_date_info = next((time_info for time_info in location.get("time", []) if time_info.get("Date") == date), None)
        
               #for time_info in location.get("time", []):
                   #print(f"正在檢查的日期：{time_info.get('Date')}")
                   # 匹配日期
                   #if time_info.get("Date") == date:
                      # print("匹配成功！")
               if target_date_info:
                   print("匹配成功！")
                   SunRiseTime = target_date_info.get("SunRiseTime", "未知")
                   SunSetTime = target_date_info.get("SunSetTime", "未知")
                   # SunRiseTime = time_info.get("SunRiseTime", "未知")
                   # SunSetTime = time_info.get("SunSetTime", "未知")
                   #print(f"找到日出日落資料：日出 {SunRiseTime}，日落 {SunSetTime}")
                   return {"SunRiseTime": SunRiseTime, "SunSetTime": SunSetTime}
               else:
                   print(f"未找到匹配日期 {date} 的資料。")
                   #print(f"日期 {time_info.get('Date')} 與 {date} 不符。匹配失敗。")
           else:
               print(f"縣市名稱 {location.get('CountyName')} 與 {city} 不符。匹配失敗。")

       # 若未找到資料
       print("未找到匹配的資料")
       return {"SunRiseTime": "不明", "SunSetTime": "不明"}

    except Exception as e:
        print(f"取得日出日落資料時發生錯誤: {e}")
        return {"SunRiseTime": "不知", "SunSetTime": "不知"}


# 取得天氣資訊的函數
def get_weather(city):
    if city not in CITY_LIST:
        return {"error": "不支援的城市"}

    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={API_KEY}&format=JSON"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "無法取得天氣資料"}

    data = response.json()
    # 印出整個 API 回傳的資料，方便查看數據結構
    # print("完整天氣資料：", json.dumps(data, indent=2, ensure_ascii=False))#了解爬取總資訊及分類

    #weather_info = {}

    for loc in data["records"]["location"]:
        if loc["locationName"] == city:#根據前端反饋的縣市，提供對應的資料
            weather_info = {} #創建一個字典形式的儲存空間
            weather_info["city"] = city #創建city對應 城市
            
            # 依照 API 回傳結構：
            # 索引：0: Wx, 1: PoP, 2: MinT, 3: CI, 4: MaxT
            Wx = loc["weatherElement"][0]["time"][0]["parameter"]
            PoP = loc["weatherElement"][1]["time"][0]["parameter"]
            MinT = loc["weatherElement"][2]["time"][0]["parameter"]
            CI = loc["weatherElement"][3]["time"][0]["parameter"]
            MaxT = loc["weatherElement"][4]["time"][0]["parameter"]
            
            # 平均溫度：(MaxT + MinT) / 2
            try:
                avg_temp = (int(MaxT["parameterName"]) + int(MinT["parameterName"])) / 2
            except Exception:
                avg_temp = "--"
            weather_info["temperature"] = avg_temp
            
            
            # 體感溫度：直接輸出 Wx 的 parameterName (氣象局中文描述)
            weather_info["feels_like"] = CI["parameterName"]
            
            # 下雨機率：使用 PoP 的 parameterName，加上百分比
            weather_info["humidity"] = PoP["parameterName"] + "%"
            
            # 最高溫|最低溫：顯示格式 "MaxT°C|MinT°C"
            weather_info["wind_speed"] = f'{MaxT["parameterName"]}°C|{MinT["parameterName"]}°C'
            
            #舒適度指數:直接輸出 Ci 的 parameterName (氣象局中文描述)
            weather_info["ci"] = CI["parameterName"]
            
            # 獲取當前日期
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 保留欄位
            # 日出、日落、氣壓需另找 API 處理，先暫訂此資訊
            sun_times = get_sunrise_sunset(city, today)
            weather_info["SunRiseTime"] = sun_times["SunRiseTime"] #日出時間
            weather_info["SunSetTime"] = sun_times["SunSetTime"]  #日落時間
            
            weather_info["barometer"] = "30.03" #氣壓
            
            # 圖片依據：使用 Wx 的 parameterValue（數值），並返回給前端以便選圖
            weather_info["conditionValue"] = Wx.get("parameterValue", "")
            # 同時保留文字描述
            weather_info["condition"] = Wx["parameterName"]            
           
            #原有資訊欄位，剔除
            # # 這裡根據 API 的返回結構調整
            # #天氣概況
            # weather_info["condition"] = loc["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            # #溫度資料
            # weather_info["temperature"] = loc["weatherElement"][4]["time"][0]["parameter"]["parameterName"]

            # # 對硬體感溫度
            # weather_info["feels_like"] = loc["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
            # #對應相對濕度
            # weather_info["humidity"] = loc["weatherElement"][2]["time"][0]["parameter"]["parameterName"]
            # #對應當下風速
            # weather_info["wind_speed"] = loc["weatherElement"][3]["time"][0]["parameter"]["parameterName"]
            
            # 打印找到的特定城市資料
            #print("解析後的天氣資訊：", json.dumps(weather_info, indent=4, ensure_ascii=False))
            return weather_info

    return {"error": "找不到指定城市的天氣資訊"}




# def print_all_weather():
#     """ 列印所有縣市的天氣現象與降雨機率資料 """
    
#     url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={API_KEY}&format=JSON"
#     response = requests.get(url)
    
#     if response.status_code != 200:
#         print("無法取得天氣資料")
#         return

#     data = response.json()
#     # 使用 json.dumps 加上 indent 讓輸出更整齊
#     # print(json.dumps(data, indent=4, ensure_ascii=False))
    
#     # 遍歷所有地區資料
#     for loc in data["records"]["location"]:
#         print("=" * 40)
#         print("地區：", loc["locationName"])
        
#         # 提取天氣現象（Wx）
#         wx = next((elem for elem in loc["weatherElement"] if elem["elementName"] == "Wx"), None)
#         if wx:
#             print("【天氣現象 Wx】")
#             for period in wx["time"]:
#                 start = period["startTime"]
#                 end = period["endTime"]
#                 description = period["parameter"]["parameterName"]
#                 code = period["parameter"].get("parameterValue", "無")
#                 print(f"從 {start} 到 {end} : {description} (代碼: {code})")
#         else:
#             print("無天氣現象資料")
        
#         # 提取降雨機率（PoP）
#         pop = next((elem for elem in loc["weatherElement"] if elem["elementName"] == "PoP"), None)
#         if pop:
#             print("\n【降雨機率 PoP】")
#             for period in pop["time"]:
#                 start = period["startTime"]
#                 end = period["endTime"]
#                 pop_value = period["parameter"]["parameterName"]
#                 unit = period["parameter"].get("parameterUnit", "")
#                 print(f"從 {start} 到 {end} : {pop_value} {unit}")
#         else:
#             print("無降雨機率資料")
#         print("=" * 40 + "\n")


# 設定 API 端點，讓前端可以請求不同城市的天氣
@weather_bp.route("/api/weather", methods=["GET"])
def weather_api():
    city = request.args.get("city", "臺北市")  # 預設為臺北市
    return jsonify(get_weather(city))



if __name__ == '__main__':
#     result = get_sunrise_sunset("Date")    
#     print("天氣:")
#     for key, value in result.items():
#         print(f"{key}: {value}")
    # 例如测试获取臺北市的天气数据
    result = get_weather("臺北市")    
    print("天氣:")
    for key, value in result.items():
        print(f"{key}: {value}")