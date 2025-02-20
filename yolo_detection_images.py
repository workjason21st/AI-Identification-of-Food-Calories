from matplotlib.projections import get_projection_class, get_projection_names
import numpy as np
import time
import cv2
import os
from sklearn.linear_model import LinearRegression
import pickle

# 設定 YOLO 物件偵測的參數
confthres = 0.5  # 物件偵測的信心閾值
nmsthres = 0.1  # 非最大抑制閾值
yolo_path = "./models/"  # YOLO 模型的根目錄
cfgpath = "./yolov4-ten_food.cfg"  # YOLO 的設定檔
dataPath = "./ten_food.data"  # YOLO 的數據設定檔
wpath = "./yolov4-ten_food_last.weights"  # YOLO 權重檔案
labelsPath="./ten_food.names" # YOLO 標籤檔案
#network,class_names,_=darknet.load_network(cfgpath,dataPath,wpath)

# 讀取預先訓練好的線性回歸模型，用於熱量估算
models = []
for i in range(10):
    with open(f'./linearmodel/linear_regression_model{i}.pkl', 'rb') as file:
        models.append(pickle.load(file))

# 英文標籤對應的中文標籤
label_translation = {
    "ChickenSchnitzel": "炸雞排",
    "Cabbage": "高麗菜",
    "WaterSpinach": "空心菜",
    "Brocoli": "花椰菜",
    "Eggplant": "茄子",
    "TricolorBeans": "三色豆",
    "ShreddedCarrot": "紅蘿蔔絲",
    "Spinach": "菠菜",
    "Rice": "白飯",
    "TomatoScrambledEggs": "蕃茄炒蛋"
}
# 定義長 寬 熱量 公克 長(cm)寬(cm)
# width,high,calory,g,widthcm,highcm
areacalory=[[2060,1465,494,270,17,12],
	    	[1212,1343,32,120,10,11],
	    	[1697,1587,53,280,14,13],
	    	[1318,1314,34,100,11,11],
	    	[940,1099,17,75,8,9],
	    	[1576,1221,214,100,13,10],
	    	[1212,1099,19,49,10,9],
	    	[1454,855,11,63,12,7],
	    	[1334,1377,268,150,11,11],
	    	[970,977,51,60,8,8],
]

def get_labels(labels_path):
    # 讀取標籤檔案，取得標籤名稱
    lpath=os.path.sep.join([yolo_path, labels_path])
    LABELS = open(lpath).read().strip().split("\n")
    return LABELS

def get_colors(LABELS):
    # 產生隨機顏色，用於不同的物件標註
    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),dtype="uint8")
    return COLORS

def get_weights(weights_path):
    # 取得 YOLO 權重檔案路徑
    weightsPath = os.path.sep.join([yolo_path, weights_path])
    return weightsPath

def get_config(config_path):
    # 取得 YOLO 設定檔案路徑
    configPath = os.path.sep.join([yolo_path, config_path])
    return configPath

def load_model(configpath,weightspath):
    # 加載 YOLO 模型
    print("[INFO] 載入 YOLO 模型...")
    net = cv2.dnn.readNetFromDarknet(configpath, weightspath)
    return net

def get_predection(image,net,LABELS,COLORS):
    # 存放偵測結果
    results = []
    # 取得影像尺寸
    (H, W) = image.shape[:2]

    # 文字大小與粗度
    text_scale_factor = min(W, H) / 1000.0
    text_thickness_factor = int(min(W, H) / 200.0)
    # 取得 YOLO 網路層名稱
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]
    
    # 對輸入影像進行預處理
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)
    net.setInput(blob)
    start = time.time()
    layerOutputs = net.forward(ln)
    print(layerOutputs)
    end = time.time()

    print("[INFO] YOLO 偵測時間: {:.6f} 秒".format(end - start))

    # 儲存偵測到的物件資訊
    boxes = []
    confidences = []
    classIDs = []
    areas = []
    calories = []
    calories_list = []

    # 遍歷 YOLO 偵測結果
    for output in layerOutputs:
        # 遍歷每個偵測到的物件(類別 ID 和信心值)
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            
            # 過濾掉低於信心閾值的預測結果
            if confidence > confthres:
                # 將邊界框座標轉換回相對於影像大小的比例
                # YOLO 返回的是邊界框的中心 (x, y) 座標以及寬度和高度
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                # 根據中心座標計算邊界框的左上角座標
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                area = int(width * height)*5
                #for j in r:
                    #area=float(j[2][2]*j[2][3])
                    #classID=j[0]
                
                # 使用線性回歸模型預測熱量
                cal = models[classID].predict(np.array([[area]]))
                cal = "{:.2f}".format(float(cal))
                # 更新邊界框、信心值和類別 ID 的列表
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)
                areas.append(area)
                calories.append(cal)
                calories_list.append(cal)
                if len(calories_list) > 10:
                    calories_list.pop(0)

    # 非最大抑制 (NMS)
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, confthres,
                            nmsthres)

    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            if x + w > W:
                x = W - w
            if y + h > H:
                y = H - h

            color = [int(c) for c in COLORS[classIDs[i]]]
            cv2.rectangle(image, (x, y), (x + w, y + h), color, text_thickness_factor)
            #text = "{}".format(label_translation.get(LABELS[classIDs[i]], LABELS[classIDs[i]]))
            print(boxes)
            print(classIDs)

            # 存入結果列表 #
            results.append({
                "label": label_translation.get(LABELS[classIDs[i]], LABELS[classIDs[i]]),  # 標籤
                "confidence": confidences[i],  # 信心度
                "bounding_box": (x, y, w, h),  # 邊界框
                "area": areas[i],  # 面積
                "calories": calories[i]  # 熱量
            })
            #cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, text_scale_factor, color, text_thickness_factor)
    return results


def runModel(image):
    Lables=get_labels(labelsPath)
    CFG=get_config(cfgpath)
    Weights=get_weights(wpath)
    nets=load_model(CFG,Weights)
    Colors=get_colors(Lables)
    res=get_predection(image,nets,Lables,Colors)
    return res