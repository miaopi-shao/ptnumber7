# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 18:25:06 2025

@author: OAP-0001
"""
# 這裡是與帳號、密碼相關的功能區
# 安裝所需的庫： pip install python-dotenv

# --------------------------------- 導入所需模組 ---------------------------------
import os 
from flask import make_response, Blueprint, request, jsonify, current_app  # Flask 藍圖與 API 回應處理
from werkzeug.security import generate_password_hash, check_password_hash  # 密碼加密與驗證
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity  # JWT 驗證
from database import db, jwt, mail
from models import AuthUser # 與資料庫和使用者模型互動
import hashlib  # 密碼雜湊處理
import random  # 隨機生成臨時密碼
import string  # 使用字母與數字生成密碼
import smtplib  # 發送電子郵件
import re
from dotenv import load_dotenv  # 環境變數加載
from email.mime.text import MIMEText  # 電子郵件內容格式化
import logging    # 添加日誌記錄功能
import traceback  # 用於追蹤錯誤堆疊
from flask_mail import Mail, Message #Flask 應用集成的郵件發送解決方案
from flask_login import login_user, current_user
import json

# 設置日誌級別和輸出格式
logging.basicConfig(
    level=logging.DEBUG,  # 日誌級別最低為 DEBUG，包含 WARNING 和 ERROR
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # 將日誌輸出到命令行（標準輸出）
)

# 測試日誌輸出
logging.info("auth的日誌初始化完成！")
logging.warning("這是一條來在auth.py測試的 WARNING 日誌！")

# from app import app

# # 配置 Flask-Mail 的參數-注意!!!正式上線的服務不能直接使用.evn的數據，會影響保密程度
# app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')          # SMTP 伺服器
# app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))    # SMTP 埠，默認 587
# app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'  # 是否啟用 TLS
# app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true' # 是否啟用 SSL
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')      # 發送郵件的帳號
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')      # 發送郵件的密碼
# app.config['MAIL_DEFAULT_SENDER'] = os.getenv('oaplookout@gmail.com')  # 預設的寄件人


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
def password_to_password(password):
    """ 將使用者輸入的密碼進行加密 """
    if len(password) < 8 or len(password) > 16:
        return None, "密碼長度必須在 8 至 16 個字元之間"
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
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
    
    morse_code = ''.join(
        morse_code_dict[char] if char in morse_code_dict else char for char in text
    )
    hashed_morse = hashlib.sha256(morse_code.encode()).hexdigest()
    return hashed_morse



# ----------------------------- 登入功能 -----------------------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    """ 使用者登入並返回 JWT Token """
    try:
        if not request.is_json:
            return jsonify({"error": "請求必須是 JSON 格式"}), 400
        try:    
            data = request.json
            logging.info(f"收到的 JSON 資料: {data}")
        except Exception as e:
            logging.error(f"JSON 解析失敗: {e}")
            return jsonify({"error": "無法解析請求的 JSON"}), 400
        
        username = data.get('username')
        logging.info(f"收到的 JSON 資料: {username}")

        password = data.get('password')
        logging.info(f"收到的 JSON 資料: {password}")
        
    
        if not username or not password:
            return jsonify({"error": "請提供使用者名稱和密碼"}), 400
    
        hashed_username = encode_morse(username)
        logging.info(f"收到的 JSON 資料: {hashed_username}")
        
        # 驗證用戶是否存在
        user = AuthUser.query.filter_by(username=hashed_username).first()
        logging.info(f"正在查詢使用者: {hashed_username}")
        logging.info(f"正在查詢使用者: {user}")
    
        if not user:
            logging.warning(f"使用者未找到: {hashed_username}")
            return jsonify({"error": "未找到該使用者"}), 404
    
        if not check_password_hash(user.password, password):
            logging.warning(f"密碼錯誤: 使用者 {hashed_username}")
            return jsonify({"error": "密碼錯誤"}), 401
    
        access_token = create_access_token(identity=str(user.user_id))
        logging.info(f"生成的 Token: {access_token}")
        login_user(user)  # 設置 Flask-Login 的登入狀態
        logging.info(f"使用者 {username} 成功登入")
        logging.info(f"返回的 JSON: {jsonify({'message': '登入成功', 'token': access_token, 'username': user.username})}")
        return make_response(json.dumps({
            "message": "登入成功",
            "token": access_token,
            "username": user.username
        }, ensure_ascii=False), 200)

    
    except Exception as e:
        logging.error(f"登入的錯誤: {e}")
        return jsonify({"error": "伺服器錯誤"}), 500

    
        access_token = create_access_token(identity=user.id)  # 創建 JWT Token
        logging.info(f"使用者 {username} 成功登入")
        return jsonify({"message": "登入成功", "token": access_token}), 200
    
    except Exception as e:
        logging.error(f"登入時發生錯誤: {e}")  # 增加錯誤日誌
        return jsonify({"error": "伺服器內部錯誤，請稍後再試"}), 50    


# ------------------------------ 取得個人資訊 API ------------------------------

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()  # 驗證用戶是否提供有效的 JWT Token
def profile():
    """ 取得登入使用者的資訊 """
    if current_user.is_authenticated:
        print(f"Session 驗證成功，用戶 ID: {current_user.get_id()}")
        user = AuthUser.query.get(current_user.get_id())
        if user:
            return jsonify({
                "username": user.username,
                "email": user.email,
                "role": user.role
            }), 200
        else:
            print("Session 驗證失敗！")
            try:
                raw_token = request.headers.get("Authorization")
                print(f"接收到的 Authorization 標頭: {raw_token}")
                logging.info(f"接收到的 Authorization 標頭: {raw_token}")
                 
                user_id = get_jwt_identity()  # 從 JWT Token 中解析出用戶 ID
                logging.info(f"解析出的用戶 ID: {user_id}")
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
            except Exception as e:
                logging.error(f"獲取個人資訊時發生錯誤: {e}")  # 記錄詳細錯誤資訊
                return jsonify({"error": "伺服器內部錯誤，請稍後再試"}), 500
          
    
# ----------------------------- 註冊功能 -----------------------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    """ 使用者註冊並存入資料庫 """
    try:
        # 進行用戶註冊邏輯
        logging.info("開始執行註冊流程")

        try:
            data = request.get_json(force=True)
            logging.info(f"收到的 JSON 資料: {data}")
            if not data:
                logging.error("接收資料為空")
                return jsonify({"error": "請提供資料"}), 400
        
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
        
            if not username or not password or not email:
                logging.error("接收資料不完整")
                return jsonify({"error": "請填寫完整資訊"}), 400
        except Exception as e:
            logging.error(f"JSON 解析失敗: {e}")
            return jsonify({"error": "請傳遞有效的 JSON 資料"}), 400
        
        username = data.get('username')
        logging.info(f"收到的 帳號 資料: {username}")
        
        password = data.get('password')
        logging.info(f"收到的 密碼 資料: {password}")
        
        email = data.get('email')
        logging.info(f"收到的 信箱 資料: {email}")
    
        if not username or not password or not email:
            return jsonify({"error": "請提供完整資訊"}), 400
    
        if AuthUser.query.filter_by(email=email).first():
            return jsonify({"error": "該電子郵件已被註冊"}), 400
    
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{8,16}$', password):
            return jsonify({"error": "密碼長度須在 8 至 16 且需包含數字和字母"}), 400
    
    
        hashed_username = encode_morse(username)
        hashed_password, error = password_to_password(password)
        if error:
            return jsonify({"error": error}), 400
    
        user = AuthUser(username=hashed_username, password=hashed_password, email=email)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"資料庫錯誤：{e}")  # 記錄到伺服器日誌中
            return jsonify({"error": "資料庫操作失敗"}), 500
        if not data:
            logging.error("收到的資料為空")
            return jsonify({"error": "請提供資料"}), 400

        
        try:
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                return jsonify({"error": "無效的電子郵件格式"}), 400
            
            # 發送註冊成功郵件
            from app import mail
            msg = Message(
                subject="註冊成功通知",
                sender="oaplookout@gmail.com",
                recipients=[email],
                body="恭喜您成功註冊！請使用您的帳號登入。"
            )
            mail.send(msg)
            print("郵件已成功發送！")
        except Exception as e:
            logging.error(f"郵件發送失敗，錯誤訊息: {e}")
            print(f"郵件發送失敗: {e}")
            return jsonify({"error": "郵件發送失敗"}), 500
        
            # 最後才返回成功訊息
        return jsonify({"message": "註冊成功"}), 201
    except Exception as e:
        logging.error(f"註冊發生錯誤: {e}")
        return jsonify({"error": "伺服器錯誤"}), 500


        


# ----------------------------- 密碼重設功能 -------------------------------------
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """ 密碼重設功能，向電子郵件發送臨時密碼 """
    try:
        # 獲取 JSON 數據
        data = request.json
        email = data.get('email')

        if not email:
            logging.error("未提供電子郵件")
            return jsonify({"error": "請提供電子郵件"}), 400

        # 查找用戶
        user = AuthUser.query.filter_by(email=email).first()
        if not user:
            logging.error(f"無法找到該電子郵件對應的用戶: {email}")
            return jsonify({"error": "該電子郵件不存在"}), 404

        # 生成臨時密碼
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        logging.info(f"為用戶 {email} 生成臨時密碼")

        # 雜湊臨時密碼並更新用戶
        hashed_temp_password = generate_password_hash(temp_password)
        user.password = hashed_temp_password
        db.session.commit()
        logging.info(f"已更新用戶 {email} 的密碼")

        # 發送郵件通知
        try:
            msg = Message(
                subject="密碼重設通知",
                sender="your-email@example.com",  # 或 app.config['MAIL_DEFAULT_SENDER']
                recipients=[email],
                body=f"您的臨時密碼是：{temp_password}"
            )
            logging.info(f"開始向用戶 {email} 發送臨時密碼郵件")
            mail.send(msg)
            logging.info(f"成功向用戶 {email} 發送臨時密碼郵件")
        except Exception as email_error:
            logging.error(f"發送郵件時失敗: {email_error}")
            return jsonify({"error": f"郵件發送失敗：{str(email_error)}"}), 500

        return jsonify({"message": "臨時密碼已發送"}), 200

    except Exception as e:
        logging.error(f"密碼重設流程中出現錯誤: {e}")
        return jsonify({"error": f"伺服器錯誤：{str(e)}"}), 500


# --------------------------------- 帳戶刪除 API -------------------------------

@auth_bp.route('/delete_account', methods=['POST'])  # 定義路由與 HTTP 方法
@jwt_required()  # 僅要求用戶攜帶有效的 JWT Token
def delete_account():
    try:
    
        # 從 Token 中取得當前用戶 ID
        user_id = get_jwt_identity()
        logging.info(f"正在刪除帳戶：{user_id}")
        user = AuthUser.query.get(user_id)
        
        if not user:
            logging.error(f"刪除失敗：找不到用戶 ID {user_id}")
            return jsonify({"error": "找不到使用者"}), 404
    
        # 刪除用戶之前檢查，驗證用戶的密碼（從請求中取得）
        password = request.json.get("password")
        logging.info(f"用戶驗證密碼：{password}")
        
        if not check_password_hash(user.password, password):
            return jsonify({"error": "密碼驗證失敗"}), 401
        
        related_data = AuthUser.query.filter_by(user_id=user_id).all()
        if related_data:
            logging.error(f"刪除失敗：用戶 {user_id} 有相關數據未完成")
            return jsonify({"error": "該用戶有未完成的相關數據，無法刪除"}), 400

    
        # 刪除用戶並提交變更
        db.session.delete(user)
        db.session.commit()
        logging.info(f"帳戶ID {user_id}確認完畢，已成功刪除用戶 ")
        return jsonify({"message": "帳號已成功刪除"}), 200
    except Exception as e:
        logging.error(f"刪除帳戶過程中出現錯誤: {e}")
        return jsonify({"error": "伺服器錯誤"}), 500



# --------------------------------- 郵件測試 -------------------------------

@auth_bp.route('/test-email', methods=['GET', 'POST'])
def test_email():
    from app import mail  # 延遲導入，避免循環引用
    try:
        print("try")
        with current_app.app_context():
            print("寄信開始")
            msg = Message(
                subject="聯成學員-妙齊測試郵件",
                sender=os.getenv('MAIL_DEFAULT_SENDER'),  # 明確指定寄件人
                # sender=current_app.config['oaplookout@gmail.com'],
                
                recipients=["aaappphh174805@gmail.com"],  # 替換為測試用的收件人
                body="老師您好，這是一封測試郵件，用於確認 Flask-Mail 功能是否正常運作。"
            )
            mail.send(msg)
        return jsonify({"message": "郵件已成功發送！"}), 200
    except Exception as e:
        return jsonify({"error": f"郵件發送失敗: {str(e)}"}), 500

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