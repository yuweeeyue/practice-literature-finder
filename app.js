// 直接連線至已上線的 Render 雲端後端
const API_BASE_URL = 'https://practice-literature-finder.onrender.com';
 // 預留：雲端部署後的後端網址
// ==================== 狀態管理 (State) ====================
let ALL_PAPERS = [];            // 用來存放從 json 讀取進來的完整資料
let currentKeyword = "";        // 儲存目前輸入的關鍵字
let selectedTag = null;         // 儲存目前選取的單一標籤
let currentSort = "relevance-desc"; // 預設排序條件

// ==================== 數據載入 (Input - Fetch) ====================
async function loadPapersData() {
    try {
        // 將 "papers.json" 修改為 Flask 後端 API 網址
const response = await fetch(`${API_BASE_URL}/api/papers`);
        if (!response.ok) {
            throw new Error(`HTTP 錯誤！狀態碼: ${response.status}`);
        }
        ALL_PAPERS = await response.json();
        
        // 資料讀取成功後，初始化畫面
        renderTagButtons();
        filterAndRender();
    } catch (error) {
        console.error("無法讀取文獻資料庫:", error);
        document.getElementById("papers-container").innerHTML = `
            <p style="color: red; text-align: center; padding: 40px;">
                資料加載失敗：請確認您已啟動後端 API 伺服器 (port 5000)，且是透過本機伺服器 (port 8000) 開啟網頁。
            </p>
        `;
    }
}

// ==================== 渲染與處理邏輯 (Process & Output) ====================

// 動態生成標籤按鈕
function renderTagButtons() {
    const tagsContainer = document.getElementById("tags-filter-container");
    const allTags = new Set();
    ALL_PAPERS.forEach(paper => {
        paper.tags.forEach(tag => allTags.add(tag));
    });

    let tagsHtml = `<button class="tag-btn ${selectedTag === null ? 'active' : ''}" onclick="selectTag(null)">顯示全部</button>`;
    allTags.forEach(tag => {
        const isActive = selectedTag === tag ? 'active' : '';
        tagsHtml += `<button class="tag-btn ${isActive}" onclick="selectTag('${tag}')">${tag}</button>`;
    });

    tagsContainer.innerHTML = tagsHtml;
}

// 切換選取標籤
function selectTag(tag) {
    selectedTag = tag;
    renderTagButtons();
    filterAndRender();
}

// 核心過濾、排序與渲染控制管道
function filterAndRender() {
    let result = [...ALL_PAPERS]; // 複製資料來源

    // A：關鍵字篩選
    if (currentKeyword.trim() !== "") {
        const query = currentKeyword.toLowerCase().trim();
        result = result.filter(paper => {
            return paper.title.toLowerCase().includes(query) || 
                   paper.authors.toLowerCase().includes(query) || 
                   paper.summary.toLowerCase().includes(query);
        });
    }

    // B：標籤篩選
    if (selectedTag !== null) {
        result = result.filter(paper => paper.tags.includes(selectedTag));
    }

    // C：排序處理
    result.sort((a, b) => {
        if (currentSort === "relevance-desc") {
            return b.relevanceScore - a.relevanceScore;
        } else if (currentSort === "relevance-asc") {
            return a.relevanceScore - b.relevanceScore;
        } else if (currentSort === "date-desc") {
            return new Date(b.publishDate) - new Date(a.publishDate);
        } else if (currentSort === "date-asc") {
            return new Date(a.publishDate) - new Date(b.publishDate);
        } else if (currentSort === "title-asc") {
            return a.title.localeCompare(b.title);
        }
        return 0;
    });

    renderPapers(result);
}

// 渲染論文卡片 (已加入刪除按鈕)
function renderPapers(papersArray) {
    const container = document.getElementById("papers-container");
    
    if (papersArray.length === 0) {
        container.innerHTML = `<p style="color: #999; text-align: center; padding: 40px;">找不到符合搜尋條件的結果</p>`;
        return;
    }

    let htmlContent = "";
    papersArray.forEach(paper => {
        const tagsHtml = paper.tags.map(tag => `<span class="tag">${tag}</span>`).join("");

        htmlContent += `
            <div class="paper-card" style="position: relative;">
                <h3 class="paper-title">
                    <a href="${paper.url}" target="_blank">${paper.title}</a>
                </h3>
                <div class="meta-info">
                    作者: ${paper.authors} | 
                    出版日期: ${paper.publishDate} | 
                    期刊: <em>${paper.journal}</em> | 
                    相關度評分: <span class="score">${paper.relevanceScore}%</span>
                </div>
                <p class="summary">${paper.summary}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
                    <div class="tags">${tagsHtml}</div>
                    <!-- 新增：刪除按鈕 -->
                    <button class="delete-btn" onclick="handleDeletePaper(${paper.id})" 
                            style="background: #e53e3e; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: bold; transition: background 0.2s;">
                        刪除文獻
                    </button>
                </div>
            </div>
        `;
    });

    container.innerHTML = htmlContent;
}

