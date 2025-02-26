# 华南理工大学
# 王熙来
# 开发时间：2024/4/17 16:03


import cv2
# import numpy as np
# import mvsdk
# import platform
import os
import csv
import pandas as pd
import datetime
class Utils():
    def __init__(self, win):
        self.win = win
        self.information_csv_path = win.information_csv_path
        self.user_ids = []
        self.init_csv()

    def init_csv(self):
        # 检插特征库里和csv里是否一样
        if not os.path.exists(self.information_csv_path):
            headers = ['name', 'id', '性别']
            with open(self.information_csv_path, 'w',  encoding='utf-8-sig')as f:
                f_csv = csv.writer(f)
                f_csv.writerow(headers)

        # 读csv
        with open(self.information_csv_path,  encoding='utf-8-sig') as f:
            f_csv = csv.reader(f)

            for i, row in enumerate(f_csv):
                if i == 0: continue
                try:
                    id = row[1]
                    self.user_ids.append(id)
                except:
                    break
            print("user_ids:", self.user_ids)

    def save_video(self,path,camera, imgs):

        sample_camera_path = os.path.join(path, camera)
        if not os.path.exists(sample_camera_path):
            os.mkdir(sample_camera_path)

        for index, img in enumerate(imgs):
            img_path = os.path.join(sample_camera_path, '%03d.jpg' % (index + 1))
            # cv2.imshow("{}".format(camera), img)
            # cv2.waitKey(1)
            cv2.imwrite(img_path, img)

        # cv2.destroyAllWindows()

    # def save_picture(self, camera, img):
    #     sample_path = os.path.join(self.conf.root_path, "calibration_pic", camera)
    #     if not os.path.exists(sample_path):
    #         os.mkdir(sample_path)
    #     img_path = os.path.join(sample_path, "{}.jpg".format(datetime.datetime.now().strftime('%m_%d_%H_%M_%S')))
    #     cv2.imwrite(img_path, img)

    def add_id(self):
        if self.win.ID in self.user_ids:
            return
        else:
            user_data = pd.read_csv(self.information_csv_path, dtype=str)
            new_item = {"name": self.win.name, "id": self.win.ID, "性别": self.win.sex}
            new_item = pd.DataFrame(new_item,index=[0])
            user_data = pd.concat([user_data, new_item])
        user_data.to_csv(self.information_csv_path, index=None)
        self.user_ids.append(self.win.ID)


