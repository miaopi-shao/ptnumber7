// tetris.js  (俄羅斯方塊遊戲)
let canvas = document.getElementById('gameCanvas');
let ctx = canvas.getContext('2d');

// 設定畫布尺寸
let rows = 20;
let cols = 10;
let blockSize = 30;  // 每個方塊的大小

// 遊戲區域尺寸
let boardWidth = cols * blockSize;
let boardHeight = rows * blockSize;
canvas.width = boardWidth;
canvas.height = boardHeight;

// 顏色定義
const colors = ['#FF5733', '#33FF57', '#3357FF', '#FFFF33', '#FF33FF', '#33FFFF', '#FF5733'];

// 定義方塊形狀
const tetrominoes = [
    [[1, 1, 1, 1]],  // I形
    [[1, 1, 0], [0, 1, 1]],  // Z形
    [[0, 1, 1], [1, 1, 0]],  // S形
    [[1, 1], [1, 1]],  // O形
    [[0, 1, 0], [1, 1, 1]],  // T形
    [[1, 0, 0], [1, 1, 1]],  // L形
    [[0, 0, 1], [1, 1, 1]]   // J形
];

// 方塊的初始化
let currentTetromino = generateTetromino();
let currentPosition = { x: Math.floor(cols / 2) - 1, y: 0 };  // 方塊初始位置

// 儲存已經放置的方塊
let board = Array.from({ length: rows }, () => Array(cols).fill(0));

// 處理鍵盤輸入
document.addEventListener('keydown', handleKeyPress);

// 開始遊戲循環
let gameInterval = setInterval(updateGame, 500);  // 每500ms執行一次遊戲更新

function handleKeyPress(event) {
    if (event.key === 'ArrowLeft') {
        moveTetromino(-1, 0);  // 向左移動
    } else if (event.key === 'ArrowRight') {
        moveTetromino(1, 0);   // 向右移動
    } else if (event.key === 'ArrowDown') {
        moveTetromino(0, 1);   // 向下移動
    } else if (event.key === 'ArrowUp') {
        rotateTetromino();     // 旋轉方塊
    }
}

// 更新遊戲狀態
function updateGame() {
    if (checkCollision(currentTetromino, currentPosition.x, currentPosition.y + 1)) {
        placeTetromino();
        clearLines();
        currentTetromino = generateTetromino();
        currentPosition = { x: Math.floor(cols / 2) - 1, y: 0 };
        if (checkCollision(currentTetromino, currentPosition.x, currentPosition.y)) {
            // 如果新方塊一開始就有碰撞，表示遊戲結束
            alert("Game Over!");
            clearInterval(gameInterval);
        }
    } else {
        currentPosition.y += 1;  // 方塊下落
    }
    drawBoard();
    drawTetromino();
}

// 生成新的隨機方塊
function generateTetromino() {
    let shape = tetrominoes[Math.floor(Math.random() * tetrominoes.length)];
    return shape;
}

// 繪製遊戲區域
function drawBoard() {
    ctx.clearRect(0, 0, boardWidth, boardHeight);  // 清空畫布
    // 畫已經放置的方塊
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

// 判斷方塊是否與其他方塊碰撞
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
                board[currentPosition.y + y][currentPosition.x + x] = 1;
            }
        }
    }
}

// 消除滿行
function clearLines() {
    for (let y = 0; y < rows; y++) {
        if (board[y].every(cell => cell !== 0)) {
            board.splice(y, 1);
            board.unshift(Array(cols).fill(0));  // 新行填充0
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
    let rotatedTetromino = currentTetromino[0].map((_, index) => currentTetromino.map(row => row[index])).reverse();
    if (!checkCollision(rotatedTetromino, currentPosition.x, currentPosition.y)) {
        currentTetromino = rotatedTetromino;
    }
}
