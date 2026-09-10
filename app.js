const API_BASE_URL = 'https://practice-literature-finder.onrender.com';

document.addEventListener('DOMContentLoaded', () => {
    loadPapers();
    setupFormListener();
});

async function loadPapers() {
    const paperList = document.getElementById('paper-list');
    try {
        const response = await fetch(`${API_BASE_URL}/api/papers`);
        if (!response.ok) {
            throw new Error(`HTTP 錯誤狀態碼：${response.status}`);
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

function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * 渲染 6 大目標項目的文獻卡片
 */
function renderPapers(papers) {
    const paperList = document.getElementById('paper-list');
    if (!paperList) return;

    if (papers.length === 0) {
        paperList.innerHTML = '<p>目前尚無文獻紀錄。</p>';
        return;
    }

    paperList.innerHTML = papers.map(paper => {
        const scoreDisplay = paper.relevance_score !== null && paper.relevance_score !== undefined
            ? `${paper.relevance_score} / 10`
            : '未評分';

        return `
            <div class="paper-card" style="border: 1px solid #ccc; padding: 15px; margin-bottom: 15px; border-radius: 5px;">
                <h3>1. 論文名稱：${escapeHtml(paper.title)}</h3>
                <p><strong>2. 作者：</strong>${escapeHtml(paper.authors || '未提供')}</p>
                <p><strong>3. 出版刊物：</strong>${escapeHtml(paper.journal || '未提供')}</p>
                <p><strong>4. 發布日期：</strong>${escapeHtml(paper.pub_date || '未提供')}</p>
                <p><strong>5. (AI判斷)相關度評分：</strong><span class="score-badge" style="color: #2b74c7; font-weight: bold;">${escapeHtml(scoreDisplay)}</span></p>
                <p><strong>6. 研究相關內容 / 摘要：</strong></p>
                <blockquote style="background: #f9f9f9; padding: 10px; border-left: 3px solid #2b74c7; margin: 5px 0;">
                    ${escapeHtml(paper.abstract || '無摘要內文')}
                </blockquote>
                <button class="btn-delete" onclick="deletePaper(${paper.id})">刪除文獻</button>
            </div>
        `;
    }).join('');
}

function setupFormListener() {
    const paperForm = document.getElementById('paper-form');
    if (!paperForm) return;

    paperForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const titleEl = document.getElementById('title');
        const authorsEl = document.getElementById('authors');
        const journalEl = document.getElementById('journal');
        const pubDateEl = document.getElementById('pub_date');
        const scoreEl = document.getElementById('relevance_score');
        const abstractEl = document.getElementById('abstract');

        const rawScore = scoreEl ? scoreEl.value.trim() : '';

        // 完整打包 6 項對應數據
        const payload = {
            title: titleEl ? titleEl.value.trim() : '',
            authors: authorsEl ? authorsEl.value.trim() : '',
            journal: journalEl ? journalEl.value.trim() : '',
            pub_date: pubDateEl ? pubDateEl.value : '',
            relevance_score: rawScore !== '' ? parseFloat(rawScore) : null,
            abstract: abstractEl ? abstractEl.value.trim() : ''
        };

        if (!payload.title) {
            alert('請輸入論文名稱！');
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
                loadPapers();
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

async function deletePaper(paperId) {
    if (!confirm('確定要刪除這筆文獻紀錄嗎？')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/papers/${paperId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('刪除成功！');
            loadPapers();
        } else {
            const errData = await response.json();
            alert('刪除失敗: ' + (errData.error || '伺服器回應錯誤'));
        }
    } catch (error) {
        console.error('刪除文獻時發生錯誤:', error);
        alert('刪除失敗: 無法連線至伺服器');
    }
}