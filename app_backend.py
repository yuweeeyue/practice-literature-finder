from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# 啟用 CORS 允許前端網頁（通常在 port 8000）跨網域請求此 API（port 5000）
CORS(app)

DB_FILE = "papers.db"

def get_db_connection():
    """建立資料庫連線，並設定 row_factory 讓查詢結果可以直接轉成字典格式"""
    conn = sqlite3.connect(DB_FILE)
    # 這行是關鍵：預設 sqlite3 回傳 tuple，設定這行後會回傳類似 dict 的 Row 物件
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

if __name__ == "__main__":
    # 預設執行在 http://127.0.0.1:5000
    # 若 5000 埠口被佔用，可手動修改 port=5001
    app.run(debug=True, port=5000)