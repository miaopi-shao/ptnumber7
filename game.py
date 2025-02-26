# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 15:52:56 2025

@author: OAP-0001
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import db, Score  # 假設有 Score 模型用來儲存分數

save_score_bp = Blueprint('save_score', __name__)

# 遊戲頁面 - 顯示俄羅斯方塊遊戲頁面
@save_score_bp.route('/game/tetris')
def tetris_game():
    return render_template('tetris_game.html')

# 遊戲頁面 - 顯示跑酷遊戲頁面
@save_score_bp.route('/game/parkour')
def parkour_game():
    return render_template('parkour_game.html')

# 儲存分數
@save_score_bp.route('/save_score', methods=['POST'])
def save_score():
    score = request.form['score']
    # 如果用戶已登入，使用登入的用戶名稱，否則使用提交的暱稱
    user = current_user.username if current_user.is_authenticated else request.form['nickname']
    
    if not user:  # 如果沒有暱稱，返回錯誤訊息
        return 'Nickname is required', 400

    new_score = Score(username=user, score=score)
    db.session.add(new_score)
    db.session.commit()
    
    return redirect(url_for('save_score.leaderboard'))  # 這裡的 `save_score.leaderboard` 是 Blueprint 裡的路由

# 排行榜頁面 - 顯示最高分前 10 名
@save_score_bp.route('/game/leaderboard')
def leaderboard():
    scores = Score.query.order_by(Score.score.desc()).limit(10).all()  # 取得最高分前 10 名
    return render_template('leaderboard.html', scores=scores)
