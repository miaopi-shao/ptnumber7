# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 18:25:06 2025

@author: OAP-0001
"""
#帳號密碼運作區
#pip install python-dotenv

import os
os.environ["JWT_SECRET"] = "test_jwt_secret"
os.environ["JWT_SECRET"] = "test_jwt_secret"
os.environ["EMAIL_USER"] = "test@example.com"
os.environ["EMAIL_PASS"] = "test_password"
os.environ["SMTP_SERVER"] = "test.smtp.com"


# 從 Flask 框架中匯入 Blueprint（藍圖）、request（請求）和 jsonify（JSON 化）模組
from flask import Blueprint, request, jsonify

# 從 werkzeug.security 模組中匯入 generate_password_hash（生成密碼雜湊）和 check_password_hash（檢查密碼雜湊）函式
from werkzeug.security import generate_password_hash, check_password_hash

# 從自定義的 models 模組中匯入 db（資料庫）和 User（使用者）類別
from models import db, User

# 匯入 Python 標準庫中的 hashlib（雜湊函式庫）模組
import hashlib

# 匯入 Python 標準庫中的 random（隨機數）模組
import random

# 匯入 Python 標準庫中的 string（字串處理）模組
import string

# 匯入 Python 標準庫中的 smtplib（簡單郵件傳輸協定）模組
import smtplib

# 匯入 Python 標準庫中的 os（作業系統介面）模組
import os

# 從 dotenv 模組中匯入 load_dotenv（載入環境變數）函式
from dotenv import load_dotenv

# 從 email.mime.text 模組中匯入 MIMEText（MIME 文本）類別
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



"""
# ... 執行測試 ...
import os
del os.environ["JWT_SECRET"]  # 測試完成後刪除環境變數
del os.environ["JWT_SECRET"]
del os.environ["EMAIL_USER"]
del os.environ["EMAIL_PASS"]
del os.environ["SMTP_SERVER"]








額外準備.env檔

JWT_SECRET=你的JWT秘密金鑰
EMAIL_USER=你的郵件發送帳號
EMAIL_PASS=你的郵件發送密碼
SMTP_SERVER=你的SMTP伺服器

存放進通區域資料夾

詳細說明：

1.JWT_SECRET：
   這是一個用於簽署 JSON Web Tokens (JWT) 的秘密金鑰。JWT 用於身份驗證和授權。
   你需要生成一個強隨機的秘密金鑰。你可以使用線上工具或 Python 的 secrets 模組來生成。
      例如：JWT_SECRET=your_strong_random_secret_key
2.EMAIL_USER：
   這是你用於發送電子郵件的電子郵件帳號。
   例如：EMAIL_USER=your_email@example.com
3.EMAIL_PASS：
   這是你用於發送電子郵件的電子郵件帳號的密碼。
   重要： 為了安全起見，建議你使用應用程式專用密碼，而不是你的主要電子郵件密碼。
   例如：EMAIL_PASS=your_email_password
4.SMTP_SERVER：
   這是你的 SMTP 伺服器地址。
   如果你使用 Gmail，則為 smtp.gmail.com。
   如果你使用其他電子郵件提供者，請查閱其文件以獲取正確的 SMTP 伺服器地址。
   例如：SMTP_SERVER=smtp.gmail.com


紀錄案例:
    .env 檔案範例：
    JWT_SECRET=aVeryStrongRandomSecretKey123
    EMAIL_USER=your_email@gmail.com
    EMAIL_PASS=your_application_specific_password
    SMTP_SERVER=smtp.gmail.com
    
注意事項:
    將 .env 檔案放在你的專案根目錄中，與你的 Python 程式碼檔案在同一個目錄中。
    確保你的 .env 檔案內容格式正確，每一行都是 KEY=VALUE 的形式。
    不要將 .env 檔案提交到版本控制系統（例如 Git），以避免洩露敏感資訊。
    如果使用gmail，請確認你的gmail有開啟，允許程式登入。
    通過準備這些環境變數，你的程式碼就可以從 .env 檔案中讀取敏感資訊，而不會將它們直接寫在程式碼中。
    
"""