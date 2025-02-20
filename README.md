# 🍽 食物熱量智慧辨識系統
本專案利用 Flask 搭配 YOLO 物件偵測 進行食物影像辨識，並估算其熱量，最終將辨識結果存入 MySQL，提供歷史紀錄查詢功能。使用者可以透過 相機拍攝 或 上傳圖片 進行食物熱量辨識，並且可以查詢過去的紀錄。

#### 🎥 更多詳情查看:
https://github.com/user-attachments/assets/805fa3d4-8708-4d7a-9560-e4d58b87d662

## 📌 功能特色
- 📷 即時相機拍攝 或 上傳圖片 進行食物辨識
- 🧠 YOLO 物件偵測 進行食物分類與熱量估算
    #### 目前可辨識食物
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

### ⚠️ 權重缺失：因為 LFS 超出上限
請確保 YOLO 模型的權重檔案已正確下載並放置於 models 資料夾中。

=>> [權重檔案下載](https://drive.google.com/drive/folders/1nwIArQ_Wjk9KglTm61v-jepH-jKNHD7U?usp=drive_link)

##

## 📜 未來改進
- 開發行動版 APP (React Native)
- 支援多種語言顯示
- 使用 TensorFlow Lite 加速辨識
- 加入 AI 推薦健康食譜功能


