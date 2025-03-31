// 站內搜尋按鈕處理邏輯 search2.js

document.addEventListener('DOMContentLoaded', function() {
    console.log("search.js 加載完成");

    // 站內搜尋按鈕處理邏輯
    const searchBtn = document.getElementById('internal-search-btn'); // 確認按鈕
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            const query = document.getElementById('internal-search-input').value.trim(); // 獲取搜尋關鍵字，並去掉多餘空格
            const category = document.getElementById('search-category').value; // 獲取分類

            if (query === "") {
                alert("請輸入搜尋關鍵字");
                return;
            }

            let url = `/internal_search?query=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}`;
            // 使用 Fetch API 發送請求並動態更新結果
            fetch(url)
                .then(response => response.text()) // 獲取返回的 HTML 結果
                .then(html => {
                    // 將結果插入到頁面的特定區域
                    document.getElementById('search-results').innerHTML = html;
                })
                .catch(error => console.error('搜索失敗:', error));
            window.location.href = url;
        });
    }
});
