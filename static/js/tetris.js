// tetris.js  (俄羅斯方塊遊戲)
// 取得畫布與繪圖上下文
let canvas = document.getElementById('gameCanvas');
let ctx = canvas.getContext('2d');

// 設定畫布尺寸
let rows = 20; // 行數（遊戲區域的高度）
let cols = 10; // 列數（遊戲區域的寬度）
let blockSize = 30; // 每個方塊的大小（像素）

// 設定遊戲區域的總寬度與高度
let boardWidth = cols * blockSize; // 畫布的寬度
let boardHeight = rows * blockSize; // 畫布的高度
canvas.width = boardWidth;
canvas.height = boardHeight;

// 定義顏色清單，用於不同的方塊
const colors = ['#FF5733', '#33FF57', '#3357FF', '#FFFF33', '#FF33FF', '#33FFFF', '#FF5733'];


// 定義所有方塊的形狀（Tetrominoes）
const tetrominoes = [
    [[1, 1, 1, 1]],  // I形（長條形）
    
    [[1, 1, 0], [0, 1, 1]],  // Z形
    
    [[0, 1, 1], [1, 1, 0]],  // S形
    
    [[1, 1], [1, 1]],  // O形（方形）
    
    [[0, 1, 0], [1, 1, 1]],  // T形
    
    [[1, 0, 0], [1, 1, 1]],  // L形
    
    [[0, 0, 1], [1, 1, 1]]   // J形
];


// 初始化變數
let currentTetromino; // 當前方塊形狀
let currentPosition;  // 當前方塊位置（座標）
let board = Array.from({ length: rows }, () => Array(cols).fill(0)); // 建立遊戲區域的二維陣列
let gameInterval; // 遊戲循環的計時器
let gameStarted = false; // 判斷遊戲是否已經開始

// 處理鍵盤輸入的事件監聽器
document.addEventListener('keydown', handleKeyPress);
document.getElementById('startButton').addEventListener('click', startGame); // 綁定開始按鈕事件

// 滑鼠移動與點擊事件
canvas.addEventListener('mousemove', handleMouseMove); // 滑鼠移動用於控制左右移動
canvas.addEventListener('click', () => moveTetromino(0, 1)); // 點擊畫布可加速下降

// 遊戲開始函數
function startGame() {
    if (!gameStarted) {
        gameStarted = true; // 標記遊戲已經開始
        currentTetromino = generateTetromino(); // 生成初始的隨機方塊
        currentPosition = { x: Math.floor(cols / 2) - 1, y: 0 }; // 初始位置
        gameInterval = setInterval(updateGame, 500); // 每500ms更新遊戲一次
    }
}

// 處理鍵盤事件函數
function handleKeyPress(event) {
    if (event.key === 'ArrowLeft' || event.key === 'a') {
        moveTetromino(-1, 0); // 向左移動
    } else if (event.key === 'ArrowRight' || event.key === 'd') {
        moveTetromino(1, 0); // 向右移動
    } else if (event.key === 'ArrowDown' || event.key === ' ') {
        moveTetromino(0, 1); // 加速下降
    } else if (event.key === 'ArrowUp' || event.key === 'w') {
        rotateTetromino(); // 旋轉方塊
    }
}

// 滑鼠移動處理函數
function handleMouseMove(event) {
    let rect = canvas.getBoundingClientRect(); // 取得畫布的位置
    let mouseX = event.clientX - rect.left; // 滑鼠在畫布內的X座標
    let targetCol = Math.floor(mouseX / blockSize); // 將滑鼠X座標轉換為遊戲區域的列數
    if (targetCol >= 0 && targetCol < cols) {
        currentPosition.x = targetCol; // 更新方塊的列位置
    }
}

