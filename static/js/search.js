// 這可以處理搜尋結果的動態顯示、過濾功能等
document.addEventListener('DOMContentLoaded', function() {
    const searchResults = document.querySelectorAll('.search-results a');
    
    searchResults.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            alert('這是搜尋結果的連結');
        });
    });
});