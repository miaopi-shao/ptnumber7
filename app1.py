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


from flask import Flask, request, jsonify, render_template
import sqlite3
import hashlib

app = Flask(__name__)

# 初始化資料庫
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()  # 啟動時建立資料表

# 習慣用語轉換密碼（允許選擇部分代碼）
def phrase_to_password(phrase, keep_every_n=1):
    unicode_string = ''.join(str(ord(char)) for char in phrase)  # 轉換成 Unicode
    selected_chars = unicode_string[::keep_every_n]  # 讓使用者選擇保留部分代碼
    hashed_password = hashlib.sha256(selected_chars.encode()).hexdigest()  # SHA-256 加密
    return hashed_password

# 首頁
@app.route('/')
def index():
    return render_template('index.html')

# 註冊 API
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    phrase = data.get('phrase')
    keep_every_n = int(data.get('keep_every_n', 1))  # 使用者選擇保留第幾個代碼

    if not username or not phrase:
        return jsonify({"error": "請提供使用者名稱和習慣用語"}), 400

    password = phrase_to_password(phrase, keep_every_n)  

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "註冊成功"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "使用者名稱已被註冊"}), 400

# 登入 API
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    phrase = data.get('phrase')
    keep_every_n = int(data.get('keep_every_n', 1))

    if not username or not phrase:
        return jsonify({"error": "請提供使用者名稱和習慣用語"}), 400

    password = phrase_to_password(phrase, keep_every_n)

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0] == password:
        return jsonify({"message": "登入成功"})
    else:
        return jsonify({"error": "帳號或密碼錯誤"}), 401

if __name__ == '__main__':
    app.run(debug=True)