# 华南理工大学
# 王熙来
# 开发时间：2024/8/17 16:52


import cv2
import numpy as np
# import pyrealsense2 as rs
import time
import concurrent.futures as futures
import os

class CameraTask_Binocular:
    def __init__(self,NS,record_save,frameRates):
        print("CameraTask_Binocular init")

        self.NS = NS # 全局信息路径
        self.record_save = record_save # 缓存标志
        self.frameRates = frameRates    # 帧率

        self.executor = futures.ThreadPoolExecutor(max_workers=1) #保存视频用的线程池

       # 设置双目相机基本信息
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G') # 视频编码格式
        self.cap = cv2.VideoCapture(1 + cv2.CAP_DSHOW)

        self.width = 2560#2560
        self.height = 720#720
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)

        print("width:", self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        print("height:", self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print("fps:", self.cap.get(cv2.CAP_PROP_FPS))




        self.recording = 0
        self.save = 0



    def save_video(self):

        path=self.NS.save_id_path
        sample_camera_path_1 = os.path.join(path, "Binocular_left")
        sample_camera_path_2 = os.path.join(path, "Binocular_right")
        if not os.path.exists(sample_camera_path_1):
            os.mkdir(sample_camera_path_1)
        if not os.path.exists(sample_camera_path_2):
            os.mkdir(sample_camera_path_2)

        for index, img in enumerate(self.RGB_buffer):
            img_path = os.path.join(sample_camera_path_1, '%03d.jpg' % (index + 1))
            img_path2 = os.path.join(sample_camera_path_2, '%03d.jpg' % (index + 1))
            # cv2.imshow("{}".format(camera), img)
            # cv2.waitKey(1)
            # print("img_path:",img_path)

            # 切割开双目相加的左右
            img1 = img[:, :img.shape[1]//2, :]
            img2 = img[:, img.shape[1]//2:, :]

            cv2.imwrite(img_path, img1)
            cv2.imwrite(img_path2, img2)


        self.RGB_buffer = []


        print('Binocular采集完成')
        self.frameRates["lock1"] = 0

    def run(self,pipe,stop_event):
        num=0
        self.RGB_buffer = []
        num_frames = 0
        start_time = time.time()

        while not stop_event.is_set():
            try:
                ret, color_image = self.cap.read()
                if ret:
                    # color_image = cv2.flip(color_image, 1)
                    # depth_image = cv2.flip(depth_image, 1)
                    # self.signal_changeFrame_RGB.emit([color_image, self.win.ui.label_realsense_RGB])
                    # self.signal_changeFrame_Depth.emit([depth_image, self.win.ui.label_realsense_Depth])

                    # 计算帧率
                    num_frames += 1
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 0:
                        fps = num_frames / elapsed_time
                    else:
                        fps = 0
                    if num_frames>60:
                        num_frames=0
                        start_time=time.time()

                    # print("fps:",fps)
                    # print(num_frames)
                    # 把整个图像进行切割，裁剪双目左右各中间部分
                    color_image1 = color_image[:, self.width // 4 - self.height // 2:self.width // 4 + self.height // 2,:]
                    color_image2 = color_image[:,self.width // 4 * 3 - self.height // 2:self.width // 4 * 3 + self.height // 2, :]
                    color_image = np.hstack((color_image1, color_image2))

                    if num_frames % 2 == 0: #降帧率显示
                        frame_show = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
                        # print("frame_show:",frame_show.shape)
                        frame_show = cv2.resize(frame_show, (320,180))
                        # 左右翻转
                        frame_show = cv2.flip(frame_show, 1)
                        pipe.send(frame_show)
                        self.frameRates["Binocular"] = fps
                        # print("fps:", fps)
                        # self.frameRates["progress"] = int(num / self.NS.sample_frame * 100)


                    if self.record_save["Binocular"] == 1:


                        num+=1
                        self.RGB_buffer.append(color_image.copy())
                        # self.Depth_buffer.append(depth_image.copy())
                        # self.Depth_Color_buffer.append(depth_color_image.copy())
                        # self.PCD_buffer.append(pcd.copy())

                        # self.signal_changenum.emit(int(num / self.win.sample_frame * 100))

                        if len(self.RGB_buffer) == 1:
                            self.frameRates["lock1"] = 1
                            start_time2 = time.time()
                        # print(len(self.imgs_buffer))
                        if len(self.RGB_buffer) == self.NS.sample_frame:
                            end_time2 = time.time()
                            print("采集完成，耗时：",end_time2-start_time2)
                            self.executor.submit(self.save_video)
                            print("保存线程正常启动")

                            self.record_save["Binocular"] = 0
                            num = 0

            except Exception as e:
                print(e)




        print("realsence stop")
        # # 停止管道数据传输
        # self.pipeline.stop()
        #
        # # 获取深度传感器的设备
        # depth_sensor = self.pipeline.get_active_profile().get_device().first_depth_sensor()
        # # 关闭深度传感器
        # depth_sensor.stop()




def runBinocularCamera(pipe,stop_event,NS,record_save,frameRates):
    task = CameraTask_Binocular(NS,record_save,frameRates)
    task.run(pipe,stop_event)