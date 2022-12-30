#主函数
import sys
import os
from glob import glob
import cv2
import myframe
import time
import pdb
import socket
import struct

# 定义变量

# 眼睛闭合判断
EYE_AR_THRESH = 0.15        # 眼睛长宽比
EYE_AR_CONSEC_FRAMES = 2    # 闪烁阈值

#嘴巴开合判断
MAR_THRESH = 0.65           # 打哈欠长宽比
MOUTH_AR_CONSEC_FRAMES = 3  # 闪烁阈值

# 定义检测变量，并初始化
COUNTER = 0                 #眨眼帧计数器
TOTAL = 0                   #眨眼总数
mCOUNTER = 0                #打哈欠帧计数器
mTOTAL = 0                  #打哈欠总数
ActionCOUNTER = 0           #分心行为计数器器

# Dangerous behavior detect flag
smoke = 0
phone = 0
drink = 0

# 疲劳判断变量
# Perclos模型
# perclos = (Rolleye/Roll) + (Rollmouth/Roll)*0.2
Roll = 0                    #整个循环内的帧技术
Rolleye = 0                 #循环内闭眼帧数
Rollmouth = 0               #循环内打哈欠数
# pdb.set_trace()
cap = cv2.VideoCapture(0)
i = 0
while cap.isOpened():
    success, frame = cap.read()
    if success:
        # 检测
        # 将摄像头读到的frame传入检测函数myframe.frametest()
        ret,frame = myframe.frametest(frame)  
        lab,eye,mouth = ret
        ActionCOUNTER += 1
        for res in lab:
            if res == 'smoke' and smoke == 0:
                print("Dangerous: Please stop smoking")
                smoke = 1
                phone = 0
                drink = 0
            elif res == 'phone' and phone == 0:
                print("Dangerous: Mobile phone detected")
                smoke = 0
                phone = 1
                drink = 0
            elif res == 'bottle' and drink == 0:
                print("Dangerous: Drinking water while driving")
                smoke = 0
                phone = 0
                drink = 1
            if ActionCOUNTER > 0:
                ActionCOUNTER -= 1
        if ActionCOUNTER == 15:
            ActionCOUNTER = 0
            smoke = 0
            phone = 0
            drink = 0

        if eye < EYE_AR_THRESH:
            # 如果眼睛开合程度小于设定好的阈值
            # 则两个和眼睛相关的计数器加1
            COUNTER += 1
            Rolleye += 1
        else:
            # 如果连续2次都小于阈值，则表示进行了一次眨眼活动
            if COUNTER >= EYE_AR_CONSEC_FRAMES:  
                TOTAL += 1
                print("Number of blinks:" + str(TOTAL))
                # 重置眼帧计数器
                COUNTER = 0

        # 哈欠判断，同上
        if mouth > MAR_THRESH: 
            mCOUNTER += 1
            Rollmouth += 1
        else:
            # 如果连续3次都小于阈值，则表示打了一次哈欠
            if mCOUNTER >= MOUTH_AR_CONSEC_FRAMES:  
                mTOTAL += 1
                print("Number of yawns: " + str(mTOTAL))
                # 重置嘴帧计数器
                mCOUNTER = 0

        # show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # show = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # cv2.imshow('detect', frame)
        # cv2.waitKey(20)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.10.9', 8088))
        filepath = "img.jpg"
        cv2.imwrite("img.jpg", frame)
        fhead = struct.pack(b'128sl', bytes(os.path.basename(filepath), encoding='utf-8'), os.stat(filepath).st_size)
        s.send(fhead)
 
        fp = open(filepath, 'rb')
        while 1:
            data = fp.read(1024)
            if not data:
                break
            s.send(data)
        fp.close()
        s.close()

        # 疲劳模型
        # 疲劳模型以150帧为一个循环
        # 每一帧Roll加1
        Roll += 1
        # 当检测满150帧时，计算模型得分
        if Roll == 150:
            # 计算Perclos模型得分
            perclos = (Rolleye/Roll) + (Rollmouth/Roll)*0.2
            # 在前端UI输出perclos值
            print("Perclos in the past 150 frames: "+str(round(perclos,3)))
            # 当过去的150帧中，Perclos模型得分超过0.38时，判断为疲劳状态
            if perclos > 0.38:
                print("Fatigue Driving!!!")
            else:
                print("Good State!")

            # 归零
            # 将三个计数器归零
            # 重新开始新一轮的检测
            Roll = 0
            Rolleye = 0
            Rollmouth = 0
            print("Restart fatigue detection...")
        i += 1
    else:
        perclos = (Rolleye/Roll) + (Rollmouth/Roll)*0.2
        # 在前端UI输出perclos值
        print(f"Perclos in the past {Roll} frames: "+str(round(perclos,3)))
        # 当过去的150帧中，Perclos模型得分超过0.38时，判断为疲劳状态
        if perclos > 0.38:
            print("Fatigue Driving!!!")
        else:
            print("Good State!")

        # 归零
        # 将三个计数器归零
        # 重新开始新一轮的检测
        Roll = 0
        Rolleye = 0
        Rollmouth = 0
        print("No camera")
        s.close()
        break

    time.sleep(0.1)
cap.release()