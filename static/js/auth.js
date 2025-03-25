//避免 replaceWith()，改用 removeEventListener() + addEventListener()
//每個 JS 檔案的程式碼封裝在 (() => {...})() 立即執行函式（IIFE）裡

// 定義 apiRequest的運行邏輯
async function apiRequest(endpoint, method, body) {
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : null,
    };
    try {
        const response = await fetch(endpoint, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error during API request:', error);
        throw error;
    }
}


document.addEventListener('DOMContentLoaded', () => {  // 1. 包裹成立即執行函式（IIFE），避免全域變數污染
    // 取得 DOM 元素
    const modalOverlay = document.getElementById("modal-overlay");  // 2. 取得 modal 背景
    const registerModal = document.getElementById("register-modal");  // 3. 取得註冊視窗
    const registerBtn = document.getElementById("register-btn");  // 4. 取得註冊按鈕
    const closeBtn = document.getElementById("close-register-modal");  // 5. 取得關閉註冊視窗按鈕
    const registerForm = document.getElementById("register-form");  // 6. 取得註冊表單
    const loginForm = document.getElementById("login-form");  // 7. 取得登入表單
    const forgotPasswordBtn = document.getElementById("forgot-password-btn");  // 7. 取得忘記帳密表單
    const confirmDeletebtn = document.getElementById("delete-account-btn");  // 7. 取得刪除帳密表單
        
        
          
    // =====  註冊帳號區域 =====
    (() => {
        // 取得 DOM 元素
        const registerBtn = document.getElementById("register-btn");  // 取得註冊按鈕
        const closeBtn = document.getElementById("close-register-modal");  // 取得關閉註冊視窗按鈕
        const registerForm = document.getElementById("register-form");  // 取得註冊表單
        const modalOverlay = document.getElementById("modal-overlay");  // 取得 modal 背景
        const registerModal = document.getElementById("register-modal");  // 取得註冊視窗
        const errorMsg = document.getElementById("register-error-msg");  // 取得錯誤訊息顯示區域
    
        // =====  開啟 & 關閉 註冊視窗 =====
        registerBtn.addEventListener("click", () => {
            modalOverlay.classList.add("active");  // 顯示背景遮罩層
            registerModal.classList.add("active");  // 顯示註冊視窗
        });
    
        function closeRegisterModal() {
            modalOverlay.classList.remove("active");  // 隱藏背景遮罩層
            registerModal.classList.remove("active");  // 隱藏註冊視窗
            errorMsg.innerText = "";  // 清空錯誤訊息
        }
    
        closeBtn.addEventListener("click", closeRegisterModal);
        modalOverlay.addEventListener("click", (event) => {
            if (event.target === modalOverlay) closeRegisterModal();
        });
    
        // =====  註冊表單提交事件 =====
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();  // 防止表單提交後頁面重新整理
    
            // 取得輸入值
            let username = document.getElementById("register-username").value;
            let phrase = document.getElementById("register-password").value;
            let email = document.getElementById("register-email").value;
            let errorMsg = document.getElementById("register-error-msg");

    
            errorMsg.innerText = "";  // 清空錯誤訊息
    
            // 發送註冊請求
             try {
                // 發送 API 請求
                let data = await apiRequest("/auth/register", "POST", { username, phrase, email });
                if (data.error) {
                    // 顯示後端返回的錯誤訊息
                    errorMsg.innerText = data.error;
                    errorMsg.style.color = "red";
                } else {
                    alert("註冊成功！請使用您的帳號登入。");
                    setTimeout(() => window.location.href = "/", 2000);
                }
            } catch (error) {
                console.error("API 錯誤:", error.message);
                errorMsg.innerText = error.message || "發生錯誤，請稍後再試。";
                errorMsg.style.color = "red";
            }
        });
    
        // =====  即時清除錯誤訊息 =====
        ["register-username", "register-password", "register-email"].forEach((id) => {
            document.getElementById(id).addEventListener("input", () => {
                errorMsg.innerText = "";
            });
        });
    
    })();
    
        
        
        
    // =====  登入帳號 =====
    // 42. 登入表單提交事件
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();  // 43. 防止表單提交後頁面重新整理
        
        event.preventDefault();
        
        // 44. 取得使用者輸入的登入資料
        let username = document.getElementById("username").value;  // 45. 取得使用者名稱
        let phrase = document.getElementById("password").value;  // 46. 取得密碼
        let errorMsg = document.getElementById("login-error-msg");
        
        errorMsg.innerText = "";

        // 47. 發送登入請求到後端 /auth/login，這會觸發 auth.py 進行登入驗證
        let data = await apiRequest("/auth/login", "POST", { username, phrase });

        if (data?.token) {  // 48. 如果後端回傳 Token，表示登入成功
            localStorage.setItem("token", data.token);  // 49. 儲存 Token 至 localStorage
            if (data?.token) {  
                localStorage.setItem("token", data.token);
                document.getElementById("user-info").innerText = `歡迎，${data.username}`;// 50. 顯示登入成功訊息
                setTimeout(() => {
                    window.location.href = "/dashboard";  // 51. 轉跳到登入後的頁面（後端會使用 app.py 路由） 
                }, 500);  // 0.5 秒後轉跳
            }
            
        } else if (data?.error) {  // 登入失敗，依據錯誤訊息分別顯示
        
            // 假設後端回傳的 error 為物件 {username: "查無此帳號", password: "密碼錯誤"}
            if (data.error.username) {
                document.getElementById("username-error").innerText = data.error.username;
            }
            if (data.error.password) {
                document.getElementById("password-error").innerText = data.error.password;
            }
            // 若回傳 error 是一般字串，可使用 alert 作為備援
            if (typeof data.error === "string") {
                alert(data.error);
            }
        // =====  即時清除錯誤訊息 =====
        ["register-username", "register-password", "register-email"].forEach((id) => {
            document.getElementById(id).addEventListener("input", () => {
                errorMsg.innerText = "";
            });
        });
    }});
     
    
    // ===== 顯示登入者資訊 =====
    async function fetchUserProfile() {
        let token = localStorage.getItem("token");
        if (!token) return;
    
        let data = await apiRequest("/auth/profile", "GET", null);
        if (data?.username) {
            document.getElementById("user-info").innerHTML = `
                <p>歡迎，${data.username}</p>
                <p>Email: ${data.email}</p>
                <p>角色: ${data.role}</p>
            `;
        }
    }
    
    // 登入成功後執行
    if (localStorage.getItem("token")) {
        fetchUserProfile();
    }
    
        
           
        
    // ===== 忘記密碼功能 =====
    forgotPasswordBtn.addEventListener("click", () => {
        // 建立彈出式小視窗內容
        const forgotPasswordModal = document.createElement("div");
        forgotPasswordModal.innerHTML = `
            <div id="forgot-password-modal" class="modal">
                <div class="modal-content">
                    <span id="close-forgot-password-modal" class="close">&times;</span>
                    <h2>忘記密碼</h2>
                    <form id="forgot-password-form">
                        <label for="forgot-username">帳號：</label>
                        <input type="text" id="forgot-username" placeholder="輸入您的帳號" required>
                        
                        <label for="forgot-email">E-mail：</label>
                        <input type="email" id="forgot-email" placeholder="輸入您的電子郵件" required>
                        
                        <button type="submit" class="btn">送出</button>
                    </form>
                    <p id="forgot-error-msg" class="error-msg"></p>
                </div>
            </div>
        `;
        document.body.appendChild(forgotPasswordModal);
    
        const closeModal = () => {
            forgotPasswordModal.remove(); // 關閉並移除彈出視窗
        };
    
        document.getElementById("close-forgot-password-modal").addEventListener("click", closeModal);
    
        // 表單提交事件
        const forgotPasswordForm = document.getElementById("forgot-password-form");
        forgotPasswordForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const username = document.getElementById("forgot-username").value;
            const email = document.getElementById("forgot-email").value;
            const errorMsg = document.getElementById("forgot-error-msg");
    
            errorMsg.innerText = ""; // 清空錯誤訊息
    
            // 向後端發送忘記密碼請求
            const data = await apiRequest("/auth/reset-password", "POST", { username, email });
    
            if (data?.message) {
                alert(data.message); // 成功訊息（例如：臨時密碼已發送）
                closeModal(); // 成功後自動關閉視窗
            } else if (data?.error) {
                errorMsg.innerText = data.error; // 顯示錯誤訊息
            }
        });
    
        // 點擊視窗外部關閉
        forgotPasswordModal.addEventListener("click", (event) => {
            if (event.target === forgotPasswordModal) closeModal();
        });
    });
    
        
        
    // =====  登出帳號 =====
    // 54. 當點擊登出按鈕時，清除 Token 並重新載入頁面
    document.getElementById("logout-btn")?.addEventListener("click", () => {
        localStorage.removeItem("token");  // 55. 清除 Token
        alert("已登出！");  // 56. 顯示登出成功訊息
        window.location.reload();  // 57. 重新載入頁面
    });
    
    
    // =====  刪除帳號 =====
    // 54. 當點擊刪除帳戶按鈕時，清除後臺帳戶數據，並跳轉回未登入狀態
     if (confirmDeletebtn) {
        confirmDeletebtn.addEventListener("click", async () => {
            let confirmDelete = confirm("確定要刪除帳號？此操作無法復原！");
            if (!confirmDelete) return;
    
            let password = prompt("請輸入密碼以確認刪除帳號：");
            if (!password) return alert("刪除已取消！");
    
            let token = localStorage.getItem("token");
    
            try {
                let response = await fetch("/auth/delete_account", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`,
                    },
                    body: JSON.stringify({ password: password }),
                });
    
                let data = await response.json();
                if (response.ok) {
                    alert("帳號已成功刪除！");
                    localStorage.removeItem("token");
                    window.location.href = "/";
                } else {
                    alert(data.error || "刪除失敗！");
                }
            } catch (error) {
                alert("伺服器錯誤，請稍後再試！");
                console.error(error);
            }
        });
    }
    
    
    // =====  API 請求封裝（避免重複 fetch） =====
    // 8. 定義一個 API 請求的函式
    //async function apiRequest(url, method, bodyData) {
    //    try {
      //      const response = await fetch(url, {  // 9. 發送 API 請求
        //        method: method,  // 10. 設定請求方法（GET, POST, 等）
          //      headers: { "Content-Type": "application/json" },  // 11. 設定標頭，告訴伺服器資料格式為 JSON
            //    body: JSON.stringify(bodyData),  // 12. 將資料轉換為 JSON 格式並放入請求的 body
            //});
            
            
           // const data = await response.json(); // 解析回應 JSON

            
            //if (!response.ok) {  // 13. 檢查回應是否成功
              //  throw new Error(`HTTP 錯誤！狀態碼: ${response.status}`);  // 14. 如果錯誤，拋出異常
    //        }
      //      return data;// 15. 根據回傳質報錯
        //} catch (error) {  // 16. 捕捉異常並處理
       //     console.error("請求失敗:", error);  // 17. 在控制台輸出錯誤訊息
        //    alert("伺服器錯誤，請稍後再試！");  // 18. 彈出錯誤提示
        //}
  //  }    

});
