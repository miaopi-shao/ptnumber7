# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 16:25:48 2025

@author: OAP-0001
"""




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
        });
    });
}
