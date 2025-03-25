# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 15:52:56 2025

@author: OAP-0001
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user
from models import db, User, AuthUser, Score  # 假設有 Score 模型用來儲存分數
from database import db


save_score_bp = Blueprint('save_score', __name__, url_prefix="/save_score")

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
    user = current_user.username if current_user.is_authenticated else request.form.get('nickname')

    # 驗證暱稱是否符合要求
    if not user or len(user.strip()) < 2 or not user.isalnum():
        return 'Invalid nickname', 400

    # 未登入用戶加上標註
    if not current_user.is_authenticated:
        user = f"(未登錄) {user}"

    new_score = Score(username=user, score=score)
    db.session.add(new_score)
    db.session.commit()
    
    return redirect(url_for('save_score.leaderboard'))

# 排行榜頁面 - 顯示最高分前 10 名
@save_score_bp.route('/game/leaderboard')
def leaderboard():
    scores = Score.query.order_by(Score.score.desc()).limit(10).all()
    return render_template('leaderboard.html', scores=scores)

# 檢查暱稱是否撞名
@save_score_bp.route('/check_name', methods=['GET'])
def check_name():
    nickname = request.args.get('nickname')
    if not nickname:
        return jsonify({"error": "暱稱為空"}), 400

    # 檢查已登入用戶是否存在相同名稱
    registered_user = Score.query.filter_by(username=nickname).first()
    if registered_user:
        return jsonify({"collision": True, "type": "registered", "message": "該名稱已被註冊用戶使用"})

    # 檢查未登入用戶是否存在相同名稱
    guest_user = Score.query.filter_by(username=f"(未登錄) {nickname}").first()
    if guest_user:
        return jsonify({"collision": True, "type": "guest", "message": "該暱稱已被其他未登入用戶使用，請更改暱稱"})

    return jsonify({"collision": False, "message": "該暱稱可以使用"})



"""
js碼
document.querySelector('#submit-score').addEventListener('click', function () {
    const nickname = document.querySelector('#nickname').value;

    // 檢查用戶是否撞名 (透過 API 返回結果)
    fetch(`/save_score/check_name?nickname=${nickname}`)
        .then(response => response.json())
        .then(data => {
            if (data.collision) {
                if (data.type === 'registered') {
                    // 未登入和已登入用戶撞名：提示登入
                    if (confirm('該名稱已被註冊，是否登入/註冊？')) {
                        window.location.href = '/auth/login';  // 跳轉到登入頁面
                    }
                } else {
                    // 未登入用戶撞名：要求修改名字
                    alert('該暱稱已被其他未登入用戶使用，請更改暱稱');
                }
            } else {
                // 沒有撞名，設置 Cookie 並提交分數
                document.cookie = `nickname=${nickname};path=/`;  // 記住暱稱
                document.querySelector('#score-form').submit();  // 提交表單
            }
        });
});

                
"""