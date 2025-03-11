# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:01:04 2025

@author: OAP-0001
"""

# external_search.py 處理站外搜尋
from flask import Blueprint, request, redirect

external_search_bp = Blueprint('external_search', __name__)

@external_search_bp.route('/external_search', methods=['GET'])
def external_search():
    query = request.args.get('query')
    if query:
        return redirect(f"https://duckduckgo.com/?q={query}")
    return redirect('/')
