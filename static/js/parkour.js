// parkour.js (跑酷遊戲)

let canvas = document.getElementById('parkourCanvas');
let ctx = canvas.getContext('2d');

// 遊戲變數
let gameWidth = canvas.width;
let gameHeight = canvas.height;

let gravity = 0.8;  // 重力加速度
let jumpStrength = 12;  // 跳躍力量
let isJumping = false;  // 是否正在跳躍
let isGameOver = false;  // 是否遊戲結束
let score = 0;  // 分數

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

// 處理跳躍
document.addEventListener('keydown', function(event) {
    if (event.code === 'Space' && !isJumping && !isGameOver) {
        character.velocityY = -jumpStrength;  // 設定跳躍的初速
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
    character.velocityY += gravity;  // 更新垂直速度
    character.y += character.velocityY;  // 更新垂直位置

    // 地面碰撞檢測
    if (character.y >= gameHeight - 100) {
        character.y = gameHeight - 100;
        character.velocityY = 0;
        isJumping = false;  // 回到地面時可以再次跳躍
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

        // 如果障礙物移出畫面，就刪除它
        if (obstacle.x + obstacle.width < 0) {
            obstacles.splice(i, 1);
            i--;
            score++;  // 每成功避開一個障礙物，增加分數
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

    requestAnimationFrame(gameLoop);  // 重新呼叫遊戲循環
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

// 開始遊戲循環
gameLoop();



// 右側欄-更新時間
function updateTime() {
    let now = new Date();
    let formattedTime = now.toLocaleString("zh-TW", { 
        year: "numeric", month: "2-digit", day: "2-digit",
        hour: "2-digit", minute: "2-digit", second: "2-digit"
    });
    document.getElementById("time-display").innerText = formattedTime;
}
setInterval(updateTime, 1000);
updateTime();




// 取得天氣資訊並顯示
function updateWeather() {
    let selectedCity = document.getElementById("city-select").value;
    
    fetch(`/api/weather?city=${selectedCity}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById("weather-display").innerText = "無法取得天氣資訊";
            } else {
                document.getElementById("weather-display").innerText = 
                    `${data.city} 天氣：${data.condition}, 溫度：${data.temperature}°C`;
            }
        })
        .catch(error => {
            console.error("Error fetching weather:", error);
            document.getElementById("weather-display").innerText = "載入天氣資訊時發生錯誤";
        });
}

// 當用戶選擇不同城市時，更新天氣資訊
document.getElementById("city-select").addEventListener("change", updateWeather);

// 每 10 分鐘更新一次天氣資訊
setInterval(updateWeather, 10 * 60 * 1000);
updateWeather();