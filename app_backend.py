from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
# 從環境變數讀取前端允許網域，本機開發時提供預設備用網址
frontend_url = os.environ.get("FRONTEND_URL", "*")

CORS(app, resources={
    r"/api/*": {
        "origins": [
            frontend_url,
            "http://127.0.0.1:5500",  # Live Server 預設埠號
            "http://localhost:5500",
            "http://127.0.0.1:5000"
        ]
    }
})

DB_FILE = "papers.db"

def get_db_connection():
    """單純負責建立並回傳資料庫連線（絕對不要在此呼叫 init_db）"""
    db_path = os.environ.get("DATABASE_PATH", "papers.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    """單向呼叫 get_db_connection() 建立資料表"""
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

    # 在應用程式載入時立即執行資料庫初始化
    init_db()
    # 優先讀取環境變數中的資料庫路徑，若無則預設為 "papers.db"
    db_path = os.environ.get("DATABASE_PATH", "papers.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# 定義 API 路由路徑
@app.route("/api/papers", methods=["GET"])
def get_papers():
    conn = None
    try:
        # 1. Input: 接收請求並建立資料庫連線
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 2. Process: 執行 SQL 查詢撈取所有文獻
        cursor.execute("SELECT * FROM papers")
        rows = cursor.fetchall()
        
        # 將 Row 物件轉換成 Python 的 List of Dicts
        papers_list = []
        for row in rows:
            # 轉換 tags 字串回到 list 格式以契合前端原有的渲染邏輯
            tags_str = row["tags"]
            tags_list = [tag.strip() for tag in tags_str.split(";")] if tags_str else []
            
            papers_list.append({
                "id": row["id"],
                "title": row["title"],
                "authors": row["authors"],
                "publishDate": row["publish_date"],
                "journal": row["journal"],
                "summary": row["summary"],
                "relevanceScore": row["relevance_score"],
                "tags": tags_list,
                "url": row["url"]
            })
            
        # 3. Output: 回傳標準 JSON 格式與 HTTP 200 狀態碼
        return jsonify(papers_list), 200

    except Exception as e:
        # 異常處理：若發生錯誤回傳 500 錯誤狀態碼
        return jsonify({"error": str(e)}), 500
        
    finally:
        if conn:
            conn.close()
@app.route("/api/papers", methods=["POST"])
def add_paper():
    conn = None
    try:
        # 1. Input: 接收前端傳入的 JSON 資料
        data = request.get_json()
        if not data:
            return jsonify({"error": "請求格式錯誤，必須提供 JSON 資料"}), 400
        
        title = data.get("title", "").strip()
        authors = data.get("authors", "").strip()
        journal = data.get("journal", "").strip()
        publish_date = data.get("publishDate", "").strip()
        summary = data.get("summary", "").strip()
        url = data.get("url", "").strip()
        
        # 2. Process: 後端防禦性資料驗證 (Defensive Validation)
        if not title:
            return jsonify({"error": "資料驗證失敗：文獻標題不可為空"}), 400
            
        # 轉換標籤陣列 -> 以分號分隔的字串，以符合 SQLite 欄位設計
        tags_list = data.get("tags", [])
        tags_str = ";".join([tag.strip() for tag in tags_list if tag.strip()])
        
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
    # 讀取環境變數中的 PORT，並轉為整數，預設為 5000
    server_port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=server_port)