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
    # 建立完整的文獻資料表結構
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
    
    # 防禦機制：自動替既有資料庫補充新新增的欄位
    existing_cols = [row[4] for row in cursor.execute("PRAGMA table_info(papers)").fetchall()]
    if "journal" not in existing_cols:
        cursor.execute("ALTER TABLE papers ADD COLUMN journal TEXT")
    if "pub_date" not in existing_cols:
        cursor.execute("ALTER TABLE papers ADD COLUMN pub_date TEXT")
        
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