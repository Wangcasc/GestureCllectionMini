import random

import xlsxwriter as xw
import os
import csv
import pandas as pd

ill_list = [
    '1_1_0_2_6',
    '1_1_105_0_2',
    '1_1_108_5_3',
    '1_1_108_5_7',
    '1_1_114_2_5',
    '1_1_116_0_5',
    '1_1_11_0_3',
    '1_1_11_0_9',
    '1_1_128_4_4',
    '1_1_134_2_2',
    '1_1_27_0_5',
    '1_1_39_0_2',
    '1_1_51_0_2',
    '1_1_53_0_2',
    '1_1_67_0_0',
    '1_1_74_0_2',
    '1_1_83_5_4',
    '1_1_93_0_9',
    '1_1_93_1_2',
    '2_1_30_2_0',
    '2_1_34_5_1',
    '2_1_3_3_7',
    '2_1_43_2_3',
    '2_1_47_1_7',
    '2_2_19_0_1',
    '2_2_26_2_4',
    # 上面是存在关键点缺失的样本，下面是关键点坐标超出图像边界的样本
    '1_1_104_0_0',
    '1_1_104_0_1',
    '1_1_104_0_2',
    '1_1_104_0_4',
    '1_1_104_0_5',
    '1_1_11_0_0',
    '1_1_121_0_5',
    '1_1_121_0_6',
    '1_1_121_0_7',
    '1_1_121_0_8',
    '1_1_121_0_9',
    '1_1_126_0_4',
    '1_1_128_0_4',
    '1_1_134_0_5',
    '1_1_134_0_6',
    '1_1_134_0_7',
    '1_1_134_0_8',
    '1_1_134_0_9',
    '1_1_137_0_8',
    '1_1_138_0_0',
    '1_1_138_0_1',
    '1_1_138_0_3',
    '1_1_139_0_6',
    '1_1_15_0_5',
    '1_1_1_0_5',
    '1_1_27_0_8',
    '1_1_28_0_1',
    '1_1_28_0_4',
    '1_1_32_0_4',
    '1_1_32_0_5',
    '1_1_32_0_6',
    '1_1_32_0_8',
    '1_1_32_0_9',
    '1_1_39_0_3',
    '1_1_39_0_6',
    '1_1_39_0_8',
    '1_1_39_0_9',
    '1_1_40_0_3',
    '1_1_41_0_6',
    '1_1_45_0_2',
    '1_1_45_0_8',
    '1_1_4_0_7',
    '1_1_4_0_8',
    '1_1_54_0_0',
    '1_1_54_0_1',
    '1_1_54_0_2',
    '1_1_54_0_3',
    '1_1_54_0_6',
    '1_1_54_0_7',
    '1_1_54_0_8',
    '1_1_54_0_9',
    '1_1_57_0_0',
    '1_1_57_0_4',
    '1_1_58_0_1',
    '1_1_58_0_5',
    '1_1_58_0_6',
    '1_1_58_0_7',
    '1_1_58_0_8',
    '1_1_67_0_7',
    '1_1_68_0_6',
    '1_1_68_0_7',
    '1_1_68_0_8',
    '1_1_69_0_4',
    '1_1_78_0_4',
    '1_1_78_0_5',
    '1_1_78_0_6',
    '1_1_78_0_7',
    '1_1_78_0_9',
    '1_1_80_0_6',
    '1_1_84_0_8',
    '1_1_86_0_3',
    '1_1_92_0_1',
    '1_1_93_0_4',
    '1_1_94_0_7',
    '1_1_99_0_3',
    '1_1_99_0_5',
    '1_1_99_0_7',
    '1_1_99_0_8',
    '1_1_99_0_9',
    '1_1_9_0_2',
    '1_1_9_0_7',
    '1_1_9_0_9',
    '2_1_15_0_3',
    '2_1_16_0_6',
    '2_1_27_0_5',
    '2_1_30_0_4',
    '2_1_30_0_8',
    '2_1_34_0_9',
    '2_1_40_0_0',
    '2_1_40_0_1',
    '2_1_40_0_2',
    '2_1_40_0_4',
    '2_1_40_0_9',
    '2_1_43_0_9',
    '2_1_47_0_3',
    '2_1_47_0_4',
    '2_1_47_0_5',
    '2_1_47_0_8',
    '2_1_4_0_1',
    '2_1_7_0_1',
    '2_1_7_0_2',
    '2_1_7_0_3',
    '2_2_20_0_6',
    '2_2_26_0_1',
    '2_2_27_0_7',
    '2_2_27_0_8',
    '2_2_28_0_2',
    '2_2_28_0_6',
    '2_2_28_0_7',
    '2_2_40_0_2',
    '2_2_9_0_6',
]

