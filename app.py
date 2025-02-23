# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:07:53 2025

@author: OAP-0001
"""

#整合用主程式

# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 導入各個 Blueprint
from auth import auth_bp
from external_search import external_search_bp
from search_engine import search_bp
from scheduled_scrape import scheduled_scrape_bp
from user_scrape import user_scrape_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# 註冊 Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(external_search_bp)
app.register_blueprint(search_bp)
app.register_blueprint(scheduled_scrape_bp)
app.register_blueprint(user_scrape_bp)

if __name__ == '__main__':
    app.run(debug=True)
