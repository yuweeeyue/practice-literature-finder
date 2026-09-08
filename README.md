# Literature Finder 🧬 × 💻

一個專為生醫研究人員設計的**輕量級文獻探索與管理系統**。本專案整合了前端互動介面、Flask 後端 API 與 SQLite 關聯式資料庫，實現端到端的文獻 CRUD（新增、讀取、刪除）數據流。

---

## 📌 專案背景與痛點解決 (Problem & Business Value)
生醫領域研究員每天需面對海量文獻。傳統文獻管理工具（如 EndNote）功能繁複且不易與自定義的 AI 評估工作流整合。
本專案解決以下核心痛點：
- **效率低下**：提供直覺式前端介面，可快速登錄並篩選關鍵文獻。
- **評估指標量化**：引入「相關性評估（Relevance Score）」與「自定義標籤（Tags）」，便於研究人員快速篩選高價值文獻。
- **資料安全與本地化**：基於 SQLite 本地資料庫，確保敏感未發表研究數據不外洩。

---

## 🛠️ 技術棧與架構 (System Architecture)
本系統依循 **Input → Process → Output (IPO)** 設計模型，確保各模組責任邊界清晰：
- **前端 (UI Layer)**：原生 HTML5 / CSS3 (響應式設計) / JavaScript (ES6 Fetch API)
- **後端 (API Layer)**：Flask (Python 3.12) - 提供參數化防禦性驗證及 RESTful API 路由
- **資料庫 (Data Layer)**：SQLite3 - 關聯式資料儲存，並使用參數化查詢防範 SQL 注入攻擊

### 🔄 數據流向 (Data Flow)
`使用者輸入 (前端表單) ➔ JSON 封裝 ➔ POST 請求 ➔ Flask 驗證 ➔ 參數化 SQL ➔ SQLite 儲存`

---

## 🚀 快速啟動與環境建置 (How to Reproduce)

### 1. 複製專案
```bash
git clone <你的 GitHub 專案網址>
cd literature-finder
2. 環境配置
本專案使用 Python 內建的 venv 進行虛擬環境隔離。
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境 (Windows)
.\venv\Scripts\activate

# 啟動虛擬環境 (Mac/Linux)
source venv/bin/activate

# 安裝依賴套件
pip install -r requirements.txt
3. 環境變數設定
請拷貝配置範本並建立本地 .env 檔案（本機專用，已被 Git 忽略）：
cp .env.example .env
確保 .env 中的 DATABASE_PATH 設為 papers.db。
4. 啟動後端伺服器
python app_backend.py
預設將啟動於：http://127.0.0.1:5000
5. 啟動前端網頁
你可以使用 VS Code 的 Live Server 套件開啟 index.html，或直接雙擊檔案於瀏覽器中執行。