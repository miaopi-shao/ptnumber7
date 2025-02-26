// 隨機產生深色顏色
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



// 控制彈出註冊視窗
document.getElementById("register-btn").addEventListener("click", function() {
    document.getElementById("modal-overlay").classList.add("active");
    document.getElementById("register-modal").classList.add("active");
});

// 關閉註冊視窗
document.getElementById("close-register-modal").addEventListener("click", function() {
    document.getElementById("modal-overlay").classList.remove("active");
    document.getElementById("register-modal").classList.remove("active");
});

// 點擊背景遮罩也能關閉視窗
document.getElementById("modal-overlay").addEventListener("click", function() {
    document.getElementById("modal-overlay").classList.remove("active");
    document.getElementById("register-modal").classList.remove("active");
});

// 監聽表單提交
document.getElementById("register-form").addEventListener("submit", function(event) {
    event.preventDefault(); // 防止表單刷新頁面

    let username = document.getElementById("register-username").value;
    let phrase = document.getElementById("register-phrase").value;
    let email = document.getElementById("register-email").value;

    fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            phrase: phrase,
            email: email
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("register-error-msg").innerText = data.error;
        } else {
            alert("註冊成功！請使用您的帳號登入。");
            document.getElementById("modal-overlay").classList.remove("active");
            document.getElementById("register-modal").classList.remove("active");
        }
    })
    .catch(error => console.error("錯誤:", error));
});





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







// 外部搜尋 (DuckDuckGo)
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








// 用戶輸入網址進行爬蟲
document.getElementById("scrape-button").addEventListener("click", function () {
    let url = document.getElementById("url-input").value;

    // 驗證 URL 的基本格式
    if (!isValidURL(url)) {
        alert("請輸入有效的網址");
        return;
    }

    fetch("/user_scrape", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("錯誤: " + data.error);
        } else {
            document.getElementById("scrape-result").innerHTML = `
                <h3>標題: ${data.title}</h3>
                <p>${data.text}...</p>
                <button id="fetch-full">是否爬取完整內容?</button>
            `;

            document.getElementById("fetch-full").addEventListener("click", function () {
                openFullScrapeModal(data.url);
            });
        }
    })
    .catch(error => {
        console.error("請求失敗", error);
        alert("請求失敗，請檢查控制台了解更多詳情");
    });
});

function openFullScrapeModal(url) {
    let modalHTML = `
        <div id="scrape-modal" class="modal">
            <div class="modal-content">
                <h3>選擇爬取範圍</h3>
                <label>篩選標題關鍵字: <input type="text" id="keyword"></label><br>
                <label>爬取字數範圍:
                    <select id="text-length">
                        <option value="1000">1000字</option>
                        <option value="2000">2000字</option>
                        <option value="5000">5000字</option>
                    </select>
                </label><br>
                <button id="confirm-fetch">確定</button>
                <button id="close-modal">取消</button>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML("beforeend", modalHTML);
    
    let modal = document.getElementById("scrape-modal");
    setTimeout(() => {
        modal.style.opacity = "1";
        modal.style.visibility = "visible";
    }, 50); // 避免剛插入時還是隱藏的

    document.getElementById("close-modal").addEventListener("click", function () {
        modal.style.opacity = "0";
        modal.style.visibility = "hidden";
        setTimeout(() => modal.remove(), 300); // 讓動畫結束後移除
    });

    document.getElementById("confirm-fetch").addEventListener("click", function () {
        let keyword = document.getElementById("keyword").value;
        let textLength = document.getElementById("text-length").value;

        fetch("/user_scrape/full", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: url,
                text_length: parseInt(textLength),
                keyword: keyword
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("錯誤: " + data.error);
            } else {
                document.getElementById("scrape-result").innerHTML = `
                    <h3>標題: ${data.title}</h3>
                    <p>${data.text}</p>
                `;
            }
            modal.style.opacity = "0";
            modal.style.visibility = "hidden";
            setTimeout(() => modal.remove(), 300);
        })
        .catch(error => {
            console.error("請求失敗", error);
            alert("請求失敗，請檢查控制台了解更多詳情");
            modal.style.opacity = "0";
            modal.style.visibility = "hidden";
            setTimeout(() => modal.remove(), 300);
        });
    });
}

// 簡單的 URL 驗證函數
function isValidURL(string) {
    try {
        new URL(string);
        return true;
    } catch (e) {
        return false;
    }
}
