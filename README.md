# Fatigue Driving detection by Dlib and yolo

project reference: https://github.com/JingyibySUTsoftware/Yolov5-deepsort-driverDistracted-driving-behavior-detection

We implement it on raspberry pi, and use socket to send back detected images. To run it, first run socket_server.py on PC, then run fatigue_detect.py on rasberry pi. Make sure to modify the socket host to the PC's ip address. If there are any trouble to use camera on raspberry pi, we recommend to record a video first and read the video directly.