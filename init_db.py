import sqlite3
import csv
import os

DB_FILE = "papers.db"
CSV_FILE = "papers_raw.csv"

def init_database():
    # 建立或連線到 SQLite 資料庫檔案
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Process: 建立符合規格的資料表 (Schema) [3]
    # 使用 AUTOINCREMENT 讓 ID 自動遞增，設定必要約束 [3]
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
    conn.commit()
    print("✓ papers 資料表建立成功")

    # 2. Input & Process: 讀取 CSV 並清洗寫入 [1]
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            
            # 清除舊資料以確保腳本可重複驗證
            cursor.execute("DELETE FROM papers")
            
            # 定義 SQL 插入語法
            insert_query = """
            INSERT INTO papers (title, authors, publish_date, journal, summary, relevance_score, tags, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            for row in reader:
                # 沿用第二天的資料清洗與自動補分邏輯
                title = row["title"].strip()
                authors = row["authors"].strip()
                journal = row["journal"].strip()
                summary = row["summary"].strip()
                url = row["url"].strip()
                publish_date = row["publishDate"].replace("/", "-").strip()
                
                raw_score = row["relevanceScore"].strip()
                if raw_score == "":
                    tags_list = [t.strip() for t in row["tags"].split(";")] if row["tags"] else []
                    score = 80 if "CRISPR" in tags_list and "Agriculture" in tags_list else 70
                else:
                    score = int(raw_score)
                
                tags_str = row["tags"].strip() # 以 "CRISPR;Gene Editing" 格式儲存

                # 3. Output: 使用「參數化查詢」安全寫入，防範攻擊 [4]
                cursor.execute(insert_query, (
                    title, authors, publish_date, journal, summary, score, tags_str, url
                ))
            
        conn.commit()
        print(f"✓ 成功將 CSV 數據導入 {DB_FILE}")
    else:
        print(f"✗ 找不到原始檔案 {CSV_FILE}")

    conn.close()

if __name__ == "__main__":
    init_database()
