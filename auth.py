# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 18:25:06 2025

@author: OAP-0001
"""
#帳號密碼運作區
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import hashlib
import random
import string
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

# 載入 .env 檔案中的環境變數
load_dotenv()

# 讀取環境變數（避免敏感資訊直接寫在程式碼中）
SECRET_KEY = os.getenv("JWT_SECRET")  # JWT 秘密金鑰
EMAIL_USER = os.getenv("EMAIL_USER")  # 郵件發送帳號
EMAIL_PASS = os.getenv("EMAIL_PASS")  # 郵件發送密碼
SMTP_SERVER = os.getenv("SMTP_SERVER")  # SMTP 伺服器

# 建立 Blueprint（Flask 藍圖），讓 `auth` API 具有獨立的路由
auth_bp = Blueprint('auth', __name__)

# --------------------- 工具函式 ---------------------

def phrase_to_password(phrase):
    """ 將習慣用語轉換為加密密碼（至少 8 個字） """
    if len(phrase) < 8:
        return None, "習慣用語長度至少 8 個字"

    hashed_password = generate_password_hash(phrase, method='pbkdf2:sha256')
    return hashed_password, None

def encode_morse(text):
    """ 將文字轉換為摩斯密碼，並回傳加密的 SHA-256 雜湊 """
    morse_code_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
        'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
        '3': '...--', '4': '....-', '5': '.....', '6': '-....',
        '7': '--...', '8': '---..', '9': '----.'
    }
    text = text.upper()
    morse_code = ' '.join(morse_code_dict[char] for char in text if char in morse_code_dict)
    hashed_morse = hashlib.sha256(morse_code.encode()).hexdigest()
    return hashed_morse

# --------------------- 註冊 API ---------------------

@auth_bp.route('/register', methods=['POST'])
def register():
    """ 使用者註冊功能，帳號經摩斯密碼加密，密碼經 PBKDF2 加密 """
    data = request.json
    username = data.get('username')  # 使用者帳號
    phrase = data.get('phrase')  # 使用者習慣用語（作為密碼）
    email = data.get('email')  # 使用者電子郵件

    if not username or not phrase or not email:
        return jsonify({"error": "請提供使用者名稱、習慣用語和電子郵件"}), 400

    # 確保帳號與 Email 不重複
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "帳號已被註冊"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "電子郵件已被使用"}), 400

    # 帳號摩斯密碼加密 + SHA-256
    hashed_username = encode_morse(username)

    # 習慣用語轉換成密碼
    password, error = phrase_to_password(phrase)
    if error:
        return jsonify({"error": error}), 400

    # 新增使用者至資料庫
    user = User(username=hashed_username, password=password, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "註冊成功", "username": username})

# --------------------- 忘記密碼 API ---------------------

@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    """ 忘記密碼功能，寄送臨時密碼至使用者電子郵件 """
    data = request.json
    email = data.get('email')

    # 檢查 Email 是否存在
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "電子郵件未註冊"}), 400

    # 產生 10 碼隨機臨時密碼
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    user.password = generate_password_hash(temp_password, method='pbkdf2:sha256')
    db.session.commit()

    # 發送臨時密碼到 Email
    send_email(email, temp_password)

    return jsonify({"message": "臨時密碼已發送至您的電子郵件"})

def send_email(email, temp_password):
    """ 發送電子郵件，內含臨時密碼 """
    subject = "忘記密碼 - 臨時密碼"
    body = f"您的臨時密碼為：{temp_password}，請盡快登入並修改您的密碼。"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = email

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)  # 使用 .env 變數進行登入
            server.sendmail(EMAIL_USER, email, msg.as_string())
        print("✅ 郵件發送成功！")
    except Exception as e:
        print("❌ 郵件發送失敗：", e)
