# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 18:25:06 2025

@author: OAP-0001
"""
# 這裡是與帳號、密碼相關的功能區
# 安裝所需的庫： pip install python-dotenv

# ------------------------------ 創建測試用虛擬資料 ------------------------------
import os  # 1. 用來操作環境變數
# 設定環境變數，這裡是模擬設置，可以在 .env 文件中實際設置
os.environ["JWT_SECRET"] = "test_jwt_secret"  # 2. 設定 JWT 秘密金鑰
os.environ["EMAIL_USER"] = "test@example.com"  # 3. 設定郵件發送帳號
os.environ["EMAIL_PASS"] = "test_password"  # 4. 設定郵件發送密碼
os.environ["SMTP_SERVER"] = "test.smtp.com"  # 5. 設定 SMTP 伺服器
# ------------------------------ 創建測試用虛擬資料 ------------------------------


# --------------------------------- 導入所需模組 --------------------------------

from flask import Blueprint, request, jsonify  # 2. 與 app.py 中的 Flask 應用程式建立藍圖及處理請求
from werkzeug.security import generate_password_hash, check_password_hash  # 3. 與 app.py 密碼加密/驗證
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager  # 4. 與 app.py JWT 驗證
from models import db, User  # 5. 與 models.py 資料庫及 User 模型聯繫
import hashlib  # 6. 用於密碼加密雜湊
import random  # 7. 用於生成臨時密碼
import string  # 8. 用於生成臨時密碼的字元
import smtplib  # 9. 用於發送電子郵件
from dotenv import load_dotenv  # 10. 用來載入環境變數（如 JWT_SECRET 等）
from email.mime.text import MIMEText  # 11. 用來構建電子郵件的正文

# --------------------------------- 導入所需模組 --------------------------------




# 載入環境變數
load_dotenv()  # 12. 從 .env 檔案載入環境變數（這部分是與 app.py 聯繫）

# 設定環境變數
SECRET_KEY = os.getenv("JWT_SECRET")  # 13. 設定 JWT 秘密金鑰（這部分是與 app.py 聯繫）
EMAIL_USER = os.getenv("EMAIL_USER")  # 14. 設定郵件發送帳號（這部分是與 app.py 聯繫）
EMAIL_PASS = os.getenv("EMAIL_PASS")  # 15. 設定郵件發送密碼（這部分是與 app.py 聯繫）
SMTP_SERVER = os.getenv("SMTP_SERVER")  # 16. 設定 SMTP 伺服器（這部分是與 app.py 聯繫）

# 建立 Blueprint，讓 `auth` API 具有獨立的路由（這部分是與 app.py 聯繫）
auth_bp = Blueprint('auth', __name__)  # 17. 初始化 auth 藍圖


# ------------------------------- 工具函式 -------------------------------------

def phrase_to_password(phrase):
    """ 將習慣用語轉換為加密密碼（至少 8 個字） """
    if len(phrase) < 8:
        return None, "習慣用語長度至少 8 個字"  # 18. 驗證密碼長度，與前端驗證聯繫（在註冊時會收到此訊息）
    if len(phrase) > 16:
        return None, "習慣用語長度最多 16 個字"  # 18. 驗證密碼長度，與前端驗證聯繫（在註冊時會收到此訊息）
    
    hashed_password = generate_password_hash(phrase, method='pbkdf2:sha256')  # 19. 密碼加密，與後端資料庫（models.py）資料儲存聯繫
    return hashed_password, None  # 20. 返回加密後的密碼（與後端資料庫聯繫）

def encode_morse(text):
    """ 將文字轉換為摩斯密碼，並回傳加密的 SHA-256 雜湊 """
    morse_code_dict = {  # 21. 摩斯密碼字典
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
        'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
        '3': '...--', '4': '....-', '5': '.....', '6': '-....',
        '7': '--...', '8': '---..', '9': '----.'
    }
    text = text.upper()  # 22. 將文字轉為大寫（這部分會與前端處理的字串格式聯繫）
    morse_code = ' '.join(morse_code_dict[char] for char in text if char in morse_code_dict)  # 23. 轉換為摩斯密碼
    hashed_morse = hashlib.sha256(morse_code.encode()).hexdigest()  # 24. SHA-256 雜湊
    return hashed_morse  # 25. 返回摩斯密碼的雜湊值（這部分與資料庫的儲存及驗證聯繫）

# ------------------------------- 工具函式 -------------------------------------




# -------------------------------- 登入 API ------------------------------------

@auth_bp.route('/login', methods=['POST'])  # 26. 登入路由，POST 請求（這是與前端互動，從 `index.html` 來傳送資料）
def login():
    """ 使用者登入，成功則返回 JWT Token """
    data = request.json  # 27. 取得請求中的 JSON 資料（前端與後端 JSON 資料交換）
    username = data.get('username')  # 28. 取得使用者名稱（來自前端 `index.html`）
    phrase = data.get('phrase')  # 29. 取得使用者密碼（來自前端 `index.html`）

    if not username or not phrase:
        return jsonify({"error": "請提供使用者名稱和密碼"}), 400  # 30. 若無資料，回傳錯誤訊息（返回前端顯示錯誤）

    # 用 SHA-256 方式加密帳號（因為我們註冊時是用 encode_morse）
    hashed_username = encode_morse(username)  # 31. 進行帳號加密（與資料庫中的帳號欄位聯繫）
    user = User.query.filter_by(username=hashed_username).first()  # 32. 查詢資料庫（與 `models.py` 中的 `User` 模型聯繫）

    if not user or not check_password_hash(user.password, phrase):  # 33. 檢查密碼是否正確（與資料庫儲存的密碼聯繫）
        return jsonify({"error": "帳號或密碼錯誤"}), 401  # 34. 帳號或密碼錯誤回應（返回給前端）

    # 產生 JWT Token，預設 1 小時過期
    access_token = create_access_token(identity=user.id)  # 35. 生成 JWT Token（與後端會話及驗證聯繫）

    return jsonify({"message": "登入成功", "token": access_token})  # 36. 返回成功訊息和 Token（傳遞給前端）

# -------------------------------- 登入 API ------------------------------------






# ------------------------------ 取得個人資訊 API ------------------------------

@auth_bp.route('/profile', methods=['GET'])  # 37. 取得個人資訊的路由
@jwt_required()  # 38. 需要 JWT Token 驗證（這部分會由前端傳送 Token）
def profile():
    """ 取得登入使用者的資訊（需要提供 JWT Token） """
    user_id = get_jwt_identity()  # 39. 從 JWT Token 中取得使用者 ID
    user = User.query.get(user_id)  # 40. 查詢資料庫中的使用者資料（與 `models.py` 中的 `User` 模型聯繫）
    if not user:
        return jsonify({"error": "用戶不存在"}), 404  # 41. 用戶不存在錯誤處理

    return jsonify({
        "username": user.username,  # 42. 返回使用者資料（這些資料會顯示在前端）
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at
    })

# ------------------------------ 取得個人資訊 API ------------------------------










# ---------------------------------- 註冊 API ----------------------------------
@auth_bp.route('/register', methods=['POST'])  # 43. 註冊路由，POST 請求（這部分是與前端表單互動）
def register():
    """ 使用者註冊功能，帳號經摩斯密碼加密，密碼經 PBKDF2 加密 """
    data = request.json  # 44. 取得前端傳來的 JSON 資料（來自 `index.html` 的表單）
    username = data.get('username')  # 45. 取得使用者名稱（來自前端）
    phrase = data.get('phrase')  # 46. 取得使用者密碼（來自前端）
    email = data.get('email')  # 47. 取得使用者電子郵件（來自前端）

    if not username or not phrase or not email:
        return jsonify({"error": "請提供完整的使用者名稱、密碼和電子郵件"}), 400  # 48. 檢查資料是否完整（錯誤回傳給前端）

    hashed_username = encode_morse(username)  # 49. 進行帳號加密
    hashed_password, error = phrase_to_password(phrase)  # 50. 密碼加密（與 `models.py` 的 `User` 模型資料結合）

    if error:
        return jsonify({"error": error}), 400  # 51. 如果密碼加密失敗，返回錯誤（回傳給前端）

    # 將使用者資料存入資料庫
    user = User(username=hashed_username, password=hashed_password, email=email)  # 52. 創建 `User` 實例（與 `models.py` 的 `User` 類別聯繫）
    db.session.add(user)  # 53. 儲存資料到資料庫（這部分與 `models.py` 中的 `db` 聯繫）
    db.session.commit()  # 54. 提交資料庫變更

    return jsonify({"message": "註冊成功"}), 201  # 55. 註冊成功回應（傳遞給前端）

# ---------------------------------- 註冊 API ----------------------------------






# --------------------------------- 密碼重設 API -------------------------------
@auth_bp.route('/reset-password', methods=['POST'])  # 56. 密碼重設路由
def reset_password():
    """ 密碼重設功能，向使用者電子郵件發送臨時密碼 """
    data = request.json  # 57. 取得 JSON 資料（來自前端）
    email = data.get('email')  # 58. 取得電子郵件

    if not email:
        return jsonify({"error": "請提供電子郵件"}), 400  # 59. 若無郵件，返回錯誤訊息

    user = User.query.filter_by(email=email).first()  # 60. 查詢資料庫（與 `models.py` 中的 `User` 模型聯繫）
    if not user:
        return jsonify({"error": "用戶不存在"}), 404  # 61. 若使用者不存在，返回錯誤

    # 隨機產生臨時密碼
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # 62. 隨機產生臨時密碼
    hashed_temp_password = generate_password_hash(temp_password)  # 63. 密碼雜湊處理

    user.password = hashed_temp_password  # 64. 更新密碼
    db.session.commit()  # 65. 提交資料庫變更

    # 發送郵件
    subject = "密碼重設通知"  # 66. 郵件主題
    body = f"您的臨時密碼是：{temp_password}\n請在登入後立即更換密碼。"  # 67. 郵件內容

    msg = MIMEText(body)  # 68. 生成郵件內容
    msg['Subject'] = subject  # 69. 設定郵件主題
    msg['From'] = EMAIL_USER  # 70. 設定發件人
    msg['To'] = email  # 71. 設定收件人

    try:
        with smtplib.SMTP(SMTP_SERVER) as server:  # 72. 發送郵件
            server.login(EMAIL_USER, EMAIL_PASS)  # 73. 登入 SMTP 伺服器
            server.sendmail(EMAIL_USER, email, msg.as_string())  # 74. 發送郵件
    except Exception as e:
        return jsonify({"error": f"發送郵件失敗：{str(e)}"}), 500  # 75. 若發送郵件失敗，返回錯誤訊息

    return jsonify({"message": "臨時密碼已發送至您的郵箱"}), 200  # 76. 返回成功訊息

# --------------------------------- 密碼重設 API -------------------------------


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