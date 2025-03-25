# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 18:25:06 2025

@author: OAP-0001
"""
# 這裡是與帳號、密碼相關的功能區
# 安裝所需的庫： pip install python-dotenv

# --------------------------------- 導入所需模組 ---------------------------------
import os 
from flask import Blueprint, request, jsonify  # Flask 藍圖與 API 回應處理
from werkzeug.security import generate_password_hash, check_password_hash  # 密碼加密與驗證
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity  # JWT 驗證
from models import db, AuthUser # 與資料庫和使用者模型互動
from database import db
import hashlib  # 密碼雜湊處理
import random  # 隨機生成臨時密碼
import string  # 使用字母與數字生成密碼
import smtplib  # 發送電子郵件
from dotenv import load_dotenv  # 環境變數加載
from email.mime.text import MIMEText  # 電子郵件內容格式化
import logging    # 添加日誌記錄功能
import traceback  # 用於追蹤錯誤堆疊
from flask_mail import Mail, Message #Flask 應用集成的郵件發送解決方案

# --------------------------------- 初始化 --------------------------------------
# 建立 Blueprint，讓 `auth` API 具有獨立的路由（這部分是與 app.py 聯繫）
auth_bp = Blueprint('auth', __name__ ) #, url_prefix="/api/auth" # 17. 初始化 auth 藍圖

mail = Mail()
# 載入環境變數
load_dotenv()  # 從 .env 文件載入環境變數
SECRET_KEY = os.getenv("JWT_SECRET", "default_secret")  # JWT 秘密金鑰（默認值）
EMAIL_USER = os.getenv("EMAIL_USER")  # 郵件發送的使用者帳號
EMAIL_PASS = os.getenv("EMAIL_PASS")  # 郵件發送密碼
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")  # SMTP 伺服器
mail = None  # 保留可選使用 flask_mail 的空參數


# -------------------------------- 工具函式 --------------------------------------
def phrase_to_password(phrase):
    """ 將使用者輸入的密碼進行加密 """
    if len(phrase) < 8 or len(phrase) > 16:
        return None, "密碼長度必須在 8 至 16 個字元之間"
    hashed_password = generate_password_hash(phrase, method='pbkdf2:sha256')
    return hashed_password, None

def encode_morse(text):
    """ 將字串轉為摩斯密碼並加密為 SHA256 雜湊值 """
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
    text = text.upper()  # 將所有字母轉大寫
    morse_code = ' '.join(morse_code_dict[char] for char in text if char in morse_code_dict)
    hashed_morse = hashlib.sha256(morse_code.encode()).hexdigest()
    return hashed_morse



# ----------------------------- 登入功能 -----------------------------------------
@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """ 使用者登入並返回 JWT Token """
    data = request.json
    username = data.get('username')
    phrase = data.get('phrase')

    if not username or not phrase:
        return jsonify({"error": "請提供使用者名稱和密碼"}), 400

    hashed_username = encode_morse(username)
    user = AuthUser.query.filter_by(username=hashed_username).first()

    if not user or not check_password_hash(user.password, phrase):
        error_msg = "帳號或密碼錯誤"
        status_code = 404 if not user else 401
        return jsonify({"error": error_msg}), status_code

    access_token = create_access_token(identity=user.id)  # 創建 JWT Token
    logging.info(f"使用者 {username} 成功登入")
    return jsonify({"message": "登入成功", "token": access_token}), 200



# ------------------------------ 取得個人資訊 API ------------------------------

@auth_bp.route('/auth/profile', methods=['GET'])
@jwt_required()  # 驗證用戶是否提供有效的 JWT Token
def profile():
    """ 取得登入使用者的資訊 """
    user_id = get_jwt_identity()  # 從 JWT Token 中解析出用戶 ID
    user = AuthUser.query.get(user_id)  # 根據用戶 ID 從資料庫中查找用戶

    if not user:
        return jsonify({"error": "用戶不存在"}), 404  # 若用戶未找到，返回錯誤

    # 返回用戶的個人資訊
    return jsonify({
        "username": user.username,  # 用戶名稱
        "email": user.email,        # 電子郵件
        "role": user.role,          # 用戶角色（如 admin 或普通用戶）
        "created_at": user.created_at  # 創建時間
    }), 200


# ----------------------------- 註冊功能 -----------------------------------------
@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """ 使用者註冊並存入資料庫 """
    data = request.json
    username = data.get('username')
    phrase = data.get('phrase')
    email = data.get('email')

    if not username or not phrase or not email:
        return jsonify({"error": "請提供完整資訊"}), 400

    if AuthUser.query.filter_by(email=email).first():
        return jsonify({"error": "該電子郵件已被註冊"}), 400

    if len(phrase) < 8 or len(phrase) > 16 or phrase.isdigit() or phrase.isalpha():
        return jsonify({"error": "密碼長度須在 8 至 16 且需包含數字和字母"}), 400

    hashed_username = encode_morse(username)
    hashed_password, error = phrase_to_password(phrase)
    if error:
        return jsonify({"error": error}), 400

    user = AuthUser(username=hashed_username, password=hashed_password, email=email)
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"資料庫錯誤：{e}"}), 500

    # 可選：發送註冊確認電子郵件
    return jsonify({"message": "註冊成功"}), 201


# ----------------------------- 密碼重設功能 -------------------------------------
@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """ 密碼重設功能，向電子郵件發送臨時密碼 """
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"error": "請提供電子郵件"}), 400

    user = AuthUser.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "該電子郵件不存在"}), 404

    # 隨機生成臨時密碼
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    hashed_temp_password = generate_password_hash(temp_password)
    user.password = hashed_temp_password  # 更新密碼
    db.session.commit()

    # 發送郵件
    try:
        msg = MIMEText(f"您的臨時密碼是：{temp_password}")
        msg['Subject'] = "密碼重設通知"
        msg['From'] = EMAIL_USER
        msg['To'] = email

        with smtplib.SMTP(SMTP_SERVER) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
    except Exception as e:
        return jsonify({"error": f"郵件發送失敗：{str(e)}"}), 500

    return jsonify({"message": "臨時密碼已發送"}), 200

# --------------------------------- 帳戶刪除 API -------------------------------

@auth_bp.route('/auth/delete_account', methods=['POST'])  # 定義路由與 HTTP 方法
@jwt_required()  # 僅要求用戶攜帶有效的 JWT Token
def delete_account():
    # 從 Token 中取得當前用戶 ID
    user_id = get_jwt_identity()
    user = AuthUser.query.get(user_id)
    if not user:
        return jsonify({"error": "找不到使用者"}), 404

    # 這裡可以加入額外確認步驟，例如驗證用戶的密碼（從請求中取得）
    password = request.json.get("password")
    if not check_password_hash(user.password, password):
        return jsonify({"error": "密碼驗證失敗"}), 401

    # 刪除用戶並提交變更
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "帳號已成功刪除"}), 200

# --------------------------------- 帳戶刪除 API -------------------------------


# 在該文件中提供 Blueprint 的導出
__all__ = ['auth_bp']

"""
傳統表單提交（POST 表單）的密碼重設方法[需要改整個，暫時先不動]

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form.get('email')
    if not email:
        flash("請提供電子郵件", "error")
        return redirect(url_for('auth.reset_password_page'))  # 假設有個重設密碼頁面

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("用戶不存在", "error")
        return redirect(url_for('auth.reset_password_page'))

    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    hashed_temp_password = generate_password_hash(temp_password)
    user.password = hashed_temp_password
    db.session.commit()

    subject = "密碼重設通知"
    body = f"您的臨時密碼是：{temp_password}\n請在登入後立即更換密碼。"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = email

    try:
        with smtplib.SMTP(SMTP_SERVER) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, email, msg.as_string())
    except Exception as e:
        flash(f"發送郵件失敗：{str(e)}", "error")
        return redirect(url_for('auth.reset_password_page'))
    
    flash("臨時密碼已發送至您的郵箱", "success")
    return redirect(url_for('auth.login'))

"""





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