# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:02:11 2025

@author: OAP-0001
"""

# search_engine.py 負責處理站內搜尋邏輯。

from flask import Blueprint, request, render_template, redirect


search_bp = Blueprint('search', __name__)

@search_bp.route('/internal_search', methods=['GET'])
def internal_search():
    
    from search_engine import search_internal  # 確保這個函式已經實作
    query = request.args.get('query')
    
    if query:
        results = search_internal(query)  # 內部搜尋邏輯
        return render_template('search_results.html', query=query, results=results)
    return redirect('/')
