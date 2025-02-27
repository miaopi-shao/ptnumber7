//避免 replaceWith()，改用 removeEventListener() + addEventListener()
//每個 JS 檔案的程式碼封裝在 (() => {...})() 立即執行函式（IIFE）裡

// 右側欄-更新時間(沒有問題)
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



// 外部搜尋 (DuckDuckGo)(沒有問題)
document.getElementById("external-search-btn").addEventListener("click", function() {
    var query = document.getElementById("external-search-input").value;
    if (query) {
        window.location.href = "https://duckduckgo.com/?q=" + encodeURIComponent(query);
    }
});






// 內部搜尋 (站內爬蟲資料)
document.getElementById("internal-search-btn").addEventListener("click", function() {
    var query = document.getElementById("internal-search-input").value;
    if (query) {
        fetch('/search?q=' + encodeURIComponent(query))
            .then(response => response.json())
            .then(data => {
                console.log(data);
            })
            .catch(error => console.error('Error:', error));
    }
});





// 隨機產生深色顏色(沒有問題)
function getRandomDarkColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    // 讓每個顏色的 R、G、B 成分較低（產生深色）
    for (let i = 0; i < 6; i++) {
        // 確保數值不會超過 7（產生較暗的顏色）
        color += letters[Math.floor(Math.random() * 8)];
    }
    return color;
}

// 為每個 <a> 標籤設定隨機深色背景色
document.querySelectorAll('.login-container2 a').forEach(function(link) {
    link.style.backgroundColor = getRandomDarkColor();
});





// 簡單的 URL 驗證函數
function isValidURL(string) {
    try {
        new URL(string);
        return true;
    } catch (e) {
        return false;
    }
}
