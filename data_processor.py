import csv
import json
import os

# 定義輸入與輸出路徑
INPUT_FILE = "papers_raw.csv"
OUTPUT_FILE = "papers.json"

def clean_and_normalize():
    # 確認原始檔案存在
    if not os.path.exists(INPUT_FILE):
        print(f"錯誤：找不到輸入檔案 {INPUT_FILE}")
        return

    cleaned_papers = []

    # 1. Input: 讀取原始 CSV 檔案
    with open(INPUT_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        for index, row in enumerate(reader, start=1):
            # 2. Process: 資料清洗與格式化
            
            # 消除標題與作者的前後空白
            title = row["title"].strip()
            authors = row["authors"].strip()
            journal = row["journal"].strip()
            summary = row["summary"].strip()
            url = row["url"].strip()
            
            # 日期格式標準化 (將 YYYY/MM/DD 替換為 YYYY-MM-DD)
            publish_date = row["publishDate"].replace("/", "-").strip()
            
            # 將標籤字串以分號拆解為陣列
            tags_str = row["tags"].strip()
            tags_list = [tag.strip() for tag in tags_str.split(";")] if tags_str else []
            
            # 處理缺失的相關度評分 (Relevance Score)
            raw_score = row["relevanceScore"].strip()
            if raw_score == "":
                # 簡單自動評分邏輯
                if "CRISPR" in tags_list and "Agriculture" in tags_list:
                    score = 80
                else:
                    score = 70  # 預設基準分
                print(f"ℹ️ 文獻 [{title[:20]}...] 缺失評分，自動補齊為: {score}%")
            else:
                score = int(raw_score)

            # 組合成乾淨的字典結構
            cleaned_paper = {
                "id": index,
                "title": title,
                "authors": authors,
                "publishDate": publish_date,
                "journal": journal,
                "summary": summary,
                "relevanceScore": score,
                "tags": tags_list,
                "url": url
            }
            cleaned_papers.append(cleaned_paper)

    # 3. Output: 寫入為標準 JSON 檔案
    with open(OUTPUT_FILE, mode="w", encoding="utf-8") as json_file:
        json.dump(cleaned_papers, json_file, indent=4, ensure_ascii=False)
        
    print(f"🎉 成功清洗 {len(cleaned_papers)} 筆資料，已輸出至 {OUTPUT_FILE}")

if __name__ == "__main__":
    clean_and_normalize()