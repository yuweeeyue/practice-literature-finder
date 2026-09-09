from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
# 從環境變數讀取前端允許網域，本機開發時提供預設備用網址
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
    # 3. 刪除文獻資料 (DELETE)
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
    
        # 安全處理評分 (防範非整數型態資料傳入)
        try:
            relevance_score = int(data.get("relevanceScore", 70))
        except (ValueError, TypeError):
            relevance_score = 70

        # 使用「參數化查詢」寫入資料庫，防止 SQL 注入
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO papers (title, authors, publish_date, journal, summary, relevance_score, tags, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(insert_query, (
            title, authors, publish_date, journal, summary, relevance_score, tags_str, url
        ))
        conn.commit()
        
        # 取得自動生成的 Primary Key ID
        new_id = cursor.lastrowid
        
        # 3. Output: 封裝新增成功的物件，回傳 HTTP 201 Created
        new_paper = {
            "id": new_id,
            "title": title,
            "authors": authors,
            "publishDate": publish_date,
            "journal": journal,
            "summary": summary,
            "relevanceScore": relevance_score,
            "tags": tags_list,
            "url": url if url else "#"
        }
        return jsonify(new_paper), 201

    except Exception as e:
        return jsonify({"error": f"伺服器內部錯誤: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

@app.route("/api/papers/<int:paper_id>", methods=["DELETE", "OPTIONS"])
def delete_paper(paper_id):
    # 1. 優先處理 CORS 預檢請求：若收到 OPTIONS 請求，直接回傳 200 OK 釋放通道
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
        
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 2. 檢查資料是否存在
        cursor.execute("SELECT id FROM papers WHERE id = ?", (paper_id,))
        if not cursor.fetchone():
            return jsonify({"error": "資料不存在或已被刪除"}), 404
            
        # 3. 執行參數化刪除
        cursor.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
        conn.commit()
        
        return jsonify({"message": f"文獻 ID {paper_id} 刪除成功"}), 200

    except Exception as e:
        return jsonify({"error": f"伺服器內部錯誤: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)