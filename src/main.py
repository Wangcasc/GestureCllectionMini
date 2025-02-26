# 华南理工大学
# 王熙来
# 开发时间：2024/10/16 16:13

import os
import sys
import shutil
import csv
# 界面
from ui.UI_New import Ui_MAIN_WINDOW

# pyqt
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import pandas as pd

from utils.utils import Utils

# from utils.camera_proc_realsence import runRealsence
from utils.camera_proc_Binocular import runBinocularCamera
from utils.camera_proc_Inf import runInfCamera

from multiprocessing import Pipe, Event, Process, Manager
import cv2

# 将当前工作目录修改为上级目录
sys.path.append("../")


# import pyrealsense2 as rs
# import dv_processing as dv
class Main_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main_Window, self).__init__()
        self.ui = Ui_MAIN_WINDOW()
        self.ui.setupUi(self)
        self.init_UI()
        # 初始化摄像头进程和管道
        self.processes = []
        self.parent_conns = []
        self.stop_events = []
        # self.ui.label_RGB,self.ui.label_RGB_2,self.ui.label_RGB_3,self.ui.label_RGB_4,self.ui.label_RGB_5
        self.show_windows = []
        self.frameRates_label = []  # 记录各个相机的帧率
        self.NS=Manager().Namespace()  # 用于进程间通信Manager命名空间,所有全局变量都放在这里
        self.record_save = Manager().dict()  # 用于进程间通信Manager字典
        self.frameRates = Manager().dict()  # 用于进程间通信Manager字典,记录各个相机的帧率
        self.frameRates["progress"]=0
        self.frameRates["lock1"]=0
        self.frameRates["lock2"]=0




        #采样设置##################
        #采样帧数
        self.NS.sample_frame=int(self.ui.lineEdit_sample_frame.text())
        print('采样帧数为{}'.format(self.NS.sample_frame))
        #保存路径
        self.fpath = self.ui.lineEdit_sample_save_path.text()
        print('保存路径为{}'.format(self.fpath))
        #数据统计csv
        self.information_csv_path = os.path.join(self.fpath, 'user_info.csv')
        self.user_ids = []
        self.init_csv()

        #工具
        self.utils = Utils(self)


        self.timer_imshow=QtCore.QTimer(self)
        self.timer_imshow.timeout.connect(self.update_frames)
        self.timer_imshow.start(1)  # 每33ms检查一次新帧
        
        # self.timer_fault=QtCore.QTimer(self)
        # self.timer_fault.timeout.connect(self.time_out)

        #控件##################
        self.name = self.ui.lineEdit_name.text()
        self.sex = self.ui.comboBox_sex.currentText()
        self.ID = self.ui.lineEdit_ID.text()
        self.gesture_type = self.ui.lineEdit_gesture_type.text()
        self.sample_time = self.ui.lineEdit_NUM.text()
        self.fpath = self.ui.lineEdit_sample_save_path.text()
        #帧数改变
        self.ui.lineEdit_sample_frame.textChanged.connect(self.sample_frame_changed)
        #路径选择
        self.ui.pushButton_select_path.clicked.connect(self.select_path)

        #ID改变
        self.ui.lineEdit_ID.textEdited.connect(self.ID_changed)
        #采样次数改变
        self.ui.lineEdit_NUM.textChanged.connect(self.sample_time_changed)
        #类别改变
        self.ui.lineEdit_gesture_type.textChanged.connect(self.gesture_type_changed)

        #性别改变
        self.ui.comboBox_sex.currentIndexChanged.connect(self.sex_changed)
        #姓名改变
        self.ui.lineEdit_name.textChanged.connect(self.name_changed)
        #注册
        self.ui.pushButton_regist.clicked.connect(self.regist)
        #删除
        self.ui.pushButton_del.clicked.connect(self.del_sample)


        #显示
        self.label_RGB_height = self.ui.label_RGB.geometry().height()  # 图像显示位置的高度
        self.label_RGB_width = self.ui.label_RGB.geometry().width()
        print("RGB Height: {}".format(self.label_RGB_height))
        print("RGB Width: {}".format(self.label_RGB_width))


        # # 双目相机########################################################################################
        parent_conn, child_conn = Pipe()  # 设置管道
        stop_event = Event()  # 设置停止event
        print("双目设备")
        # 记录每个设备的储存标志位 0显示 1缓存后保存
        self.record_save["Binocular"] = 0
        # 每个相机的帧率
        self.frameRates["Binocular"] = 0
        # self.frameRates["realsence_Depth"] = 0
        process = Process(target=runBinocularCamera,
                          args=(child_conn, stop_event, self.NS, self.record_save, self.frameRates))
        process.start()

        self.show_windows.append(self.ui.label_RGB)

        self.frameRates_label.append(self.ui.label_frameRates_1)


        self.parent_conns.append(parent_conn)
        self.stop_events.append(stop_event)
        self.processes.append(process)

        # #红外相机########################################################################################
        parent_conn2, child_conn2 = Pipe()
        stop_event2 = Event()
        print("红外设备")
        self.record_save["Inf"] = 0
        self.frameRates["Inf"] = 0
        process2 = Process(target=runInfCamera,
                           args=(child_conn2, stop_event2, self.NS, self.record_save, self.frameRates))
        process2.start()

        self.show_windows.append(self.ui.label_Inf)
        self.frameRates_label.append(self.ui.label_frameRates_2)
        self.parent_conns.append(parent_conn2)
        self.stop_events.append(stop_event2)
        self.processes.append(process2)

        print("parent_conns:", len(self.parent_conns))



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
            # print("user_ids:", self.user_ids)
    def init_UI(self):
        #初始化UI
        #图标        #自适应大小
        self.ui.label_scut.setPixmap(QPixmap("./sys_img/scut.jpg"))
        self.ui.label_BIP.setPixmap(QPixmap("./sys_img/biplab.jpg"))

    def sample_frame_changed(self):
        try:
            self.NS.sample_frame = int(self.ui.lineEdit_sample_frame.text())
            print('将采样帧数改成了{}'.format(self.NS.sample_frame))
        except:
            return

    def select_path(self):
        self.fpath = QFileDialog.getExistingDirectory(self, "选择保存视频的根目录", "../")
        if self.fpath == '':
            QMessageBox.warning(self, "Warning", "请选择需要保存的路径")
            return
        self.ui.lineEdit_sample_save_path.setText(self.fpath)
        print('保存路径为{}'.format(self.fpath))
        self.information_csv_path = os.path.join(self.fpath, 'user_info.csv')
        self.init_csv()

    def ID_changed(self):
        self.ID = self.ui.lineEdit_ID.text()
        print('ID为{}'.format(self.ID))

    def sample_time_changed(self):
        self.sample_time = self.ui.lineEdit_NUM.text()
        print('第{}次采样'.format(self.sample_time))

    def gesture_type_changed(self):
        self.gesture_type = self.ui.lineEdit_gesture_type.text()
        print('类别为{}'.format(self.gesture_type))




    def sex_changed(self):
        self.sex = self.ui.comboBox_sex.currentText()
        print('性别为{}'.format(self.sex))



    def name_changed(self):
        self.name = self.ui.lineEdit_name.text()
        print('姓名为{}'.format(self.name))

    def update_frames(self):
        #从管道里面读取数据，初始化的时候管道和show_label是一一对应的
        self.ui.progressBar.setValue(int(self.frameRates["progress"]))
        try:
            for i, parent_conn in enumerate(self.parent_conns):
                # print("i:", i)
                # print("parent_conn:", parent_conn.poll())
                if parent_conn.poll():
                    # print("i:", i)

                    frame = parent_conn.recv()
                    # print("frame:", frame.shape)

                    # frame = QImage(frame, frame.shape[1], frame.shape[0],frame.shape[1]*3, QImage.Format_RGB888)
                    # print(self.show_windows[i].height(),self.show_windows[i].width())
                    frame=cv2.resize(frame,(self.show_windows[i].width(),self.show_windows[i].height()))
                    # cv2.imshow("{}".format(self.show_windows[i]),frame)
                    # print(self.show_windows[i].height(), self.show_windows[i].width())
                    frame=QImage(frame, self.show_windows[i].width(), self.show_windows[i].height(),self.show_windows[i].width()*3, QImage.Format_RGB888)
                    # print(self.show_windows[i].height(), self.show_windows[i].width())
                    img = QPixmap.fromImage(frame)
                    self.show_windows[i].setPixmap(img)

                    self.frameRates_label[i].setText("帧率：{:.2f}".format(self.frameRates["Binocular"])) #Binocular Inf

                    if self.frameRates["lock1"]==0 and self.frameRates["lock2"]==0 and self.ui.pushButton_regist.isEnabled() ==False  :
                        self.ui.pushButton_regist.setEnabled(True)

        except Exception as e:
            print("Exception:", e)
            # print("update_frames failed")
            pass


    def add_id(self):
        if self.ID in self.user_ids:
            return
        else:
            user_data = pd.read_csv(self.information_csv_path, dtype=str)
            new_item = {"name": self.name, "id": self.ID, "性别": self.sex, "年龄": self.age}
            new_item = pd.DataFrame(new_item,index=[0])
            user_data = pd.concat([user_data, new_item])
            user_data.to_csv(self.information_csv_path, index=None)
            self.user_ids.append(self.ID)

    def regist(self):
        #检查信息是否完整
        if self.name=='' or self.sex==''  or self.ID==''  or self.gesture_type=='' or self.sample_time=='':
            QMessageBox.warning(self, "Warning", "当前用户信息不全，请重新填写")
            return

        img_path = self.fpath + '/img'
        if not os.path.isdir(img_path):
            os.makedirs(img_path)

        #检查是否注册过
        self.save_id_path=img_path+'/'+self.ID+"_"+self.gesture_type+"_"+self.sample_time
        if os.path.exists(self.save_id_path):
            del_or_not = QMessageBox.warning(self, "Warning", "已注册，点击确定将重新注册，是否继续？", QMessageBox.Yes | QMessageBox.No,
                                             QMessageBox.Yes)
            if del_or_not == QMessageBox.No:
                return

        if not os.path.isdir(self.save_id_path):
            os.makedirs(self.save_id_path)

        self.NS.save_id_path=self.save_id_path

        self.frameRates["lock1"] = 1
        self.frameRates["lock2"] = 1


        self.record_save["Binocular"] = 1

        self.record_save["Inf"] = 1

        # self.timer_fault.start(2000)
        # print("timer start")
        self.add_id()

        # disable regist lable
        self.ui.pushButton_regist.setDisabled(True)


    def del_sample(self):
        #检查信息是否完整
        if self.name=='' or self.sex=='' or self.ID=='' or  self.gesture_type=='' or self.sample_time=='':
            QMessageBox.warning(self, "Warning", "信息不全，请重新填写")
            return

        img_path = self.fpath + '/img'
        sample=self.ID+"_"+self.gesture_type+"_"+self.sample_time
        self.del_id_path=img_path+'/'+sample
        if os.path.exists(self.del_id_path):
            del_or_not = QMessageBox.warning(self, "Warning", "点击确定将删除样本“{}”，是否继续？".format(sample), QMessageBox.Yes | QMessageBox.No,
                                             QMessageBox.Yes)
            if del_or_not == QMessageBox.No:
                return
            else:
                shutil.rmtree(self.del_id_path)


                #检查是否还有该ID的样本,没有则删除ID信息
                id_left= False
                samples= os.listdir(img_path)
                for sample in samples:
                    if sample.split('_')[2]==self.ID:
                        id_left=True
                        break

                if id_left==False:
                    df = pd.read_csv(self.information_csv_path, dtype=str)
                    for i in range(df.shape[0]):
                        if df.values[i, 1] == self.ID:
                            df.drop(df.index[i], inplace=True)
                            df.to_csv(self.information_csv_path, index=False)

                QMessageBox.information(self, "Information", "删除成功")

        else:
            QMessageBox.warning(self, "Warning", "未注册，请检查信息是否正确")
            return

    #
    # def time_out(self):
    #     print("time out")
    #     for thread in self.threads:
    #         thread.save = 1
    #     self.timer_fault.stop()
    #
    # def show_frame(self, lst):
    #     frame = lst[0]
    #     label = lst[1]
    #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #     frame = cv2.resize(frame, (self.label_RGB_height, self.label_RGB_width))
    #     frame = QImage(frame, self.label_RGB_height, self.label_RGB_width, QImage.Format_RGB888)
    #     img = QPixmap.fromImage(frame)
    #     label.setPixmap(img)

    def closeEvent(self, event):
        self.timer_imshow.stop()
        #关闭管道，防止卡死
        for parent_conns in self.parent_conns:
            parent_conns.close()
        # print("close")
        for stop_event in self.stop_events:
            stop_event.set()
        # time.sleep(5)
        # print("close")
        for process in self.processes:
            process.join()
            print("close")
        event.accept()
        # print("close")

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    window = Main_Window()
    window.show()
    sys.exit(app.exec_())