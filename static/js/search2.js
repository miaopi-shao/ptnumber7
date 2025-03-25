
// 站內搜尋按鈕處理邏輯
document.addEventListener('DOMContentLoaded', function() {
    console.log("search.js 加載完成");

    // 站內搜尋按鈕處理邏輯
    const searchBtn = document.getElementById('internal-search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            const query = document.getElementById('internal-search-input').value.trim(); // 去掉多餘空格
            const category = document.getElementById('search-category').value;

            if (query === "") {
                alert("請輸入搜尋關鍵字");
                return;
            }

            let url = `/internal_search?query=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}`;
            window.location.href = url;
        });
    }
});
