# # 华南理工大学
# # 王熙来
# # 开发时间：2024/10/14 11:19
#
import cv2
import time
# # 查看当前电脑有多少个摄像头
#
# # def get_camera_count():
# #     camera_count = 0
# #     for i in range(10):
# #         cap = cv2.VideoCapture(i)
# #         if cap.isOpened():
# #             camera_count += 1
# #             cap.release()
# #     return camera_count
# #
# # print(get_camera_count())
#
fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
fourcc2 = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
#读取两个相机
cap = cv2.VideoCapture(1+cv2.CAP_DSHOW)
cap2 = cv2.VideoCapture(0+cv2.CAP_DSHOW)
#设置视频流宽高
#width=2560  height=720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_FOURCC, fourcc)

cap2.set(cv2.CAP_PROP_FPS, 60)
cap2.set(cv2.CAP_PROP_FOURCC, fourcc2)
# 相机信息
print("width:", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print("height:", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("fps:", cap.get(cv2.CAP_PROP_FPS))

print("width:", cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
print("height:", cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("fps:", cap2.get(cv2.CAP_PROP_FPS))



framenum = 0
framebuffer = []
while True:
    start = time.time()
    ret, frame = cap.read()
    ret2, frame2 = cap2.read()
    # cv2.imshow("frame", frame)
    # cv2.imshow("frame2", frame2)

    # 保存240帧到本地
    # if ret2:
    # 把frame2缩放到0.4倍大小
    frame2 = cv2.resize(frame2, (int(frame2.shape[1] * 0.4), int(frame2.shape[0] * 0.4)))
    frame=cv2.resize(frame, (int(frame.shape[1] * 0.4), int(frame.shape[0] * 0.4)))

    framenum += 1
    cv2.imshow("frame2", frame2)
    cv2.imshow("frame", frame)
        # cv2.imwrite("{}.jpg".format(framenum), frame2)
        # framebuffer.append(frame2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
    # if framenum == 240:
    #     # 保存视频
    #     for i, frame in enumerate(framebuffer):
    #         cv2.imwrite("{}.jpg".format(i), frame)
        break
    end = time.time()
    print("fps:", 1 / (end - start + 0.00001))

# 上面是两个摄像头的初步测试，下面是尝试为两个摄像头指定id,没用

# import cv2
#
# def get_camera_id():
#     capIds = []
#     for i in range(10):
#         try:
#             cap = cv2.VideoCapture(i)
#         except:
#             continue
#
#         if cap.isOpened():
#             # 获取一些摄像头的属性信息，尝试从中推断硬件 ID
#             width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#             height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#             fps = cap.get(cv2.CAP_PROP_FPS)
#             # 这里可以根据需要定义一种方式来生成类似硬件 ID 的标识
#             # 例如，可以使用宽度、高度和帧率的组合作为标识
#             camera_id = f"camera_{width}_{height}_{fps}_{i}"
#             capIds.append(camera_id)
#             cap.release()
#     return capIds
#
# print(get_camera_id())