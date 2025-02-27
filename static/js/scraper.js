(() => {
    // 用戶輸入網址進行爬蟲
    document.getElementById("scrape-btn").addEventListener("click", function () {
        let url = document.getElementById("url-input").value;

        // 驗證 URL 的基本格式
        if (!isValidURL(url)) {
            alert("請輸入有效的網址");
            return;
        }

        // 發送請求到伺服器進行爬蟲
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
                // 更新爬取結果，並新增按鈕讓用戶選擇是否爬取完整內容
                document.getElementById("scrape-result").innerHTML = `
                    <h3>標題: ${data.title}</h3>
                    <p>${data.text}...</p>
                    <button id="fetch-full">是否爬取完整內容?</button>
                `;

                let fetchFullButton = document.getElementById("fetch-full");

                // 先移除舊的事件監聽，確保不會重複綁定
                fetchFullButton.removeEventListener("click", openFullScrapeModal);

                // 重新綁定事件
                fetchFullButton.addEventListener("click", function () {
                    openFullScrapeModal(data.url);
                });
            }
        })
        .catch(error => {
            console.error("請求失敗", error);
            alert("請求失敗，請檢查控制台了解更多詳情");
        });
    });

    // 打開爬取範圍選擇視窗
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

        // 檢查是否已經存在 modal，存在則刪除，確保不會重複添加
        let existingModal = document.getElementById("scrape-modal");
        if (existingModal) {
            existingModal.remove();
        }
        document.body.insertAdjacentHTML("beforeend", modalHTML);

        let modal = document.getElementById("scrape-modal");

        // 設定淡入動畫
        setTimeout(() => {
            modal.style.opacity = "1";
            modal.style.visibility = "visible";
        }, 50);

        // 綁定關閉按鈕的點擊事件
        let closeBtn = document.getElementById("close-modal");

        // 先移除舊的事件監聽，避免重複綁定
        closeBtn.removeEventListener("click", closeModal);
        closeBtn.addEventListener("click", closeModal);

        function closeModal() {
            modal.style.opacity = "0";
            modal.style.visibility = "hidden";
            setTimeout(() => modal.remove(), 300);
        }

        // 綁定確定爬取的按鈕
        document.getElementById("confirm-fetch").addEventListener("click", function () {
            let keyword = document.getElementById("keyword").value;
            let textLength = document.getElementById("text-length").value;

            // 發送請求，爬取完整內容
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
                    // 顯示完整爬取結果
                    document.getElementById("scrape-result").innerHTML = `
                        <h3>標題: ${data.title}</h3>
                        <p>${data.text}</p>
                    `;
                }
                closeModal(); // 爬取完成後關閉視窗
            })
            .catch(error => {
                console.error("請求失敗", error);
                alert("請求失敗，請檢查控制台了解更多詳情");
                closeModal(); // 發生錯誤時也關閉視窗
            });
        });
    }
});