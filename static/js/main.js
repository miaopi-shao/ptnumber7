//  檔案名稱:main.sj 綜合功能匯集檔
//避免 replaceWith()，改用 removeEventListener() + addEventListener()
//每個 JS 檔案的程式碼封裝在 (() => {...})() 立即執行函式（IIFE）裡

document.addEventListener("DOMContentLoaded", () => {
    // 簡單的 URL 驗證函數
    function isValidURL(string) {
        try {
            new URL(string);
            return true;
        } catch (e) {
            return false;
        }
    }
});


//const offsetMap = {0: 38,1: 500,2: 962,3: 1424,4: 1886,5: 2348,6: 2810,7: 3272,8: 3734,9: 4192,0:4620};
//const offsetMap = {  0: [0, 77],[4543, 4620],  1: [385, 462],[463, 540],  2: [847, 924],[925, 1002],  3: [1309, 1386],[1387, 1464],  4: [1771, 1848],[1849, 1926],  5: [2233, 2310],[2311, 2388],  6: [2695, 2772],[2773, 2850],  7: [3157, 3234],[3235, 3312],  8: [3618, 3695],[3696, 3773],  9: [4080, 4157],[4158, 4235]};

document.addEventListener("DOMContentLoaded", function() {
    const digitHeight = 77; // 每格圖的高度
    const steps = 7;        // 動畫分為 7 步完成

    // 映射表：根據您的描述，將完整數字對應到背景圖片中（每格 77px）
    // 例如：數字 1 的第一個完整展示從 387px 開始，數字 2 從 541px 開始，以此類推307
    // 定義新的映射表：每個數字對應兩個區間，這邊我們取第一組（前半部分）
    const offsetMap = {
        0: [0, 77],
        1: [385, 462],
        2: [847, 924],
        3: [1309, 1386],
        4: [1771, 1848],
        5: [2233, 2310],
        6: [2695, 2772],
        7: [3157, 3234],
        8: [3618, 3695],
        9: [4080, 4157]
    };

    // 每秒更新時鐘：時與分靜態更新，秒數做動畫過渡
    function updateClock() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        // 用映射表更新時與分（靜態更新，取映射表的第一個值）
        updateStaticDigit("hours-tens", parseInt(hours[0]));
        updateStaticDigit("hours-units", parseInt(hours[1]));
        updateStaticDigit("minutes-tens", parseInt(minutes[0]));
        updateStaticDigit("minutes-units", parseInt(minutes[1]));
        updateStaticDigit("seconds-tens", parseInt(seconds[0]));
        
        // 秒數個位使用平滑動畫更新
        smoothUpdateSecondsUnits();
    }
    
        // 靜態更新函數：根據映射表直接設置元素背景位置（取第一組數值）
    function updateStaticDigit(elementId, digit) {
        const elem = document.getElementById(elementId);
        if (elem) {
            const targetOffset = offsetMap[digit][0];
            elem.style.backgroundPosition = `0px -${targetOffset}px`;
            elem.dataset.offset = targetOffset; // 保存當前偏移，用於動畫起點
        }
    }
    
    // 平滑更新秒數個位，利用 requestAnimationFrame 內插更新
    function smoothUpdateSecondsUnits() {
        const elem = document.getElementById("seconds-units");
        if (!elem) return;
        const now = new Date();
        const currentSec = now.getSeconds();
        // 將秒數格式化為兩位字串
        const secStr = String(currentSec).padStart(2, '0');
        const currentUnits = parseInt(secStr[1]);
        const nextSec = (currentSec + 1) % 60;
        const nextSecStr = String(nextSec).padStart(2, '0');
        const nextUnits = parseInt(nextSecStr[1]);
        
        // 從數字 currentUnits 到 nextUnits 的動畫
        // 起始偏移：從 elem.dataset.offset（若沒有則用映射表中對應當前個位）
        const startOffset = parseInt(elem.dataset.offset) || offsetMap[currentUnits][0];
        const targetOffset = offsetMap[nextUnits][0];
        const startTime = Date.now();
        const duration = 1000; // 1秒過渡
        
        function animate() {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const newOffset = startOffset + (targetOffset - startOffset) * progress;
            elem.style.backgroundPosition = `0px -${newOffset}px`;
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                // 動畫結束時設定最終偏移
                elem.dataset.offset = targetOffset;
            }
        }
        requestAnimationFrame(animate);
    }

    // 每秒更新一次時鐘
    setInterval(updateClock, 1);
    updateClock(); // 初始化時鐘
});




