# 🍽 食物熱量智慧辨識系統
本專案利用 Flask 搭配 YOLO 物件偵測 進行食物影像辨識，並估算其熱量，最終將辨識結果存入 MySQL，提供歷史紀錄查詢功能。使用者可以透過 相機拍攝 或 上傳圖片 進行食物熱量辨識，並且可以查詢過去的紀錄。

## 📌 功能特色
- 📷 即時相機拍攝 或 上傳圖片 進行食物辨識
- 🧠 YOLO 物件偵測 進行食物分類與熱量估算
    ## 目前可辨識食物
    - ChickenSchnitzel (炸雞排)
    - Cabbage (高麗菜)
    - WaterSpinach (空心菜)
    - Brocoli (花椰菜)
    - Eggplant (茄子)
    - TricolorBeans (三色豆)
    - ShreddedCarrot (紅蘿蔔絲)
    - Spinach (菠菜)
    - Rice (白飯)
    - TomatoScrambledEggs (蕃茄炒蛋)

- 💾 辨識結果儲存至 MySQL，支援歷史紀錄查詢
- 📊 前端即時顯示結果，包含食物名稱與熱量資訊
- 🗑 可刪除歷史紀錄

## 🛠️ 使用技術
| 類別    | 技術
|---------|--------------------------
| 前端    | HTML, CSS, JavaScript
| 後端    | Flask (Python)
| 影像辨識 | YOLO (Object Detection)
| 資料庫   | MySQL
| API 傳輸 | RESTful API (JSON)

## 📌 專案結構
📂 食物熱量辨識系統

├── 📁 static        # 靜態資源 (CSS, JavaScript)

├── 📁 templates     # Flask 頁面模板

├── 📂 models        # YOLO 模型檔案

├── app.py          # Flask 後端主程式

├── database.py     # MySQL 連線管理

├── requirements.txt # 依賴套件清單

├── README.md       # 專案說明文件

## 📜 未來改進
- 開發行動版 APP (React Native)
- 支援多種語言顯示
- 使用 TensorFlow Lite 加速辨識
- 加入 AI 推薦健康食譜功能


