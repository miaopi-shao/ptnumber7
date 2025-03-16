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
    
        fetch(`/api/weather?city=${selectedCity}`)
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
                            //Image by <a href="https://pixabay.com/users/pixaline-1569622/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=1987414">Sabine Kroschel</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=1987414">Pixabay</a>
                            break;
                        case 4: // 多雲
                        case 8: // 陰天
                            weatherImage.src = 'static/images/weather/cloudy.png';
                            //Image by <a href="https://pixabay.com/users/openicons-28911/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=98536">OpenIcons</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=98536">Pixabay</a>
                            break;
                        case 5: // 晴間多雲
                        case 6: // 晴間多雲 
                            weatherImage.src = 'static/images/weather/partly_cloudy.png';
                            //Image by <a href="https://pixabay.com/users/theujulala-59978/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=1265202">TheUjulala</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=1265202">Pixabay</a>
                            break;
                        case 7: // 大部多雲
                            weatherImage.src = 'static/images/weather/mostly_cloudy.png';
                            //Image by <a href="https://pixabay.com/users/openclipart-vectors-30363/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=159378">OpenClipart-Vectors</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=159378">Pixabay</a>
                            break;
                        case 15: // 大雨
                            weatherImage.src = 'static/images/weather/heavy_rain.png';
                            //Image by <a href="https://pixabay.com/users/openicons-28911/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=98538">OpenIcons</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=98538">Pixabay</a>
                            break;
                        case 17: // 大暴雨
                            weatherImage.src = 'static/images/weather/heavy_storm.png';
                            //Image by <a href="https://pixabay.com/users/openclipart-vectors-30363/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=159389">OpenClipart-Vectors</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=159389">Pixabay</a>
                            break;
                        case 18: // 特大暴雨
                            weatherImage.src = 'static/images/weather/severe_storm.png';
                            //Image by <a href="https://pixabay.com/users/openicons-28911/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=98539">OpenIcons</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=98539">Pixabay</a>
                            break;
                        case 3: // 雷陣雨
                            weatherImage.src = 'static/images/weather/thunderstorm.png';
                            //Image by <a href="https://pixabay.com/users/clker-free-vector-images-3736/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=29949">Clker-Free-Vector-Images</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=29949">Pixabay</a>
                            break;
                        case 10: // 小雨 (新增)
                        case 11: // 中雨 (新增)
                            weatherImage.src = 'static/images/weather/light_rain.png';
                            //Image by <a href="https://pixabay.com/users/theujulala-59978/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=1265201">TheUjulala</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=1265201">Pixabay</a>
                            break;
                        case 9: // 陣雨 
                            weatherImage.src = 'static/images/weather/showers.png';
                            //no
                            break;
                        case 19: // 雪
                            weatherImage.src = 'static/images/weather/snow.png';
                            //Image by <a href="https://pixabay.com/users/openclipart-vectors-30363/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=149829">OpenClipart-Vectors</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=149829">Pixabay</a>
                            break;
                        case 20: // 小雪
                            weatherImage.src = 'static/images/weather/light_snow.png';
                            break;
                        case 21: // 中雪
                            weatherImage.src = 'static/images/weather/moderate_snow.png';
                            break;
                        case 22: // 大雪
                            weatherImage.src = 'static/images/weather/heavy_snow.png';
                            break;
                        case 23: // 霧
                            weatherImage.src = 'static/images/weather/fog.png';
                            //Image by <a href="https://pixabay.com/users/openclipart-vectors-30363/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=159381">OpenClipart-Vectors</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=159381">Pixabay</a>
                            break;
                        case 24: // 霜
                            weatherImage.src = 'static/images/weather/frost.png';
                            //Image by <a href="https://pixabay.com/users/inspire-studio-22128832/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=7234858">J S</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=7234858">Pixabay</a>
                            break;
                        case 26: // 沙塵暴 (新增)
                            weatherImage.src = 'static/images/weather/dust_storm.png';
                            //<a href="https://www.flaticon.com/free-icons/sand-storm" title="sand storm icons">Sand storm icons created by IconBaandar - Flaticon</a>
                            break;
                        case 28: // 強風 (新增)
                            weatherImage.src = 'static/images/weather/strong_wind.png';
                            //Image by <a href="https://pixabay.com/users/inspire-studio-22128832/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=7126916">J S</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=7126916">Pixabay</a>
                            break;
                        case 29: // 暴風雪 (新增)
                            weatherImage.src = 'static/images/weather/blizzard.png';
                            //Image by <a href="https://pixabay.com/users/openclipart-vectors-30363/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=1292857">OpenClipart-Vectors</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=1292857">Pixabay</a>
                            break;
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