// 更新遊戲狀態函數
function updateGame() {
    if (checkCollision(currentTetromino, currentPosition.x, currentPosition.y + 1)) {
        placeTetromino(); // 如果碰撞，放置方塊到遊戲區域
        clearLines(); // 清除已滿的行
        currentTetromino = generateTetromino(); // 生成新的隨機方塊
        currentPosition = { x: Math.floor(cols / 2) - 1, y: 0 }; // 方塊位置初始化
        if (checkCollision(currentTetromino, currentPosition.x, currentPosition.y)) {
            alert("遊戲結束！"); // 判斷遊戲結束
            clearInterval(gameInterval); // 停止遊戲循環
        }
    } else {
        currentPosition.y += 1; // 方塊下落
    }
    drawBoard(); // 繪製遊戲區域
    drawTetromino(); // 繪製當前方塊
}

// 生成新的隨機方塊
function generateTetromino() {
    let shape = tetrominoes[Math.floor(Math.random() * tetrominoes.length)];
    return shape;
}

// 繪製遊戲區域
function drawBoard() {
    ctx.clearRect(0, 0, boardWidth, boardHeight); // 清空畫布
    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            if (board[y][x] !== 0) {
                ctx.fillStyle = colors[board[y][x] - 1];
                ctx.fillRect(x * blockSize, y * blockSize, blockSize, blockSize);
                ctx.strokeRect(x * blockSize, y * blockSize, blockSize, blockSize);
            }
        }
    }
}

// 繪製當前的方塊
function drawTetromino() {
    for (let y = 0; y < currentTetromino.length; y++) {
        for (let x = 0; x < currentTetromino[y].length; x++) {
            if (currentTetromino[y][x] !== 0) {
                ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
                ctx.fillRect((currentPosition.x + x) * blockSize, (currentPosition.y + y) * blockSize, blockSize, blockSize);
                ctx.strokeRect((currentPosition.x + x) * blockSize, (currentPosition.y + y) * blockSize, blockSize, blockSize);
            }
        }
    }
}

// 判斷是否碰撞
function checkCollision(tetromino, offsetX, offsetY) {
    for (let y = 0; y < tetromino.length; y++) {
        for (let x = 0; x < tetromino[y].length; x++) {
            if (tetromino[y][x] !== 0) {
                let newX = currentPosition.x + x + offsetX;
                let newY = currentPosition.y + y + offsetY;
                if (newX < 0 || newX >= cols || newY >= rows || board[newY][newX] !== 0) {
                    return true;
                }
            }
        }
    }
    return false;
}

// 放置方塊到遊戲區域
function placeTetromino() {
    for (let y = 0; y < currentTetromino.length; y++) {
        for (let x = 0; x < currentTetromino[y].length; x++) {
            if (currentTetromino[y][x] !== 0) {
                board[currentPosition.y + y][currentPosition.x + x] = 1; // 更新遊戲區域
            }
        }
    }
}

// 消除已滿的行
function clearLines() {
    for (let y = 0; y < rows; y++) {
        if (board[y].every(cell => cell !== 0)) { // 判斷整行是否填滿
            board.splice(y, 1); // 刪除已滿的行
            board.unshift(Array(cols).fill(0)); // 在頂部添加一行空白
        }
    }
}

// 移動方塊
function moveTetromino(offsetX, offsetY) {
    if (!checkCollision(currentTetromino, currentPosition.x + offsetX, currentPosition.y + offsetY)) {
        currentPosition.x += offsetX;
        currentPosition.y += offsetY;
    }
}

// 旋轉方塊
function rotateTetromino() {
    // 生成旋轉後的新方塊矩陣（順時針旋轉90度）
    let rotatedTetromino = currentTetromino[0].map((_, index) => 
        currentTetromino.map(row => row[index])
    ).reverse(); // 使用矩陣轉置並反轉行順序

    // 如果旋轉後的位置不會產生碰撞，則更新當前的方塊為旋轉後的方塊
    if (!checkCollision(rotatedTetromino, currentPosition.x, currentPosition.y)) {
        currentTetromino = rotatedTetromino;
    }
}