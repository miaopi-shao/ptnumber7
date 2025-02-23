# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 18:25:06 2025

@author: OAP-0001
"""

# auth.py 帳號註冊用函式
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

def phrase_to_password(phrase):
    """ 使用 SHA-256 進行加密，並加上安全鹽值 """
    if len(phrase) < 8:
        return None, "習慣用語長度至少 8 個字"

    # 加鹽 (增加隨機性，提高安全性)
    hashed_password = generate_password_hash(phrase, method='pbkdf2:sha256')
    return hashed_password, None

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    phrase = data.get('phrase')

    if not username or not phrase:
        return jsonify({"error": "請提供使用者名稱和習慣用語"}), 400

    # 檢查帳號是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "帳號已被註冊"}), 400

    # 產生加密密碼
    password, error = phrase_to_password(phrase)
    if error:
        return jsonify({"error": error}), 400

    # 儲存到資料庫
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "註冊成功", "username": username})
