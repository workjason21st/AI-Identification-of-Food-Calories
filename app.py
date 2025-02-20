from flask import Flask, render_template , request , jsonify, send_from_directory
from PIL import Image
import os , io , sys
import json
import base64
import traceback
import numpy as np 
import cv2
from datetime import datetime
from yolo_detection_images import runModel
from database import create_connection

# 建立 Flask 應用程式
app = Flask(__name__, static_folder='static')

def resize_with_pad(image, target_size):
    h, w = image.shape[:2]
    scale = min(target_size[0] / w, target_size[1] / h)
    new_w, new_h = int(w * scale), int(h * scale)

    resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    pad_w = (target_size[0] - new_w) // 2
    pad_h = (target_size[1] - new_h) // 2

    padded_image = cv2.copyMakeBorder(resized_image, pad_h, pad_h, pad_w, pad_w,
                                      cv2.BORDER_CONSTANT, value=(255, 255, 255))
    return padded_image

# 主要功能:偵測食物物件並回傳
@app.route('/detectObject' , methods=['POST'])
def mask_image():
    try:
        # 檢查請求中是否包含圖片檔案
        if 'image' not in request.files:
            return jsonify({'error': '未提供圖片'}), 400

        # 取得上傳的檔案
        file = request.files['image']

        # 讀取圖片資料 轉換成NumPy陣列 再轉換成OpenCV影像格式
        try:
            img_pil = Image.open(file).convert("RGB")
            img = np.array(img_pil)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        except Exception as e:
            return jsonify({'error': '圖片格式錯誤，無法解析', 'details': str(e)}), 400
        # 呼叫模型進行食物辨識
        try:
            testResults = runModel(img)
            total_calories = 0
            calories = []
            labels = []
            for result in testResults:
                labels.append(result["label"])
                calories.append(result["calories"])
                total_calories += float(result["calories"])
            if len(labels) == 0:
                testResults = "無法辨識圖片中的食物"
            else:
                testResults = f"以下圖片含有的食物有: {', '.join(labels)}，總共有 {total_calories} 的熱量"

        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)
            return jsonify({'error': '模型辨識失敗', 'details': str(e)}), 500
        
        # 調整圖片大小
        img = resize_with_pad(img, (416, 416))
        # 轉換處理後的圖片為 Base64 編碼
        img = Image.fromarray(img.astype("uint8"))
        rawBytes = io.BytesIO()
        img.save(rawBytes, "JPEG")
        rawBytes.seek(0)
        img_base64 = base64.b64encode(rawBytes.read())

        # 回傳辨識結果與影像
        return jsonify({
            'status': str(img_base64),
            'results': testResults,
            'labels': labels,
            'calories': calories
        })
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({'error': '伺服器內部錯誤', 'details': str(e)}), 500

# 設定 API 允許前端存取圖片
@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.static_folder, filename)

# API 儲存歷史紀錄
@app.route('/saveHistory', methods=['POST'])
def save_history():
    data = request.json
    labels = data.get("labels", [])
    calories = data.get("calories", [])
    image_path = data.get("image_path", "")
    timestamp = data.get("timestamp", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    calories = [float(cal) for cal in calories]

    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO history (labels, calories, image_path, timestamp) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (json.dumps(labels), json.dumps(calories), image_path, timestamp))
                connection.commit()
            return jsonify({"success": True})
        finally:
            connection.close()
    return jsonify({"success": False, "error": "Database connection failed"}), 500

# API 取得歷史紀錄
@app.route('/getHistory', methods=['GET'])
def get_history():
    connection = create_connection()
    if not connection:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT labels, calories, image_path, timestamp FROM history ORDER BY timestamp DESC LIMIT 10")
            history_records = cursor.fetchall()
            history = []
            # JSON轉回 Python 陣列
            for row in history_records:
                try:
                    labels = row["labels"]
                    if labels:
                        labels = json.loads(labels)
                    else:
                        labels = []
                    calories = row["calories"]
                    if calories:
                        calories = json.loads(calories)
                    else:
                        calories = []
                    history.append({
                        "labels": labels,
                        "calories": calories,
                        "image_path": row["image_path"],
                        "timestamp": row["timestamp"]
                    })
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}, row data: {row}")
                    continue
            return jsonify({"success": True, "history": history})
    finally:
        connection.close()
        
# API 清除歷史紀錄
@app.route('/clearHistory', methods=['POST'])
def clear_history():
    connection = create_connection()
    if not connection:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM history")
            connection.commit()
        return jsonify({"success": True})
    finally:
        connection.close()

# 測試 API（確認伺服器運行狀態）
@app.route('/test' , methods=['GET','POST'])
def test():
	print("log: got at test" , file=sys.stderr)
	return jsonify({'status':'succces'})

# 網站首頁（對應到 index.html）
@app.route('/')
def home():
	return render_template('./index.html')
	
# 設定 CORS 允許跨來源請求（避免瀏覽器阻擋 AJAX 請求）
@app.after_request
def after_request(response):
    print("log: setting cors" , file = sys.stderr)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# 啟動 Flask 應用程式
if __name__ == '__main__':
    # 使用 Render 指定的 PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
