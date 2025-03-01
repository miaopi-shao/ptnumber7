document.addEventListener("DOMContentLoaded", function() {
    // 取得 canvas 元素及其 2D 畫布上下文
    let canvas = document.getElementById('parkourCanvas');
    if (!canvas) {
        console.error("找不到 id 為 'parkourCanvas' 的 canvas 元素！");
        return;
    }
    let ctx = canvas.getContext('2d');

    // 遊戲變數
    let gameWidth = canvas.width;
    let gameHeight = canvas.height;
    let gravity = 0.8;          // 重力加速度
    let jumpStrength = 14;      // 跳躍力量
    let isJumping = false;      // 是否正在跳躍
    let isGameOver = false;     // 是否遊戲結束
    let score = 0;              // 分數

    // 角色設定
    let character = {
        x: 50,
        y: gameHeight - 100,
        width: 50,
        height: 50,
        velocityY: 0,
        color: "blue"
    };

    // 障礙物設定
    let obstacles = [];
    let obstacleSpeed = 4;

    // 處理跳躍：當按下空白鍵且角色未在跳躍或遊戲未結束時觸發
    document.addEventListener('keydown', function(event) {
        if (event.code === 'Space' && !isJumping && !isGameOver) {
            character.velocityY = -jumpStrength;  // 設定跳躍初速
            isJumping = true;
        }
    });

    // 遊戲主循環
    function gameLoop() {
        if (isGameOver) {
            return showGameOver();
        }
        ctx.clearRect(0, 0, gameWidth, gameHeight);  // 清除畫布

        // 更新角色位置
        character.velocityY += gravity;
        character.y += character.velocityY;

        // 地面碰撞檢測
        if (character.y >= gameHeight - 100) {
            character.y = gameHeight - 100;
            character.velocityY = 0;
            isJumping = false;
        }

        // 顯示角色
        ctx.fillStyle = character.color;
        ctx.fillRect(character.x, character.y, character.width, character.height);

        // 生成障礙物
        if (Math.random() < 0.02) {  // 隨機生成障礙物
            let obstacleHeight = Math.random() * (gameHeight / 2) + 30;
            obstacles.push({
                x: gameWidth,
                y: gameHeight - obstacleHeight,
                width: 30,
                height: obstacleHeight,
                color: "red"
            });
        }

        // 更新並顯示障礙物
        for (let i = 0; i < obstacles.length; i++) {
            let obstacle = obstacles[i];
            obstacle.x -= obstacleSpeed;

            // 如果障礙物移出畫面，刪除並增加分數
            if (obstacle.x + obstacle.width < 0) {
                obstacles.splice(i, 1);
                i--;
                score++;
            }

            // 碰撞檢測
            if (character.x < obstacle.x + obstacle.width &&
                character.x + character.width > obstacle.x &&
                character.y < obstacle.y + obstacle.height &&
                character.y + character.height > obstacle.y) {
                isGameOver = true;
            }

            // 顯示障礙物
            ctx.fillStyle = obstacle.color;
            ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
        }

        // 顯示分數
        ctx.font = "20px Arial";
        ctx.fillStyle = "black";
        ctx.fillText("Score: " + score, 20, 30);

        requestAnimationFrame(gameLoop);
    }

    // 顯示遊戲結束畫面
    function showGameOver() {
        ctx.clearRect(0, 0, gameWidth, gameHeight);
        ctx.fillStyle = "black";
        ctx.font = "40px Arial";
        ctx.fillText("Game Over!", gameWidth / 2 - 100, gameHeight / 2);
        ctx.font = "20px Arial";
        ctx.fillText("Final Score: " + score, gameWidth / 2 - 50, gameHeight / 2 + 40);
    }

    // 定義全域的 startGame 函數，供 HTML 按鈕使用
    window.startGame = function() {
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

    // 選擇是否自動開始遊戲？（若不需要，自行移除下面這行）
     startGame();
});
