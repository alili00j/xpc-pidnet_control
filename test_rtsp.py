import cv2

# RTSP URL
rtsp_url = "rtsp://admin:admin123@192.168.1.66:554"
# rtsp_url = "http://192.168.1.66:8000"
# 创建VideoCapture对象并打开视频流
cap = cv2.VideoCapture(rtsp_url)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = cap.get(cv2.CAP_PROP_FPS)
# 保证摄像头的输出与保存的视频尺寸大小相同
size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
out = cv2.VideoWriter('camera_test2.avi', fourcc, 10.0, size)
# cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)             # 设置缓冲区大小为1帧
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)          # 设置宽度为640
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)         # 设置高度为480
# cap.set(cv2.CAP_PROP_FPS, 30)                   # 设置帧率为30fps
# cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.CAP_DSHOW)  # 设置硬件加速解码
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
# 检查视频流是否成功打开
if not cap.isOpened():
    print("无法打开视频流")
else:
    # 不断读取视频流帧
    while True:
        ret, frame = cap.read()

        if ret:
            # 在这里对每一帧图像进行处理
            # 在示例中，将该帧显示出来
            cv2.imshow('Frame', frame)
            out.write(frame)
        # 按下'q'键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# 释放VideoCapture对象和销毁窗口
cap.release()
out.release()
cv2.destroyAllWindows()