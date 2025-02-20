import pymysql
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 建立 MySQL 連線
def create_connection():
    try:
        return pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        print(f"❌ MySQL 連線錯誤: {e}")
        raise  # 遇到錯誤時終止程式

# 確保歷史紀錄的資料表存在
def create_history_table():
    connection = create_connection()
    if not connection:
        print("❌ 無法建立資料表，資料庫連線失敗")
        return
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    labels TEXT NOT NULL,
                    calories TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        connection.commit()
    except Exception as e:
        print(f"❌ 建立資料表失敗: {e}")
    finally:
        connection.close()
        
# 確保資料表已存在
if __name__ == '__main__':
    create_history_table()
