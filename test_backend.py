import unittest
import sqlite3
import os
import json
import app_backend  # 匯入你的 Flask 後端模組

class BackendTestCase(unittest.TestCase):
    def setUp(self):
        """
        Arrange (準備階段)
        1. 建立測試專用臨時資料庫，確保與正式資料庫隔離
        2. 動態覆寫 (Monkey Patch) 後端的資料庫連線，使測試流量全數導向測試資料庫
        3. 啟動 Flask 測試客戶端 (test_client)
        """
        self.test_db_path = "test_papers.db"
        
        # 確保清理先前的測試殘留檔
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except PermissionError:
                pass

        # 初始化測試資料庫結構
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                authors TEXT,
                publish_date TEXT,
                journal TEXT,
                summary TEXT,
                relevance_score INTEGER,
                tags TEXT,
                url TEXT
            )
        """)
        # 寫入一筆種子資料 (Seed Data) 用於測試讀取與刪除功能
        cursor.execute("""
            INSERT INTO papers (id, title, authors, publish_date, journal, summary, relevance_score, tags, url)
            VALUES (1, 'CRISPR Gene Editing in Agriculture', 'Jennifer A. Doudna', '2026-09-01', 'Nature', 'Summary test', 95, 'Biology;AI', 'http://example.com')
        """)
        conn.commit()
        conn.close()

       # 定義測試專用的資料庫連線產生器，確保 row_factory 有被設定
        def get_test_db_connection():
            conn = sqlite3.connect(self.test_db_path)
            conn.row_factory = sqlite3.Row  # 關鍵：啟用字典型態讀取，與後端對齊
            return conn

        # 動態注入
        self.original_get_db_connection = app_backend.get_db_connection
        app_backend.get_db_connection = get_test_db_connection

        # 啟用 Flask 測試模式
        app_backend.app.config["TESTING"] = True
        self.client = app_backend.app.test_client()

    def tearDown(self):
        """
        Cleanup (清理階段)
        還原後端的原始資料庫連線函式，並實體刪除測試資料庫檔案
        """
        app_backend.get_db_connection = self.original_get_db_connection
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except PermissionError:
                pass

    # ==================== 1. 測試讀取功能 (GET) ====================
    def test_get_papers_success(self):
        """測試 GET /api/papers 是否能正確讀取初始種子資料"""
        # Act (執行)
        response = self.client.get("/api/papers")
        data = json.loads(response.data.decode("utf-8"))

        # Assert (斷言)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[ 0 ]["title"], "CRISPR Gene Editing in Agriculture")

    # ==================== 2. 測試寫入功能 (POST) ====================
    def test_create_paper_success(self):
        """測試 POST /api/papers 正常寫入 (Happy Path)"""
        payload = {
            "title": "Oncology LLM Agent in Clinical Trials",
            "authors": "Frank et al.",
            "journal": "JCO",
            "publishDate": "2026-09-06",
            "relevanceScore": 85,
            "summary": "This is a test summary for LLM agent.",
            "tags": ["AI", "Cancer"],
            "url": "http://clinical-trials-example.com"
        }
        # Act
        response = self.client.post("/api/papers", json=payload)
        data = json.loads(response.data.decode("utf-8"))

        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["title"], "Oncology LLM Agent in Clinical Trials")
        self.assertEqual(data["tags"], ["AI", "Cancer"])

        # 深入資料庫驗證：確認後端確實有將 tags 序列化為分號字串寫入 SQLite
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT tags FROM papers WHERE title = 'Oncology LLM Agent in Clinical Trials'")
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[ 0 ], "AI;Cancer")

    def test_create_paper_validation_error(self):
        """測試 POST /api/papers 防禦驗證：標題空白應回傳 400 (Edge Case)"""
        payload = {
            "title": "   ",  # 測試後端是否有執行 strip() 驗證
            "authors": "No Title Author"
        }
        # Act
        response = self.client.post("/api/papers", json=payload)
        data = json.loads(response.data.decode("utf-8"))

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)
        self.assertIn("文獻標題不可為空", data["error"])

    # ==================== 3. 測試刪除功能 (DELETE) ====================
    def test_delete_paper_success(self):
        """測試 DELETE /api/papers/<id> 正常刪除 (Happy Path)"""
        # Act
        response = self.client.delete("/api/papers/1")
        data = json.loads(response.data.decode("utf-8"))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("刪除成功", data["message"])

        # 深入資料庫驗證：確認資料庫中 ID=1 的資料已不復存在
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM papers WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNone(row)

    def test_delete_paper_not_found(self):
        """測試 DELETE /api/papers/<id> 刪除不存在的 ID (Error Case)"""
        # Act
        response = self.client.delete("/api/papers/999")
        data = json.loads(response.data.decode("utf-8"))

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()