# delete ill samples in csv file
def delete_ill():
    csv_dir = r'D:\ZYF\datasets\metadata\metadata'
    csv_list = os.listdir(csv_dir)
    for csv_file in csv_list:
        print(csv_file)
        csv_path = os.path.join(csv_dir, csv_file)
        fin_csv = pd.read_csv(csv_path)
        drop_list = []
        for i, row in fin_csv.iterrows():  # 遍历行
            if row[0] in ill_list or row[1] in ill_list:  # 如果行索引在 ill_list 中
                drop_list.append(i)  # 添加到要删除的索引集合中
        csv_new = fin_csv.drop(drop_list)
        csv_new.to_csv(os.path.join(r'D:\ZYF\datasets\metadata\metadata_new', csv_file), index=False, encoding="utf-8")

#remove ill sample folders
# video_dir = r'D:\ZYF\datasets\DHG-Auth\color_hand'
# for video in ill_list:
#     video_path = os.path.join(video_dir, video)
#     os.remove(video_path)
#     print('remove ', video)

# generate csv
# with open('E:\ZYF\datasets\metadata\metadata/test.csv', "w") as csvfile:
#     writer = csv.writer(csvfile)
#     title = ['vid_name', 'label', 'use?']  # 设置表头
#     writer.writerow(title)
#     video_dir = 'E:\ZYF\datasets\DHG-Auth\color_hand'
#     video_list = os.listdir(video_dir)
#     for vid_name in video_list:
#         if vid_name.split('_')[0] == '2':
#             insertData = [vid_name, vid_name.split('_')[2], 'True']
#             writer.writerow(insertData)
#         else:
#             continue

# with open(f'E:\ZYF\datasets\metadata\metadata_new/test_uesr1.csv', "w") as csvfile:
#     writer = csv.writer(csvfile)
#     title = ['vid_name', 'label', 'use?']  # 设置表头
#     writer.writerow(title)
#     video_dir = 'E:\ZYF\datasets\DHG-Auth\color_hand'
#     video_list = os.listdir(video_dir)
#     for vid_name in video_list:
#         if vid_name.split('_')[0] == '2':
#             insertData = [vid_name, vid_name.split('_')[2], 'True']
#             writer.writerow(insertData)
#         else:
#             continue
# workbook = xw.Workbook('E:\ZYF\datasets\metadata\metadata/test.csv')  # 创建工作簿
# worksheet1 = workbook.add_worksheet("sheet1")  # 创建子表
# worksheet1.activate()  # 激活表
# worksheet1.write_row('A1', title)  # 从A1单元格开始写入表头
# workbook.close()  # 关闭表


