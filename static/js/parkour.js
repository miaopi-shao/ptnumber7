document.addEventListener("DOMContentLoaded", function () {
    // =============================== 1. 開始載入模組及機制 ===============================
    // 取得 canvas 元素及其 2D 畫布上下文
    let canvas = document.getElementById('parkourCanvas');
    if (!canvas) {
        console.error("找不到 id 為 'parkourCanvas' 的 canvas 元素！");
        return;
    }
    let ctx = canvas.getContext('2d');

    // 遊戲畫面與參數
    let gameWidth = canvas.width;      // 遊戲畫面寬度
    let gameHeight = canvas.height;    // 遊戲畫面高度
    let gravity = 0.6;                 // 重力加速度，角色下墜速度影響因素
    let baseJumpStrength = 12;         // 跳躍力量，角色每次跳躍的最低跳躍力量
    let maxJumpStrength = 20;          // 跳躍力量，角色每次跳躍的最大跳躍力量
    let isJumping = false;             // 是否正在跳躍
    let jumpPressed = false;           // 是否正在按住跳躍鍵
    let jumpDuration = 0;              // 記錄按住空白鍵的持續時間
    let isGameOver = false;            // 是否遊戲結束
    let score = 0;                     // 玩家當前分數

    // 載入圖片資源
    let characterImage = new Image();
    characterImage.src = "/static/images/game_man.png"; // 替換為角色圖片的路徑
    let obstacleImage = new Image();
    obstacleImage.src = "/static/images/game_lag.png";   // 替換為障礙物圖片的路徑
    let backgroundImage = new Image();
    backgroundImage.src = "/static/images/game_back.png"; // 替換為背景圖片的路徑

    // 障礙物與角色設定
    let obstacles = [];                     // 障礙物陣列，用於存儲場景中所有障礙物
    let obstacleSpeed = 3;                  // 固定障礙物移動速度
    let maxObstacleHeight = gameHeight / 2; // 障礙物最高高度

    let character = {
        x: 50,                      // 角色的初始橫向位置
        y: gameHeight - 100,        // 角色的初始縱向位置（貼近地面）
        width: 50,                  // 角色的寬度
        height: 50,                 // 角色的高度
        velocityY: 0                // 角色的垂直速度
    };

    // =============================== 2. 確定按鍵邏輯 ===============================
    // 處理跳躍邏輯
    document.addEventListener('keydown', function (event) {
        if (event.code === 'Space' && !isJumping && !isGameOver) {
            isJumping = true;                     // 設置跳躍狀態
            jumpDuration = 0;                     // 初始化持續時間
        }
    });
    
    // 當空白鍵釋放時，設定跳躍力量
    document.addEventListener('keyup', function (event) {
        if (event.code === 'Space' && jumpPressed && !isGameOver) {
            jumpPressed = false; // 標記按鍵釋放
            let jumpStrength = baseJumpStrength + (jumpDuration / 100); // 根據持續時間計算力量
            if (jumpStrength > maxJumpStrength) jumpStrength = maxJumpStrength; // 限制跳躍力量
            character.velocityY = -jumpStrength; // 設定角色跳躍速度
            isJumping = true; // 角色處於跳躍狀態
        }
    });

    // =============================== 3. 遊戲運行狀態 ===============================
    function gameLoop() {
        if (isGameOver) {
            return showGameOver(); // 若遊戲結束，顯示結束畫面
        }}

        // 計算跳躍持續時間
        if (jumpPressed) {
            jumpDuration += 16; // 每幀大約為 16 毫秒
        
        // 清除畫布
        ctx.clearRect(0, 0, gameWidth, gameHeight);

        // 繪製背景
        ctx.drawImage(backgroundImage, 0, 0, gameWidth, gameHeight);

        // 繪製角色
        ctx.drawImage(characterImage, character.x, character.y, character.width, character.height);

        // 更新角色位置
        character.velocityY += gravity;    // 施加重力影響
        character.y += character.velocityY; // 更新角色垂直位置

        // 地面碰撞檢測
        if (character.y >= gameHeight - 100) {
            character.y = gameHeight - 100;  // 修正角色位置貼近地面
            character.velocityY = 0;         // 重置垂直速度
            isJumping = false;               // 角色結束跳躍狀態
        }

        // 生成障礙物
        if (Math.random() < 0.009) { // 調低生成頻率為 0.9%
            let obstacleHeight = Math.random() * (maxObstacleHeight) + 20; // 調整高度範圍
            obstacles.push({
                x: gameWidth,                 // 障礙物生成於畫面最右端
                y: gameHeight - obstacleHeight, // 障礙物垂直位置
                width: 30,                   // 障礙物寬度
                height: obstacleHeight        // 障礙物高度
            });
        }

        // 更新並繪製障礙物
        for (let i = 0; i < obstacles.length; i++) {
            let obstacle = obstacles[i];
            obstacle.x -= obstacleSpeed; // 障礙物向左移動

            // 如果障礙物超出畫面，移除並增加分數
            if (obstacle.x + obstacle.width < 0) {
                obstacles.splice(i, 1); // 移除障礙物
                i--;                   // 調整索引
                score++;               // 增加分數
            }

            // 碰撞檢測（判斷角色是否撞到障礙物）
            if (
                character.x < obstacle.x + obstacle.width &&
                character.x + character.width > obstacle.x &&
                character.y < obstacle.y + obstacle.height &&
                character.y + character.height > obstacle.y
            ) {
                isGameOver = true; // 若發生碰撞，設定遊戲結束
            }

            // 繪製障礙物
            ctx.drawImage(obstacleImage, obstacle.x, obstacle.y, obstacle.width, obstacle.height);
        }

        // 顯示當前分數
        ctx.font = "20px Arial";
        ctx.fillStyle = "black";
        ctx.fillText("Score: " + score, 20, 30);

        // 持續請求下一幀
        requestAnimationFrame(gameLoop);
    }

    // =============================== 4. 遊戲結束並記錄分數 ===============================
    function showGameOver() {
        ctx.clearRect(0, 0, gameWidth, gameHeight); // 清除畫布
        ctx.fillStyle = "black";
        ctx.font = "40px Arial";
        ctx.fillText("Game Over!", gameWidth / 2 - 100, gameHeight / 2); // 顯示遊戲結束文字
        ctx.font = "20px Arial";
        ctx.fillText("Final Score: " + score, gameWidth / 2 - 50, gameHeight / 2 + 40); // 顯示最終分數
    }

    // 定義全域的 startGame 函數，供按鈕觸發使用
    window.startGame = function () {
        // 重置遊戲狀態
        isGameOver = false;
        score = 0;
        character.x = 50;
        character.y = gameHeight - 100;
        character.velocityY = 0;
        obstacles = [];

        // 開始遊戲主循環
        gameLoop();
    };

    // 自動開始遊戲（若不需要自動啟動，可移除此行）
    startGame();
});