// ==================== 事件監聽註冊 ====================
document.addEventListener("DOMContentLoaded", () => {
    // 啟動非同步資料載入
    loadPapersData();

    // 監聽搜尋按鈕點擊
    document.getElementById("search-btn").addEventListener("click", () => {
        currentKeyword = document.getElementById("search-input").value;
        filterAndRender();
    });

    // 監聽輸入框 Enter 鍵
    document.getElementById("search-input").addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            currentKeyword = document.getElementById("search-input").value;
            filterAndRender();
        }
    });

    // 監聽排序下拉選單
    document.getElementById("sort-select").addEventListener("change", (e) => {
        currentSort = e.target.value;
        filterAndRender();
    });
});
document.addEventListener("DOMContentLoaded", () => {
    // ... 原有的 DOM 載入與監聽代碼 ...
// 範例：新增文獻表單送出事件
const paperForm = document.getElementById('paper-form');
paperForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    // ... 原本的新增邏輯 ...
});
document.getElementById('paper-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    // 1. 讀取表單輸入值
    const titleInput = document.getElementById('title');
    const authorsInput = document.getElementById('authors');
    const abstractInput = document.getElementById('abstract');

    // 2. 打包成 payload 物件（關鍵：必須先宣告變數）
    const titleEl = document.getElementById('title');
    const authorsEl = document.getElementById('authors');
    const abstractEl = document.getElementById('abstract');

    try {
        // 3. 發送請求至雲端 API
        const response = await fetch(`${API_BASE_URL}/api/papers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert('新增成功！');
            titleInput.value = ''; // 清空表單
            loadPapers();         // 重新讀取清單
        } else {
            const errData = await response.json();
            alert('新增失敗: ' + (errData.error || '未知錯誤'));
        }
    } catch (error) {
        console.error('新增失敗:', error);
        alert('新增失敗: ' + error.message);
    }
});
    // 註冊表單提交事件監聽器
    const addForm = document.getElementById("add-paper-form");
    if (addForm) {
        addForm.addEventListener("submit", handleAddPaper);
    }
});
// ==================== 新增文獻處理 (Create - POST) ====================
async function handleAddPaper(event) {
    event.preventDefault(); // 1. 攔截預設表單提交，防止網頁重新整理

    // 2. Input: 蒐集表單輸入值
    const title = document.getElementById("form-title").value.trim();
    const authors = document.getElementById("form-authors").value.trim();
    const journal = document.getElementById("form-journal").value.trim();
    const publishDate = document.getElementById("form-date").value;
    const relevanceScore = document.getElementById("form-score").value;
    const summary = document.getElementById("form-summary").value.trim();
    const url = document.getElementById("form-url").value.trim();
    
    // 解析標籤字串為陣列
    const tagsInput = document.getElementById("form-tags").value.trim();
    const tags = tagsInput ? tagsInput.split(";").map(t => t.trim()).filter(t => t !== "") : [];

    // 建立請求酬載 (Payload)
    const requestBody = {
        title,
        authors,
        journal,
        publishDate: publishDate || new Date().toISOString().split('T')[ 0 ], // 若未填則預設今日
        relevanceScore: relevanceScore ? parseInt(relevanceScore) : 70,
        summary,
        tags,
        url: url || "#"
    };

    // 3. Process: 發送 POST 請求至 Flask API
    try {
        const response = await fetch(`${API_BASE_URL}/api/papers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
});

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP 錯誤！狀態碼: ${response.status}`);
        }

        const newPaper = await response.json();

        // 4. Output: 更新前端 State 並驅動管道渲染，表單重設歸零
        ALL_PAPERS.push(newPaper);
        filterAndRender(); // 呼叫統一過濾與排序管線，網頁不重新整理，新卡片立即在前端呈顯

        event.target.reset(); // 重置表單欄位
        alert("✓ 文獻新增成功，已同步寫入 SQLite 資料庫！");

    } catch (error) {
        console.error("新增文獻時發生錯誤:", error);
        alert(`新增失敗: ${error.message}`);
    }
}
// ==================== 刪除文獻處理 (Delete - DELETE) ====================
async function handleDeletePaper(id) {
    // 1. 安全防範：執行二次確認，防止使用者誤觸
    const confirmDelete = confirm("⚠️ 您確定要將此文獻從數據庫中永久刪除嗎？此操作無法還原。");
    if (!confirmDelete) return;

    // 2. Process: 發送 DELETE 請求至 Flask API
    try {
       const response = await fetch(`${API_BASE_URL}/api/papers/${id}`, {
    method: 'DELETE'
});
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP 錯誤！狀態碼: ${response.status}`);
        }

        // 3. Output: 狀態同步 (State Sync)
        // 從前端記憶體陣列中過濾掉被刪除的資料
        ALL_PAPERS = ALL_PAPERS.filter(paper => paper.id !== id);
        
        // 重新執行統一渲染管道，卡片會瞬間從畫面上消失，無需重新整理網頁
        filterAndRender();
        alert("✓ 文獻已成功從 SQLite 資料庫中刪除！");

    } catch (error) {
        console.error("刪除文獻時發生錯誤:", error);
        alert(`刪除失敗: ${error.message}`);
    }
}