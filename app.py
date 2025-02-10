# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 18:34:21 2025

@author: OAP-0001
"""

# -*- coding: utf-8 -*-
"""
簡易前後端框架示例
工具：Flask、SQLite、雲端檔案上傳（模擬）、爬蟲工具 (requests+BeautifulSoup)
"""


from flask import Flask, render_template, request, jsonify
import hashlib

app = Flask(__name__)

# 轉換習慣用語為密碼的函數
def phrase_to_password(phrase):
    # 將習慣用語轉換為 Unicode 數字串
    unicode_string = ''.join(str(ord(char)) for char in phrase)
    # 使用 SHA-256 加密該數字串
    hashed_password = hashlib.sha256(unicode_string.encode()).hexdigest()
    return hashed_password

# 註冊頁面顯示
@app.route('/')
def index():
    # 渲染 index.html 頁面
    return render_template('index.html')

# 註冊 API
@app.route('/register', methods=['POST'])
def register():
    # 取得 POST 請求的 JSON 數據
    data = request.json
    username = data.get('username')  # 取得帳號
    phrase = data.get('phrase')  # 取得習慣用語
    keep_every_n = data.get('keep_every_n', 1)  # 取得保留代碼的間隔 (預設為 1)

    # 如果帳號或習慣用語缺少，返回錯誤信息
    if not username or not phrase:
        return jsonify({"error": "請提供使用者名稱和習慣用語"}), 400

    # 將習慣用語轉換為密碼
    password = phrase_to_password(phrase)
    # 在這裡應該將密碼保存到資料庫（這裡省略）

    # 返回帳號和加密後的密碼
    return jsonify({"username": username, "encrypted_password": password})

# 啟動 Flask 應用
if __name__ == '__main__':
    app.run(debug=True)