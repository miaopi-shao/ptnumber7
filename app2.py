# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 11:01:05 2025

@author: OAP-0001
"""

from flask import Flask, request, jsonify
import hashlib
import os

app = Flask(__name__)

# 模擬使用者資料存儲（實際應該用資料庫）
users = {}

# 轉換習慣用語為密碼（加鹽 + SHA-256）
def phrase_to_password(phrase, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()  # 生成隨機鹽值

    salted_phrase = phrase + salt  # 加鹽
    hashed_password = hashlib.sha256(salted_phrase.encode()).hexdigest()
    
    return hashed_password, salt  # 回傳加密後密碼與鹽值

# 註冊 API
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "請求體必須為 JSON 格式"}), 400
    
    username = data.get('username')
    phrase = data.get('phrase')

    if not username or not phrase:
        return jsonify({"error": "請提供使用者名稱和習慣用語"}), 400

    if username in users:
        return jsonify({"error": "使用者名稱已被註冊"}), 400

    password, salt = phrase_to_password(phrase)  # 轉換密碼
    users[username] = {"password": password, "salt": salt}  # 模擬存入資料庫

    return jsonify({"username": username, "encrypted_password": password})

# 登入 API
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "請求體必須為 JSON 格式"}), 400
    
    username = data.get('username')
    phrase = data.get('phrase')

    if not username or not phrase:
        return jsonify({"error": "請提供使用者名稱和習慣用語"}), 400

    if username not in users:
        return jsonify({"error": "使用者不存在"}), 404

    stored_password = users[username]["password"]
    stored_salt = users[username]["salt"]
    hashed_password, _ = phrase_to_password(phrase, stored_salt)

    if hashed_password == stored_password:
        return jsonify({"message": "登入成功！"})
    else:
        return jsonify({"error": "密碼錯誤"}), 401

if __name__ == '__main__':
    app.run(debug=True)
