import os
import sqlite3
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# 1. 載入本機環境變數
load_dotenv()

app = Flask(__name__)

# 2. 配置 CORS 跨域存取
frontend_url = os.environ.get("FRONTEND_URL", "*")
CORS(app, resources={
    r"/api/*": {
        "origins": [
            frontend_url,
            "http://127.0.0.1:5500",
            "http://localhost:5500",
            "http://127.0.0.1:5000"
        ]
    }
})

def get_db_connection():
    """建立 SQLite 資料庫連線並轉為字典結構"""
    db_path = os.environ.get("DATABASE_PATH", "papers.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化資料庫並進行安全性欄位動態擴充"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            authors TEXT,
            journal TEXT,
            pub_date TEXT,
            abstract TEXT,
            relevance_score REAL,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 防禦性擴充：自動補齊可能缺失的資料欄位
    for col_name, col_type in [("journal", "TEXT"), ("pub_date", "TEXT")]:
        try:
            cursor.execute(f"ALTER TABLE papers ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass # 欄位已存在則自動跳過
        
    conn.commit()
    conn.close()

init_db()

# ==================== API 路由設計 ====================

@app.route("/api/papers", methods=["GET"])
def get_papers():
    """取得所有文獻清單"""
    try:
        conn = get_db_connection()
        papers = conn.execute("SELECT * FROM papers ORDER BY created_at DESC").fetchall()
        conn.close()
        return jsonify([dict(row) for row in papers]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/papers", methods=["POST"])
def add_paper():
    """新增單筆文獻"""
    data = request.get_json()
    if not data or not data.get("title", "").strip():
        return jsonify({"error": "論文名稱為必填項目！"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO papers 
               (title, authors, journal, pub_date, abstract, relevance_score) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                data.get("title", "").strip(),
                data.get("authors", "").strip(),
                data.get("journal", "").strip(),
                data.get("pub_date", "").strip(),
                data.get("abstract", "").strip(),
                data.get("relevance_score", None)
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"message": "新增成功", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/papers/<int:paper_id>", methods=["DELETE"])
def delete_paper(paper_id):
    """刪除特定文獻"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
        conn.commit()
        deleted_rows = cursor.rowcount
        conn.close()

        if deleted_rows == 0:
            return jsonify({"error": "找不到該筆文獻"}), 404

        return jsonify({"message": "刪除成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/papers/analyze", methods=["POST"])
def analyze_paper():
    """呼叫 Gemini API 進行 AI 結構化分析與自動評分"""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        return jsonify({"error": "未設定 GEMINI_API_KEY 金鑰"}), 500

    data = request.get_json()
    title = data.get("title", "").strip() if data else ""
    abstract = data.get("abstract", "").strip() if data else ""

    if not title:
        return jsonify({"error": "分析需提供論文名稱！"}), 400

    prompt = f"""你是一位專業的生醫與 AI 領域文獻審查專家。
請分析以下論文標題與摘要內容，評估其與「生醫科技 (Biology) × 人工智慧 (AI) × 商業應用 (Business)」的跨域相關度分數（0.0 至 10.0 分），並生成一段 100 字以內的精準核心摘要。

論文標題：{title}
論文摘要：{abstract if abstract else "無提供摘要"}

請嚴格輸出純 JSON 格式，格式如下：
{{
    "relevance_score": 8.5,
    "ai_summary": "精簡後的繁體中文核心摘要內容..."
}}
"""

    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return jsonify(json.loads(response.text)), 200
    except Exception as e:
        return jsonify({"error": f"AI 分析失敗: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)