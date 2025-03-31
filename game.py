# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 15:52:56 2025

@author: OAP-0001
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user
from models import User, AuthUser, Score  # 假設有 Score 模型用來儲存分數
from database import db


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
@save_score_bp.route('/game/save_score', methods=['POST'])
def save_score():
    # 從表單中獲取分數
    score = request.form.get('score', type=int)
    if not score or score < 0:  # 驗證分數
        return 'Invalid score', 400

    game_name = request.form.get('game_name') or "Tetris"  # 默認遊戲名稱

    user_id = None
    guest_nickname = None
    
    if current_user.is_authenticated:  # 如果用戶已登入
        user_id = current_user.id
    else:  # 未登入用戶
        nickname = request.form.get('nickname')  # 從表單中獲取暱稱
        if not nickname or len(nickname.strip()) < 2 or not nickname.isalnum():
            return 'Invalid nickname', 400  # 驗證暱稱
        guest_nickname = nickname.strip()
    
    # 創建新的分數記錄
    new_score = Score(
        user_id=user_id,
        guest_nickname=guest_nickname,
        game_name= game_name,
        score=score
    )
    
    # 儲存到資料庫
    db.session.add(new_score)
    db.session.commit()

    return redirect(url_for('save_score.leaderboard'))

# 排行榜頁面 - 顯示最高分前 10 名
@save_score_bp.route('/game/leaderboard')
def leaderboard():
    scores = Score.query.order_by(Score.score.desc()).limit(10).all()
    leaderboard_data = []

    for score in scores:
        if score.user_id:  # 登入用戶
            user = User.query.get(score.user_id)
            username = user.username if user else "未知用戶"
        else:  # 未登入用戶
            username = f"(未登入) {score.guest_nickname}"

        leaderboard_data.append({
            "username": username,
            "game_name": score.game_name,
            "score": score.score,
            "created_at": score.created_at
        })
    
    return render_template('leaderboard.html', scores=leaderboard_data)

# 檢查暱稱是否撞名
@save_score_bp.route('/game/check_name', methods=['GET'])
def check_name():
    nickname = request.args.get('nickname')
    if not nickname:
        return jsonify({"error": "暱稱為空"}), 400

   # 檢查已登入用戶是否存在相同名稱
    registered_user = User.query.filter_by(username=nickname).first()  # 查 User 模型
    if registered_user:
        return jsonify({"collision": True, "type": "registered", "message": "該名稱已被註冊用戶使用"})
    
    # 檢查未登入用戶是否存在相同名稱
    guest_user = Score.query.filter_by(guest_nickname=nickname).first()  # 查 Score 中的 guest_nickname
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