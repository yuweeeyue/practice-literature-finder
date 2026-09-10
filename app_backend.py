import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

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
    
    # 1. 建立資料表基礎結構（若資料庫不存在時執行）
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
    
    # 2. 動態檢查並補充欄位（若欄位已存在則忽略錯誤，避免崩潰）
    new_columns = [("journal", "TEXT"), ("pub_date", "TEXT")]
    for col_name, col_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE papers ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            # 當欄位已存在時，SQLite 會拋出 OperationalError，此處直接跳過
            pass
        
    conn.commit()
    conn.close()

init_db()

@app.route("/api/papers", methods=["GET"])
def get_papers():
    try:
        conn = get_db_connection()
        papers = conn.execute("SELECT * FROM papers ORDER BY created_at DESC").fetchall()
        conn.close()
        return jsonify([dict(row) for row in papers]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/papers", methods=["POST"])
def add_paper():
    data = request.get_json()
    if not data or not data.get("title", "").strip():
        return jsonify({"error": "Title is required"}), 400

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
        return jsonify({"message": "Paper created successfully", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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