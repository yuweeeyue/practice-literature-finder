const API_BASE_URL = 'http://127.0.0.1:5000'; // 本機測試，若部署 Render 改為網域網址

document.addEventListener('DOMContentLoaded', () => {
    loadPapers();
    setupFormListener();
    setupAIAnalyzeListener();
});

async function loadPapers() {
    const paperList = document.getElementById('paper-list');
    try {
        const response = await fetch(`${API_BASE_URL}/api/papers`);
        if (!response.ok) throw new Error(`HTTP 狀態碼：${response.status}`);
        const papers = await response.json();
        renderPapers(papers);
    } catch (error) {
        console.error('載入文獻失敗:', error);
        if (paperList) paperList.innerHTML = `<p style="color: red;">資料加載失敗，請確認後端服務已啟動。</p>`;
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
            <div class="paper-card">
                <h3>1. 論文名稱：${escapeHtml(paper.title)}</h3>
                <p><strong>2. 作者：</strong>${escapeHtml(paper.authors || '未提供')}</p>
                <p><strong>3. 出版刊物：</strong>${escapeHtml(paper.journal || '未提供')}</p>
                <p><strong>4. 發布日期：</strong>${escapeHtml(paper.pub_date || '未提供')}</p>
                <p><strong>5. (AI判斷)相關度評分：</strong><span style="color: #28a745; font-weight: bold;">${escapeHtml(scoreDisplay)}</span></p>
                <p><strong>6. 研究相關內容 / 摘要：</strong></p>
                <blockquote style="background: #f8f9fa; padding: 10px; border-left: 4px solid #007bff; margin: 5px 0;">
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

        const rawScore = document.getElementById('relevance_score').value.trim();
        const payload = {
            title: document.getElementById('title').value.trim(),
            authors: document.getElementById('authors').value.trim(),
            journal: document.getElementById('journal').value.trim(),
            pub_date: document.getElementById('pub_date').value,
            relevance_score: rawScore !== '' ? parseFloat(rawScore) : null,
            abstract: document.getElementById('abstract').value.trim()
        };

        try {
            const response = await fetch(`${API_BASE_URL}/api/papers`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
            alert('新增失敗: 無法連線至伺服器');
        }
    });
}

function setupAIAnalyzeListener() {
    const aiBtn = document.getElementById('btn-ai-analyze');
    const loadingStatus = document.getElementById('ai-loading-status');

    if (!aiBtn) return;

    aiBtn.addEventListener('click', async () => {
        const title = document.getElementById('title').value.trim();
        const abstract = document.getElementById('abstract').value.trim();

        if (!title) {
            alert('請先輸入「論文名稱」再進行 AI 分析！');
            return;
        }

        aiBtn.disabled = true;
        if (loadingStatus) loadingStatus.style.display = 'inline';

        try {
            const response = await fetch(`${API_BASE_URL}/api/papers/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, abstract })
            });

            const data = await response.json();

            if (response.ok) {
                if (data.relevance_score !== undefined) {
                    document.getElementById('relevance_score').value = data.relevance_score;
                }
                if (data.ai_summary) {
                    document.getElementById('abstract').value = data.ai_summary;
                }
                alert('AI 分析完成！已自動填入相關度評分與摘要。');
            } else {
                alert('AI 分析失敗: ' + (data.error || '未知錯誤'));
            }
        } catch (error) {
            alert('分析失敗: 無法連線至伺服器');
        } finally {
            aiBtn.disabled = false;
            if (loadingStatus) loadingStatus.style.display = 'none';
        }
    });
}

async function deletePaper(paperId) {
    if (!confirm('確定要刪除這筆文獻紀錄嗎？')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/papers/${paperId}`, { method: 'DELETE' });
        if (response.ok) {
            alert('刪除成功！');
            loadPapers();
        } else {
            alert('刪除失敗');
        }
    } catch (error) {
        alert('刪除失敗: 無法連線至伺服器');
    }
}