document.addEventListener("DOMContentLoaded", () => {
    
    // -----------------------------
    // 設定溫度單位切換：攝氏與華氏
    // -----------------------------
    // 當使用者點擊攝氏按鈕（.cels）
    document.getElementById('cels').addEventListener('click', function(e) {
        e.preventDefault(); // 防止預設連結行為
        localStorage.setItem('tempUnit', 'C'); // 儲存偏好為攝氏
        updateWeather(); // 重新更新天氣資訊
    });

    // 當使用者點擊華氏按鈕（.far）
    document.getElementById('far').addEventListener('click', function(e) {
        e.preventDefault(); // 防止預設連結行為
        localStorage.setItem('tempUnit', 'F'); // 儲存偏好為華氏
        updateWeather(); // 重新更新天氣資訊
    });


    // 將攝氏轉換為華氏的函式
    function celsiusToFahrenheit(celsius) {
        return (celsius * 9 / 5 + 32).toFixed(1); // 保留一位小數
    }

    
    // -----------------------------
    // 更新天氣資訊的函式
    // -----------------------------
    function updateWeather() {
        let selectedCity = document.getElementById("city-select").value;
    
        fetch(`/weather/api/weather?city=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById("weather-display").innerText = "無法取得天氣資訊";
                } else {
                   
                   
                       // 取得使用者偏好（假設預設為攝氏）
                    let maxTemp = parseFloat(data.max_temp);
                    let minTemp = parseFloat(data.min_temp);
                    let tempUnit = localStorage.getItem("tempUnit") || "C";
                    let temperature = parseFloat(data.temperature);
                    let displayTemp;
                    if (tempUnit === "F") {
                         // 若使用者偏好為華氏，則轉換並附上單位
                         //平均溫度
                        displayTemp = celsiusToFahrenheit(temperature) + "°F";
                        //最高及最低溫度
                        displayRange = celsiusToFahrenheit(maxTemp) + "°F | " + celsiusToFahrenheit(minTemp) + "°F";
                    } else {
                         // 否則顯示攝氏
                        displayTemp = temperature + "°C";//平均溫度
                        displayRange = maxTemp + "°C | " + minTemp + "°C";//最高及最低溫度
                    }
                    
                    // 取的前端互動代碼
                    document.getElementById("weather-display").innerHTML = 
                        `${data.city} 天氣：${data.condition}, 溫度：${displayTemp}`;
                    // 更新天气详细信息
                    // 體感溫度：直接輸出氣象局中文描述 (Wx的parameterName)
                    document.getElementById("feels-like").innerText = data.feels_like|| "適合睡覺";
                    // 降雨機率，數字後面加上%
                    document.getElementById("humidity").innerText = data.humidity|| "100%" ;
                    // 最高溫|最低溫：顯示格式 "MaxT°C|MinT°C"
                    // 前端：根據用戶偏好轉換並顯示 "MaxT°C|MinT°C" 或 "MaxT°F|MinT°F"
                    
                    
                    document.getElementById("wind").innerText = displayRange;
                    
                     // 日出、日落、氣壓使用預設值 (或其他來源)
                    document.getElementById("sunrise").innerText = data.SunRiseTime|| "06:31";
                    document.getElementById("sunset").innerText = data.SunSetTime|| "19:52";
                    
                    
                    document.getElementById("barometer").innerText = `${data.barometer}" Hg`;
                    
                    console.log("API 回傳的完整資料：", data);
                    
                    // 字串轉數值，將 parameterValue 轉成數字（假如是字串）
                    let conditionCode = parseInt(data.conditionValue, 10);
                    
                    // 假設 API 回傳資料已儲存在 data 物件中
                    // 並且您確定 data.parameter.parameterValue 存在且為 "天氣代碼："
                    //console.log("天氣代碼：", conditionCode, data.condition); //在瀏覽器的 Console 中看到實際的數值
                    
                    //根據天氣更新圖片
                    let weatherImage = document.getElementById("weather-image");
                    
                    // 字串轉數值的conditionCode是天氣代碼
                    switch (conditionCode) {
                        case 1: // 晴天
                            weatherImage.src = 'static/images/weather/sunny.png';
                            break;
                        case 2: // 晴時多雲
                            weatherImage.src = 'static/images/weather/mostly_clear.png';
                            break; 
                        case 3: // 多雲時晴
                            weatherImage.src = 'static/images/weather/partly_clear.png';
                            break;
                        case 4: // 多雲
                            weatherImage.src = 'static/images/weather/partly_cloudy.png';
                            break;
                        case 5: // 多雲時陰
                            weatherImage.src = 'static/images/weather/mostly_cloudy.png';
                            break;
                        case 6: // 陰時多雲
                            weatherImage.src = 'static/images/weather/mostly_cloudy2.png';
                            break;
                        case 7: // 陰天
                            weatherImage.src = 'static/images/weather/cloudy.png';
                            break;
                        case 8: // 陣雨 (多種情況統一)
                            weatherImage.src = 'static/images/weather/showers.png';
                            break;
                        case 9: // 多雲時陰短暫雨
                            weatherImage.src = 'static/images/weather/mostly_cloudy_with_rain.png';
                            break;
                        case 10: // 陰時多雲短暫雨
                            weatherImage.src = 'static/images/weather/mostly_cloudy_with_rain2.png';
                            break;
                        case 11: // 雨天
                            weatherImage.src = 'static/images/weather/rainy.png';
                            break;
                        case 12: // 多雲時陰有雨
                            weatherImage.src = 'static/images/weather/mostly_cloudy_with_rain3.png';
                            break;
                        case 13: // 陰時多雲有雨
                            weatherImage.src = 'static/images/weather/mostly_cloudy_with_rain4.png';
                            break;
                        case 14: // 陰有陣雨
                            weatherImage.src = 'static/images/weather/showers2.png';
                            break;
                        case 15: // 短暫陣雨或雷雨
                            weatherImage.src = 'static/images/weather/thundershowers.png';
                            break;
                        case 16: // 晴陣雨或雷雨
                            weatherImage.src = 'static/images/weather/showers_thunderstorms.png';
                            break;
                        case 17: // 陰雷陣雨
                            weatherImage.src = 'static/images/weather/cloudy_thundershowers.png';
                            break;
                        case 18: // 雷雨
                            weatherImage.src = 'static/images/weather/thunderstorms.png';
                            break;
                        case 19: // 晴午後陣雨
                            weatherImage.src = 'static/images/weather/afternoon_showers.png';
                            break;
                        case 20: // 多雲午後陣雨
                            weatherImage.src = 'static/images/weather/partly_cloudy_afternoon_showers.png';
                            break;
                        case 21: // 晴雷陣雨
                            weatherImage.src = 'static/images/weather/thundershowers2.png';
                            break;
                        case 22: // 多雲雷陣雨
                            weatherImage.src = 'static/images/weather/cloudy_thundershowers2.png';
                            break;
                        case 23: // 雨或雪
                            weatherImage.src = 'static/images/weather/rain_or_snow.png';
                            break;
                        case 24: // 晴霧
                            weatherImage.src = 'static/images/weather/fog.png';
                            break;
                        case 25: // 多雲霧
                            weatherImage.src = 'static/images/weather/cloudy_fog.png';
                            break;
                        case 26: // 多雲時晴有霧
                            weatherImage.src = 'static/images/weather/partly_clear_fog.png';
                            break;
                        case 27: // 有霧
                            weatherImage.src = 'static/images/weather/fog2.png';
                            break;
                        case 28: // 陰有霧
                            weatherImage.src = 'static/images/weather/cloudy_fog.png';
                            break;
                        case 29: // 局部雨
                            weatherImage.src = 'static/images/weather/local_rain.png';
                            break;
                        case 30: // 局部陣雨
                            weatherImage.src = 'static/images/weather/local_showers.png';
                            break;
                        case 31: // 局部雨和霧
                            weatherImage.src = 'static/images/weather/fog_local_rain.png';
                            break;
                        case 32: // 陰短暫陣雨有霧
                            weatherImage.src = 'static/images/weather/heavy_snow.png';
                            break;
                        case 33: // 多雲局部雷陣雨
                            weatherImage.src = 'static/images/weather/moderate_snow.png';
                            break;
                        case 34: // 陰局部短暫雷陣雨 
                            weatherImage.src = 'static/images/weather/light_snow.png';
                            break;
                        case 35:
                        case 36:
                        case 37:
                        case 38:
                        case 39:
                        case 40:
                        case 41: // 多雲局部短暫陣雨或雷雨有霧 
                            weatherImage.src = 'static/images/weather/snow.png'; break;
                            
                        case 42: // 暴風雪 (新增)
                            weatherImage.src = 'static/images/weather/blizzard.png';break;
                        default:
                            console.log("沒有匹配到代碼:", data.conditionValue);
                            weatherImage.src = 'static/images/preloader.gif'; // 若無匹配的天氣代碼，使用預設圖
                            break;
                    }
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
});



document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("external-search-btn").addEventListener("click", function(event) {
        event.preventDefault(); // 阻止表單的預設提交行為
        const query = document.getElementById("external-search-input").value;
        if (query) {
            window.location.href = "https://duckduckgo.com/?q=" + encodeURIComponent(query);
        }
    });
});





document.addEventListener("DOMContentLoaded", () => {
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
});