# generate csv for Real_DHGA dataset
def generate_csv_rd_test():
    for gesture in range(0, 10):
        with open(f'D:\ZYF\datasets\metadata\metadata_rd/test_single_session_gesture{gesture+1}.csv', "w", newline="") as csvfile:
            print('gesture', gesture+1)
            writer = csv.writer(csvfile)
            title = ['video1', 'video2', 'label']  # 设置表头
            writer.writerow(title)
            train = session = 1
            for id in range(6, 42):
                # 构建正样本
                for sample in range(0, 5):
                    video1 = f'{train}_{session}_{id+1}_{gesture+1}_{sample+1}'  # 文件夹命名从1开始，所以所有从0开始的序号要加1才能对得上
                    for sample2 in range(sample+1, 6):
                        video2 = f'{train}_{session}_{id+1}_{gesture+1}_{sample2+1}'
                        insertData = [video1, video2, '1']
                        writer.writerow(insertData)
                # 构建负样本
                for i in range(15):
                    sample = random.randint(0, 5)
                    video1 = f'{train}_{session}_{id + 1}_{gesture + 1}_{sample + 1}'
                    while True:
                        id2 = random.randint(0, 41)
                        if not id2 == id:
                            break
                    sample2 = random.randint(0, 5)
                    video2 = f'{train}_{session}_{id2 + 1}_{gesture + 1}_{sample2 + 1}'
                    insertData = [video1, video2, '0']
                    writer.writerow(insertData)
        print('gesture', gesture + 1, 'finished')

def generate_csv_rd_train():
    with open(f'D:\ZYF\datasets\metadata\metadata_rd/train.csv', "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        title = ['vid_name', 'label', 'use?']  # 设置表头
        writer.writerow(title)
        for id in range(0, 5):
            print(id)
            train = session = 1
            for gesture in range(0, 6):
                for sample in range(0, 6):
                    vid_name = f'{train}_{session}_{id+1}_{gesture+1}_{sample+1}'
                    label = id
                    insertData = [vid_name, label, 'TRUE']
                    writer.writerow(insertData)

def check_csv(csv_path):
    fin_csv = pd.read_csv(csv_path)
    for head in fin_csv:
        row = fin_csv[head]
        for i, sample in enumerate(row):
            if sample == '1_1_25_1_7':
                print('1_1_25_1_7')

def generate_csv_rd_multidataset_train():
    # 生成多数据集联合训练的csv文件，使用所有数据
    with open(f'D:\ZYF\datasets\metadata\metadata_rd/train_multidataset.csv', "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        title = ['vid_name', 'label', 'use?']  # 设置表头
        writer.writerow(title)
        for id in range(0, 42):
            print(id)
            train = session = 1
            for gesture in range(0, 10):
                for sample in range(0, 6):
                    vid_name = f'{train}_{session}_{id+1}_{gesture+1}_{sample+1}'
                    label = id + 193
                    insertData = [vid_name, label, 'TRUE']
                    writer.writerow(insertData)

def generate_csv_sd_multidataset_train():
    # 生成多数据集联合训练的csv文件，使用所有数据
    with open(f'D:\ZYF\datasets\metadata\metadata_new/train_multidataset.csv', "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        title = ['vid_name', 'label', 'use?']  # 设置表头
        writer.writerow(title)
        for id in range(0, 143):
            print(id)
            train = session = 1
            for gesture in range(0, 6):
                for sample in range(0, 10):
                    vid_name = f'{train}_{session}_{id}_{gesture}_{sample}'
                    if vid_name in ill_list:
                        continue
                    label = id
                    insertData = [vid_name, label, 'TRUE']
                    writer.writerow(insertData)
        for id in range(0, 50):
            print(id+143)
            train = 2
            for session in range(1, 3):
                for gesture in range(0, 6):
                    for sample in range(0, 10):
                        vid_name = f'{train}_{session}_{id}_{gesture}_{sample}'
                        if vid_name in ill_list:
                            continue
                        label = id+143
                        insertData = [vid_name, label, 'True']
                        writer.writerow(insertData)

if __name__ == '__main__':
    # csv_path = 'D:\ZYF\datasets\metadata\metadata_rd/test_single_session_gesture1.csv'
    # generate_csv_rd_test()
    # delete_ill()
    # generate_csv_rd_train()
    generate_csv_sd_multidataset_train()
    generate_csv_rd_multidataset_train()