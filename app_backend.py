import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# CORS 配置：允許前端來源存取 API
frontend_url = os.environ.get("FRONTEND_URL", "*")
CORS(app, resources={r"/api/*": {"origins": [frontend_url, "http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:5000"]}})

def get_db_connection():
    db_path = os.environ.get("DATABASE_PATH", "papers.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            authors TEXT,
            abstract TEXT,
            relevance_score REAL,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 啟動時自動初始化資料庫
init_db()

# 1. 讀取文獻清單 (GET)
@app.route("/api/papers", methods=["GET"])
def get_papers():
    try:
        conn = get_db_connection()
        papers = conn.execute("SELECT * FROM papers ORDER BY created_at DESC").fetchall()
        conn.close()
        return jsonify([dict(row) for row in papers]), 200
    except Exception as e:
        if "no such table" in str(e):
            init_db()
            return jsonify([]), 200
        return jsonify({"error": str(e)}), 500

# 2. 新增文獻資料 (POST)
@app.route("/api/papers", methods=["POST"])
def add_paper():
    data = request.get_json()
    if not data or not data.get("title", "").strip():
        return jsonify({"error": "Title is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO papers (title, authors, abstract) VALUES (?, ?, ?)",
            (data.get("title").strip(), data.get("authors", ""), data.get("abstract", ""))
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"message": "Paper created successfully", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. 刪除文獻資料 (DELETE) - 全域僅能宣告一次 delete_paper 函式
@app.route("/api/papers/<int:paper_id>", methods=["DELETE"])
def delete_paper(paper_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
        conn.commit()
        deleted_rows = cursor.rowcount
        conn.close()

        if deleted_rows == 0:
            return jsonify({"error": "Paper not found"}), 404

        return jsonify({"message": "Paper deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)