import cv2

def main():
    # 打开摄像头
    video_capture = cv2.VideoCapture('rtmp://192.168.31.222:1935/live/stream')

    # 检查摄像头是否成功打开
    if not video_capture.isOpened():
        print("无法打开摄像头")
        return

    # 获取摄像头帧的宽度和高度
    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(frame_height)
    print(frame_width)

    # 创建窗口
    cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Camera", frame_width, frame_height)

    # 循环读取和显示摄像头画面
    while True:
        # 读取摄像头画面
        ret, frame = video_capture.read()

        # 检查是否成功读取画面
        if not ret:
            print("无法获取画面")
            break

        # 显示摄像头画面
        cv2.imshow("Camera", frame)

        # 按下 'q' 键退出循环
        if cv2.waitKey(1) == ord('q'):
            break

    # 关闭窗口和摄像头
    cv2.destroyAllWindows()
    video_capture.release()

if __name__ == "__main__":
    main()