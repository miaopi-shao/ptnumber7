document.addEventListener("DOMContentLoaded", function () {
    // ========================== 跑酷小遊戲 ==========================
    
    let canvas = document.getElementById('parkourCanvas');
    canvas.width = 1200;
    canvas.height = 800;
    if (!canvas) {
        console.error("❌ 找不到 id 為 'parkourCanvas' 的 canvas 元素！");
        return;
    }
    let ctx = canvas.getContext('2d');

    // 遊戲畫布相關參數
    let gameWidth = canvas.width;  // 遊戲畫面寬度
    let gameHeight = canvas.height; // 遊戲畫面高度

    // 物理相關參數
    let gravity = 0.6;             // 重力影響
    let baseJumpStrength = 20;      // 角色最低跳躍力量
    let maxJumpStrength = 35;       // 角色最大跳躍力量
    let isJumping = false;          // 是否正在跳躍
    let jumpPressed = false;        // 是否正在按住跳躍鍵
    let jumpDuration = 0;           // 記錄按住跳躍鍵的時間
    let isGameOver = false;         // 是否遊戲結束
    let score = 0;                  // 玩家當前得分

    // ========================== 2️⃣ 加載圖片資源 ==========================

    let characterImage = new Image();
    characterImage.src = "/static/images/game_man.png";  // 角色圖片

    let obstacleImage = new Image();
    obstacleImage.src = "/static/images/game_lag.png";   // 障礙物圖片

    let backgroundImage = new Image();
    backgroundImage.src = "/static/images/game_back.png"; // 背景圖片

    // ========================== 3️⃣ 角色與障礙物參數 ==========================

    let obstacles = [];                 // 障礙物列表
    let obstacleSpeed = 3;              // 障礙物移動速度
    let maxObstacleHeight = gameHeight / 5; // 障礙物最大高度

    let character = {
        x: 50,                          // 角色初始位置（X軸）
        y: gameHeight - 100,            // 角色初始位置（Y軸）
        width: 50,                      // 角色寬度
        height: 50,                     // 角色高度
        velocityY: 0                    // 角色垂直速度
    };

    // ========================== 4️⃣ 監聽鍵盤事件 ==========================

    document.addEventListener('keydown', function (event) {
        // 如果按下空白鍵（跳躍）
        if (event.code === 'Space' && !isJumping && !isGameOver) {
            isJumping = true;
            jumpPressed = true;
            jumpDuration = 0;
        }

        // 按下 Enter 鍵可以重新開始遊戲
        if (event.code === 'Enter' && isGameOver) {
            startGame();
        }
    });

    document.addEventListener('keyup', function (event) {
        // 當釋放空白鍵時，計算跳躍高度
        if (event.code === 'Space' && jumpPressed && !isGameOver) {
            jumpPressed = false;
            let jumpStrength = Math.min(baseJumpStrength + (jumpDuration / 60), maxJumpStrength);
            character.velocityY = -jumpStrength;
            isJumping = true;
        }
    });

    // ========================== 5️⃣ 遊戲迴圈 ==========================

    function gameLoop() {
        if (isGameOver) {
            showGameOver(); // 如果遊戲結束，顯示結束畫面
            return;
        }

        // 計算跳躍持續時間
        if (jumpPressed) {
            jumpDuration += 16; // 每一幀約 16 毫秒
        }

        // 清除畫布
        ctx.clearRect(0, 0, gameWidth, gameHeight);

        // 繪製背景
        ctx.drawImage(backgroundImage, 0, 0, gameWidth, gameHeight);

        // 繪製角色
        ctx.drawImage(characterImage, character.x, character.y, character.width, character.height);

        // 更新角色位置
        character.velocityY += gravity;  // 施加重力
        character.y += character.velocityY;  // 更新角色 Y 軸位置

        // 限制角色不能掉出地面
        if (character.y >= gameHeight - 100) {
            character.y = gameHeight - 100;
            character.velocityY = 0;
            isJumping = false;
        }

        // 生成障礙物（隨機）
        if (Math.random() < 0.009) { // 調整障礙物生成頻率（0.9%）
            let obstacleHeight = Math.random() * (maxObstacleHeight) + 20;
            obstacles.push({
                x: gameWidth,                 // 生成於畫面最右端
                y: gameHeight - obstacleHeight, // 設定障礙物高度
                width: 30,                   // 障礙物寬度
                height: obstacleHeight        // 障礙物高度
            });
        }

        // 更新障礙物位置並檢測碰撞
        obstacles = obstacles.filter(obstacle => {
            obstacle.x -= obstacleSpeed; // 障礙物向左移動
            if (obstacle.x + obstacle.width < 0) {
                score++; // 增加分數
                return false; // 移除離開畫面的障礙物
            }
            return true;
        });

        for (let obstacle of obstacles) {
            // 碰撞偵測
            if (
                character.x < obstacle.x + obstacle.width &&
                character.x + character.width > obstacle.x &&
                character.y < obstacle.y + obstacle.height &&
                character.y + character.height > obstacle.y
            ) {
                isGameOver = true; // 碰撞發生，遊戲結束
            }
            ctx.drawImage(obstacleImage, obstacle.x, obstacle.y, obstacle.width, obstacle.height);
        }

        // 顯示當前得分
        ctx.font = "20px Arial";
        ctx.fillStyle = "black";
        ctx.fillText("Score: " + score, 20, 30);

        // 遞迴執行下一幀
        requestAnimationFrame(gameLoop);
    }

    // ========================== 6️⃣ 遊戲結束 ==========================

    function showGameOver() {
        ctx.clearRect(0, 0, gameWidth, gameHeight);
        ctx.fillStyle = "black";
        ctx.font = "40px Arial";
        ctx.fillText("Game Over!", gameWidth / 2 - 100, gameHeight / 2);
        ctx.font = "20px Arial";
        ctx.fillText("Final Score: " + score, gameWidth / 2 - 50, gameHeight / 2 + 40);
        ctx.fillText("Press ENTER to restart", gameWidth / 2 - 80, gameHeight / 2 + 80);
    }

    // ========================== 7️⃣ 開始遊戲 ==========================

    window.startGame = function () {
        isGameOver = false;
        score = 0;
        character.x = 50;
        character.y = gameHeight - 100;
        character.velocityY = 0;
        obstacles = [];
        gameLoop();
    };

    startGame();  // 自動開始遊戲
});