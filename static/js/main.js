# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 16:25:48 2025

@author: OAP-0001
"""


// 彈出註冊視窗
document.getElementById('showRegisterPopup').addEventListener('click', function() {
    document.getElementById('registerPopup').style.display = 'block';
});

// 關閉註冊視窗
document.getElementById('closePopup').addEventListener('click', function() {
    document.getElementById('registerPopup').style.display = 'none';
});

// 註冊提交表單
document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('newUsername').value;
    const phrase = document.getElementById('newPhrase').value;
    const keepEveryN = document.getElementById('keepEveryN').value;

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username,
            phrase,
            keep_every_n: keepEveryN
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(`註冊成功！帳號：${data.username}, 密碼：${data.encrypted_password}`);
        document.getElementById('registerPopup').style.display = 'none';
    })
    .catch(error => alert('註冊失敗，請稍後再試'));
});

// 新增：爬蟲功能按鈕事件
document.getElementById('startCrawler').addEventListener('click', function() {
    // 顯示提示資訊
    document.getElementById('crawlerResult').innerHTML = '正在爬取中，請稍候...';
    
    // 使用 fetch 送出 GET 請求到 /scrape
    fetch('/scrape')
        .then(response => response.json())
        .then(data => {
            if(data.error) {
                document.getElementById('crawlerResult').innerHTML = `<span style="color:red;">錯誤：${data.error}</span>`;
            } else {
                document.getElementById('crawlerResult').innerHTML = data.scraped_data;
            }
        })
        .catch(error => {
            document.getElementById('crawlerResult').innerHTML = `<span style="color:red;">發生錯誤：${error}</span>`;
        });
});