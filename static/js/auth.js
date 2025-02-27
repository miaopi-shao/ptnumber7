//避免 replaceWith()，改用 removeEventListener() + addEventListener()
//每個 JS 檔案的程式碼封裝在 (() => {...})() 立即執行函式（IIFE）裡

document.addEventListener('DOMContentLoaded', () => {  // 1. 包裹成立即執行函式（IIFE），避免全域變數污染
    // 取得 DOM 元素
    const modalOverlay = document.getElementById("modal-overlay");  // 2. 取得 modal 背景
    const registerModal = document.getElementById("register-modal");  // 3. 取得註冊視窗
    const registerBtn = document.getElementById("register-btn");  // 4. 取得註冊按鈕
    const closeBtn = document.getElementById("close-register-modal");  // 5. 取得關閉註冊視窗按鈕
    const registerForm = document.getElementById("register-form");  // 6. 取得註冊表單
    const loginForm = document.getElementById("login-form");  // 7. 取得登入表單
    
    // =====  API 請求封裝（避免重複 fetch） =====
    // 8. 定義一個 API 請求的函式
    async function apiRequest(url, method, bodyData) {
        try {
            const response = await fetch(url, {  // 9. 發送 API 請求
                method: method,  // 10. 設定請求方法（GET, POST, 等）
                headers: { "Content-Type": "application/json" },  // 11. 設定標頭，告訴伺服器資料格式為 JSON
                body: JSON.stringify(bodyData),  // 12. 將資料轉換為 JSON 格式並放入請求的 body
            });

            if (!response.ok) {  // 13. 檢查回應是否成功
                throw new Error(`HTTP 錯誤！狀態碼: ${response.status}`);  // 14. 如果錯誤，拋出異常
            }
            return await response.json();  // 15. 解析 JSON 格式的回應資料並返回
        } catch (error) {  // 16. 捕捉異常並處理
            console.error("請求失敗:", error);  // 17. 在控制台輸出錯誤訊息
            alert("伺服器錯誤，請稍後再試！");  // 18. 彈出錯誤提示
        }
    }

    // =====  開啟 & 關閉 註冊視窗 =====
    // 19. 點擊註冊按鈕顯示註冊視窗
    registerBtn.addEventListener("click", () => {
        modalOverlay.classList.add("active");  // 20. 顯示背景遮罩層
        registerModal.classList.add("active");  // 21. 顯示註冊視窗
    });

    // 22. 定義一個關閉註冊視窗的函式
    function closeRegisterModal() {
        modalOverlay.classList.remove("active");  // 23. 隱藏背景遮罩層
        registerModal.classList.remove("active");  // 24. 隱藏註冊視窗
    }

    // 25. 當點擊關閉按鈕時，關閉註冊視窗
    closeBtn.addEventListener("click", closeRegisterModal);
    // 26. 當點擊背景區域時，也會關閉註冊視窗
    modalOverlay.addEventListener("click", (event) => {
        if (event.target === modalOverlay) closeRegisterModal();  // 27. 如果點擊背景區域，關閉視窗
    });

    // =====  註冊帳號 =====
    // 28. 註冊表單提交事件
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();  // 29. 防止表單提交後頁面重新整理

        // 30. 取得使用者輸入的註冊資料
        let username = document.getElementById("register-username").value;  // 31. 取得使用者名稱
        let phrase = document.getElementById("register-password").value;  // 32. 取得密碼
        let email = document.getElementById("register-email").value;  // 33. 取得電子郵件
        let errorMsg = document.getElementById("register-error-msg");  // 34. 取得錯誤訊息顯示區域

        errorMsg.innerText = "";  // 35. 清空錯誤訊息

        // 36. 發送註冊請求到後端 /auth/register，這會觸發 auth.py 進行帳號註冊
        let data = await apiRequest("/auth/register", "POST", { username, phrase, email });

        if (data?.error) {  // 37. 如果後端回傳錯誤訊息
            errorMsg.innerText = data.error;  // 38. 顯示錯誤訊息
        } else {  // 39. 如果註冊成功
            alert("註冊成功！請使用您的帳號登入。");  // 40. 顯示註冊成功訊息
            closeRegisterModal();  // 41. 關閉註冊視窗
        }
    });

    // =====  登入帳號 =====
    // 42. 登入表單提交事件
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();  // 43. 防止表單提交後頁面重新整理

        // 44. 取得使用者輸入的登入資料
        let username = document.getElementById("username").value;  // 45. 取得使用者名稱
        let phrase = document.getElementById("password").value;  // 46. 取得密碼

        // 47. 發送登入請求到後端 /auth/login，這會觸發 auth.py 進行登入驗證
        let data = await apiRequest("/auth/login", "POST", { username, phrase });

        if (data?.token) {  // 48. 如果後端回傳 Token，表示登入成功
            localStorage.setItem("token", data.token);  // 49. 儲存 Token 至 localStorage
            alert("登入成功！");  // 50. 顯示登入成功訊息
            window.location.href = "/dashboard";  // 51. 轉跳到登入後的頁面（後端會使用 app.py 路由）
        } else {  // 52. 如果登入失敗
            alert(data?.error || "登入失敗！");  // 53. 顯示錯誤訊息
        }
    });

    // =====  登出帳號 =====
    // 54. 當點擊登出按鈕時，清除 Token 並重新載入頁面
    document.getElementById("logout-btn")?.addEventListener("click", () => {
        localStorage.removeItem("token");  // 55. 清除 Token
        alert("已登出！");  // 56. 顯示登出成功訊息
        window.location.reload();  // 57. 重新載入頁面
    });

});
