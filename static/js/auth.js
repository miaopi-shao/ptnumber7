//避免 replaceWith()，改用 removeEventListener() + addEventListener()
//每個 JS 檔案的程式碼封裝在 (() => {...})() 立即執行函式（IIFE）裡

// 定義 apiRequest的運行邏輯
async function apiRequest(endpoint, method, body) {
    const token = localStorage.getItem("token"); // 確保正確取得 token
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : null,
    };
    console.log("註冊請求 Body:", JSON.stringify({ username, password, email }));
    console.log("JSON.stringify(body):", JSON.stringify(body));
    console.log("API 請求 Headers:", options.headers);
    console.log("API 請求 Body:", options.body);
    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`; // 加入 Authorization 標頭
    }
    try {
        const response = await fetch(endpoint, options);
        
        if (!response.ok) {
            let errorMessage = `HTTP 錯誤！狀態碼: ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (parseError) {
                console.error("無法解析伺服器回應：", parseError.message);
            }
            throw new Error(errorMessage);
        }
        return await response.json();
    } catch (error) {
        if (error.message.includes("Failed to fetch")) {
            console.error("API 錯誤：伺服器無法連接或跨域問題。");
            throw new Error("無法連接伺服器，請檢查網路連線或跨域設置。");
        } else {
            console.error("API 請求錯誤:", error.message);
            throw error; // 傳遞原始錯誤
        }
    }
}


document.addEventListener('DOMContentLoaded', () => {  // 1. 包裹成立即執行函式（IIFE），避免全域變數污染

    // 檢查使用者登入狀態
    async function fetchUserProfile() {
        console.log("初始化用戶資訊加載...");
    
        try {
            // 驗證並獲取用戶資訊
            let data = await apiRequest("/auth/profile", "GET");
    
            console.log("個人資訊回應:", data); // 確認回應方便調試
    
            // 確保 DOM 中的 `account-info` 區域存在
            let userInfoElement = document.getElementById("account-info") || (() => {
                const element = document.createElement("div");
                element.id = "account-info";
                document.body.appendChild(element);
                return element;
            })();
    
            userInfoElement.innerHTML = `
                <p>歡迎，${data.username}</p>
                <p>Email: ${data.email}</p>
                <p>角色: ${data.role}</p>
            `;
        } catch (error) {
            console.error("獲取用戶資訊失敗:", error.message);
            alert("無法獲取用戶資訊，請稍後再試！");
        }

    }
    
    // API 請求封裝函數
    async function apiRequest(endpoint, method, options = {}) {
        const token = localStorage.getItem("token"); // 確保正確取得 token
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers, // 合併自定義 headers
        };
        if (token) {
            headers["Authorization"] = `Bearer ${token}`; // 添加 Authorization 標頭
        }
    
        console.log("發送請求到:", endpoint);
        console.log("附帶標頭:", headers);
    
        try {
            const response = await fetch(endpoint, {
                method: method,
                headers: headers,
                body: options.body ? JSON.stringify(options.body) : null,
            });
            
            if (response.status === 401) {
                alert("您的登入已過期，請重新登入！");
                window.location.href = "/login";
                return; // 提前退出，避免繼續處理錯誤
            }
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP 錯誤！狀態碼: ${response.status}`);
            }
    
            return await response.json();
        } catch (error) {
            console.error("API 請求錯誤:", error.message);
            throw error; // 傳遞原始錯誤
        }
    }
    
    // 當頁面加載完成後初始化用戶資訊
    document.addEventListener("DOMContentLoaded", () => {
        fetchUserProfile();
    });
    
    // 取得 DOM 元素
    const modalOverlay = document.getElementById("modal-overlay");  // 2. 取得 modal 背景
    const loginForm = document.getElementById("login-form");  // 7. 取得登入表單
    const forgotPasswordBtn = document.getElementById("forgot-password-btn");  // 7. 取得忘記帳密表單
    const confirmDeletebtn = document.getElementById("delete-account-btn");  // 7. 取得刪除帳密表單
         
    // ===== 登入帳號 =====
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault(); // 防止表單提交後頁面重新整理
    
        let username = document.getElementById("username").value.trim();
        let password = document.getElementById("password").value.trim();
    
        // 檢查是否有輸入帳號和密碼
        if (!username || !password) {
            if (!username) usernameError.innerText = "請輸入使用者名稱！";
            if (!password) passwordError.innerText = "請輸入密碼！";
            generalError.innerText = "";
            return;
        }
    
        try {
            // 發送登入請求
            let data = await apiRequest("/auth/login", "POST", {
                body: { username, password: password } // 正確封裝 Body
            });
            console.log("後端回應資訊:", data); // 打印 data 檢查內容是否包含 token
    
            if (data?.token) {
                // 存儲 Token
                localStorage.setItem("token", data.token);
                console.log("存入的 Token:", localStorage.getItem("token"));
    
                if (data?.username) {
                    let accountInfoElement = document.getElementById("account-info");
    
                    if (!accountInfoElement) {
                        console.warn("'account-info' 不存在，動態創建！");
                        accountInfoElement = document.createElement("div");
                        accountInfoElement.id = "account-info";
                        document.body.appendChild(accountInfoElement); // 動態添加到頁面
                    }
    
                    accountInfoElement.innerText = `歡迎，${data.username}`;
                }
                // 顯示提示框後刷新頁面
                alert("登入成功！即將重新加載頁面。");
                setTimeout(() => {
                    console.log("正在重新加載頁面...");
                    window.location.reload(); // 刷新頁面來渲染後端模板
                }, 2000);
            } else if (data?.error) {
                // 處理錯誤訊息
                const usernameError = document.getElementById("username-error");
                const passwordError = document.getElementById("password-error");
                const generalError = document.getElementById("general-error");
                // 清除錯誤訊息
                usernameError.innerText = "";
                passwordError.innerText = "";
                if (data.error === "未找到該使用者") {
                    usernameError.innerText = data.error;
                } else {
                    generalError.innerText = data.error;
                }
            }
        } catch (error) {
            console.error("登入請求失敗:", error.message);
        
            // 顯示錯誤訊息到指定區域，而不是彈出視窗
            const generalError = document.getElementById("general-error");
            if (generalError) {
                generalError.innerText = error.message;
            }
        }
    });

     
    

    
        
           
              
    
    
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
            let password = document.getElementById("register-password").value;
            let email = document.getElementById("register-email").value;
            let errorMsg = document.getElementById("register-error-msg");
            
            console.log("使用者名稱:", username);
            console.log("密碼:", password);
            console.log("電子郵件:", email);

            
            errorMsg.innerText = "";  // 清空錯誤訊息
            
            // ===== 驗證輸入值是否完整 =====
            if (!username || !password || !email) {  // 核心邏輯在這裡
                errorMsg.innerText = "請填寫完整資訊！";
                errorMsg.style.color = "red";
                return;  // 停止後續處理
            }
            
            // 發送註冊請求
             try {
                // 發送 API 請求
                let data = await apiRequest("/auth/register", "POST", { username, password, email });
                if (data.error) {
                    // 顯示後端返回的錯誤訊息
                    errorMsg.innerText = data.error;
                    errorMsg.style.color = "red";
                } else {
                    alert("註冊成功！請使用您的帳號登入。");
                    setTimeout(() => window.location.href = "/", 2000);
                }
            } catch (error) {
                if (error.message.includes("Failed to fetch")) {
                    errorMsg.innerText = "無法連接伺服器，請檢查網絡連線。";
                } else {
                    errorMsg.innerText = error.message || "發生未知錯誤，請稍後再試。";
                }
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
});  
    
