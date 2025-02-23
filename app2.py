# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 18:34:21 2025

@author: OAP-0001
"""
"""
簡易前後端框架示例
工具：Flask、SQLite、雲端檔案上傳（模擬）、爬蟲工具 (requests+BeautifulSoup)
"""

"""
from flask import Flask, render_template, request, jsonify request, redirect, url_for
import hashlib, os

# 資料庫整合
from flask_sqlalchemy import SQLAlchemy

# 爬蟲功能 (requests + BeautifulSoup)
import requests
from bs4 import BeautifulSoup
# 爬蟲功能 (追加模式)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#搜尋引擎
from search_engine import search_bp  # 引入搜尋引擎 Blueprint





# 開始運行
app = Flask(__name__)
app.register_blueprint(search_bp)  # 註冊搜尋引擎的 Blueprint

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)



# 轉換習慣用語為密碼的函數
def phrase_to_password(phrase):
    # 將習慣用語轉換為 Unicode 數字串
    unicode_string = ''.join(str(ord(char)) for char in phrase)
    # 使用 SHA-256 加密該數字串
    hashed_password = hashlib.sha256(unicode_string.encode()).hexdigest()
    return hashed_password



# 呈現網頁區域
@app.route('/')
def index():
    return render_template('index.html')



# 註冊 API
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    phrase = data.get('phrase')
    keep_every_n = data.get('keep_every_n', 1)

    if not username or not phrase:
        return jsonify({"error": "請提供使用者名稱和習慣用語"}), 400
    
    # 這裡可以不用重複檢查 username 與 phrase（已在前面檢查過）
    password = phrase_to_password(phrase)
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"username": username, "encrypted_password": password})

# 雲端檔案上傳模擬
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(f'uploads/{file.filename}')
    return jsonify({"message": "檔案上傳成功"})

if __name__ == '__main__':
    app.run(debug=True)




# 爬蟲功能 (requests + BeautifulSoup)
@app.route('/scrape', methods=['GET'])
def scrape():
    
    # 取得使用者指定的爬取方式：預設使用 requests 方法
    method = request.args.get('method', 'requests') # 預設使用 requests 方法
    url = "https://www.example.com"  # 目標網站
    target_class = "some-class"  # 目標 HTML 類別
    
    # --- Selenium 爬蟲邏輯 ---
    def selenium_scrape(headless=True):
        try:
            chrome_options = webdriver.ChromeOptions()
            if headless:
                chrome_options.add_argument("--headless")  # 無頭模式
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
    
            service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)

            # **使用 WebDriverWait 等待 JavaScript 加載**
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, target_class)))
                
            except Exception:
                driver.quit()
                return jsonify({"error": "Selenium 爬取失敗：目標內容未載入"}), 500

            # 解析 HTML
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            data_element = soup.find('div', {'class': target_class})
            if not data_element:
                return jsonify({"error": "Selenium 爬取失敗：找不到目標內容"}), 500

            return jsonify({"scraped_data": data_element.text.strip()})
    
        except Exception as e:
            return jsonify({"error": f"Selenium 爬取出錯: {str(e)}"}), 500

    # --- Requests 爬蟲邏輯 ---
    if method == 'requests':
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers)

            if response.status_code != 200 or not response.text:
                 return jsonify({"error": f"requests 爬取失敗，狀態碼: {response.status_code}"}), 500

            soup = BeautifulSoup(response.text, 'html.parser')
            data_element = soup.find('div', {'class': target_class})
            if not data_element:
                return jsonify({"error": "requests 爬取失敗：找不到目標內容"}), 500

            return jsonify({"scraped_data": data_element.text.strip()})

        except Exception as e:
            return jsonify({"error": f"requests 爬取出錯: {str(e)}"}), 500

    elif method == 'selenium_headless':
         return selenium_scrape(headless=True)

    elif method == 'selenium_visible':
        return selenium_scrape(headless=False)

    else:
        return jsonify({"error": "未知的爬取方式，請使用 'selenium_headless', 'selenium_visible' 或 'requests'"}), 400
    
    
    
""" 
"""   
    if method in ['selenium_headless', 'selenium_visible']:
        try:
            chrome_options = webdriver.ChromeOptions()
            # 若選擇無頭模式，就添加 headless 參數
            if method == 'selenium_headless':
                chrome_options.add_argument("--headless")
            # 若選擇明爬，就不要添加 headless 參數，瀏覽器窗口會顯示
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            driver.get("https://www.example.com")
            page_source = driver.page_source
            driver.quit()
            
            soup = BeautifulSoup(page_source, 'html.parser')
            data = soup.find('div', {'class': 'some-class'}).text
            return jsonify({"scraped_data": data})
        except Exception as e:
            return jsonify({"error": f"Selenium 爬取出錯: {str(e)}"}), 500
        
        
    elif method == 'requests':
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
                }
            response = requests.get("https://www.example.com", headers=headers)

            if response.status_code != 200 or not response.text.strip():
               return jsonify({"error": f"requests 爬取失敗，狀態碼: {response.status_code}"}), 500

            soup = BeautifulSoup(response.text, 'html.parser')
            data_element = soup.find('div', {'class': 'some-class'})

            if data_element:  # 確保找到了內容
               data = data_element.text.strip()
            else:
                return jsonify({"error": "requests 爬取失敗：找不到目標內容"}), 500

            return jsonify({"scraped_data": data})

        except Exception as e:
            return jsonify({"error": f"requests 爬取出錯: {str(e)}"}), 500
        
        
    elif method in ['selenium_headless', 'selenium_visible']:
        try:
            chrome_options = webdriver.ChromeOptions()
        
            # 設定無頭模式
            if method == 'selenium_headless':
                chrome_options.add_argument("--headless")
        
            # 減少資源占用
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")

            service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
            driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.get("https://www.example.com")

            # 等待 JavaScript 加載
            import time
            time.sleep(3)

            page_source = driver.page_source
            driver.quit()

            soup = BeautifulSoup(page_source, 'html.parser')
            data_element = soup.find('div', {'class': 'some-class'})

            if data_element:
                data = data_element.text.strip()
            else:
                return jsonify({"error": "Selenium 爬取失敗：找不到目標內容"}), 500

            return jsonify({"scraped_data": data})

        except Exception as e:
            return jsonify({"error": f"Selenium 爬取出錯: {str(e)}"}), 500
    
    
    else:
        return jsonify({"error": "未知的爬取方式，請使用 'selenium_headless', 'selenium_visible' 或 'requests'"}), 400
    '''
    說明：
      環境依賴：
           若選擇 Selenium，請務必確保服務器中已安裝 Google Chrome 與正確配置的 ChromeDriver。
           若使用 requests，就完全不依賴瀏覽器，只需網路連線即可。

      選擇方式：
           使用者可以在 URL 中加入參數，例如：

            1. /scrape?method=selenium_headless 使用 Selenium 無頭模式
            2. /scrape?method=selenium_visible 使用 Selenium 明爬
            3. /scrape?method=requests 使用純 requests 模式
         彈性：
           這種設計不僅能讓你根據不同場景靈活選擇爬蟲方式，也能在開發和除錯時更方便調試（例如，明爬可以直觀看到瀏覽器行為）。

      這樣一來，就不再局限於單一的 Google Chrome 環境，也能根據具體需求選擇合適的爬取方式。正如我們常說的：不想被綁死在某個工具上，就得給使用者多種選擇，讓他們自由搭配！
    '''


"""
"""
# 啟動 Flask 應用
if __name__ == '__main__':
    app.run(debug=True)
    
"""    