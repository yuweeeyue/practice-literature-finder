// 指向 Render 實體公開後端網址
const API_BASE_URL = 'https://practice-literature-finder.onrender.com';

// 頁面 DOM 載入完成後進行初始化
document.addEventListener('DOMContentLoaded', () => {
    loadPapers();
    setupFormListener();
});

/**
 * 1. 讀取文獻清單 (GET)
 */
async function loadPapers() {
    const paperList = document.getElementById('paper-list');
    try {
        const response = await fetch(`${API_BASE_URL}/api/papers`);
        if (!response.ok) {
            throw new Error(`HTTP 錯誤，狀態碼：${response.status}`);
        }
        const papers = await response.json();
        renderPapers(papers);
    } catch (error) {
        console.error('載入文獻失敗:', error);
        if (paperList) {
            paperList.innerHTML = `<p class="error-msg">資料加載失敗，請確認 API 伺服器正常運作。</p>`;
        }
    }
}

/**
 * 渲染文獻資料至網頁 DOM (包含刪除按鈕)
 */
function renderPapers(papers) {
    const paperList = document.getElementById('paper-list');
    if (!paperList) return;

    if (papers.length === 0) {
        paperList.innerHTML = '<p>目前尚無文獻紀錄。</p>';
        return;
    }

    paperList.innerHTML = papers.map(paper => `
        <div class="paper-card">
            <h3>${escapeHtml(paper.title)}</h3>
            <p><strong>作者：</strong>${escapeHtml(paper.authors || '未提供')}</p>
            <p><strong>摘要：</strong>${escapeHtml(paper.abstract || '無摘要')}</p>
            <button class="btn-delete" onclick="deletePaper(${paper.id})">刪除</button>
        </div>
    `).join('');
}

/**
 * 3. 發送刪除文獻請求 (DELETE)
 */
async function deletePaper(paperId) {
    if (!confirm('確定要刪除這筆文獻紀錄嗎？')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/papers/${paperId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('刪除成功！');
            loadPapers(); // 重新整理清單
        } else {
            const errData = await response.json();
            alert('刪除失敗: ' + (errData.error || '伺服器回應錯誤'));
        }
    } catch (error) {
        console.error('刪除文獻時發生錯誤:', error);
        alert('刪除失敗: 無法連線至伺服器');
    }
}

/**
 * 2. 繫結新增表單送出事件 (POST)
 */
function setupFormListener() {
    // 於全域僅宣告一次 paperForm
    const paperForm = document.getElementById('paper-form');
    if (!paperForm) {
        console.warn("未在 DOM 中找到 id='paper-form' 的表單元素");
        return;
    }

    paperForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // 阻擋 HTML 原生 GET 刷頁

        const titleEl = document.getElementById('title');
        const authorsEl = document.getElementById('authors');
        const abstractEl = document.getElementById('abstract');

        // 安全封裝 payload 物件
        const payload = {
            title: titleEl ? titleEl.value.trim() : '',
            authors: authorsEl ? authorsEl.value.trim() : '',
            abstract: abstractEl ? abstractEl.value.trim() : ''
        };

        if (!payload.title) {
            alert('請輸入文獻標題！');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/papers`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert('文獻新增成功！');
                paperForm.reset();
                loadPapers(); // 重新載入列表
            } else {
                const errData = await response.json();
                alert('新增失敗: ' + (errData.error || '伺服器回應錯誤'));
            }
        } catch (error) {
            console.error('新增文獻時發生錯誤:', error);
            alert('新增失敗: 無法連線至伺服器');
        }
    });
}
