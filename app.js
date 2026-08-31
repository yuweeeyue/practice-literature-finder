// ==================== 狀態管理 (State) ====================
let ALL_PAPERS = [];            // 用來存放從 json 讀取進來的完整資料
let currentKeyword = "";        // 儲存目前輸入的關鍵字
let selectedTag = null;         // 儲存目前選取的單一標籤
let currentSort = "relevance-desc"; // 預設排序條件

// ==================== 數據載入 (Input - Fetch) ====================
async function loadPapersData() {
    try {
        // 唯一修改點：將 "papers.json" 改為 Flask 後端 API 網址
        const response = await fetch("http://127.0.0.1:5000/api/papers");
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

// 渲染論文卡片
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
            <div class="paper-card">
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
                <div class="tags">${tagsHtml}</div>
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