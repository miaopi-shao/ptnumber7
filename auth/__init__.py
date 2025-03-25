# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 15:47:15 2025

@author: OAP-0001
"""

# auth資料夾套件化-帳號密碼區
try:
    from .auth import auth_bp
except ImportError as e:
    print(f"Error importing auth_bp: {e}")

# ...後續再導入其他模組的代碼

# 將所有藍圖組合成一個列表，方便在 app.py 中一次性註冊
all_auth_blueprints = [
    auth_bp,
    # ...可以繼續加入其他藍圖
]