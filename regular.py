# !/usr/bin/python
# encoding: utf-8
# author: zhangtong

import os
from PIL import Image
import imghdr
import time
import threading
import shutil
'''
    根据vio_surveil_xxx.dat文件的内容寻找对应的图片信息，进行合格分类统计
'''
img_dir_src = '/data/TRAS/WF/'                       # 源图片文件夹
vio_surveil_xxx = '/data/TRAS/bak/WF/'               # vio_surveil_xxx.dat文件路径
csv_dir_src = '/usr/local/TRAS/Imgdect/Out/'         # csv存储路径
path_save_r = '/usr/local/TRAS/Imgdect/img_save_r/'  # 合格图片文件夹
path_save_w = '/usr/local/TRAS/Imgdect/img_save_w/'  # 不合格图片文件夹
img_info_dict = {}      # {序号:[部门编号,设备编号,拍照总数,格式合格数量],}
device_dict = {}        # 部门及其设备拍照数据记录表 {部门编号:{设备编号:[拍照总数,格式合格数量],},}
img_g = []              # 照片合格列表 [(图片路径,图片名称),]
img_ng = []             # 照片不合格列表 [(图片路径,图片名称),]
total_img_data = []     # 总图片数据 [(图片路径,当前路径下所有图片信息)]


# TODO 判断图片像素点格式是否满足 图片路径,图片名称 返回 T or F
def img_size(img_dir, img_name):
    img = Image.open(img_dir+'/'+img_name)
    w_h = img.size[0]
    h_h = img.size[1]
    if (w_h >= 768 or h_h >= 576) and w_h*h_h >= 768*576 and img.format == "JPEG" and img.mode == "RGB" and abs(w_h - h_h) < 1260:
        return True
    else:
        return False


# TODO 查找vio_surveil_xxx.dat文件 返回符合文件名的列表
def find_vio_f(file_dir, now_time):
    sve_vio_t = []
    for filename in os.listdir(file_dir):
        if filename[:22] == "vio_surveil_"+now_time[:10]:
            sve_vio_t.append(filename)
    return sve_vio_t


# TODO 根据vio_surveil_xxx.dat文件 初始化有关部门信息的两个字典
def device_dict_init(now_time):
    global img_info_dict
    global device_dict
    device_dir = vio_surveil_xxx + now_time[:8] + '/'
    device_list = find_vio_f(device_dir, now_time)
    for i in device_list:
        filename = device_dir + i   # filename 为 vio_surveil开头文件的路径
        with open(filename, encoding="utf-8") as vio_file:
            for line1 in vio_file:
                index = line1.split('|%|', 60)  # index 1为设备编号 59为部门编号 52录入时间
                str_time = ''
                for str1 in filter(str.isdigit, index[52][:13]):
                    str_time += str1
                if str_time != now_time[:10]:
                    continue
                img_info_dict.update({index[0]: [index[1], index[59], 0, 0]})  # 格式参考字典定义位置给出的示例
                if not index[1] in device_dict:
                    device_dict.update({index[1]: {index[59]: [0, 0]}})
                elif not index[59] in device_dict[index[1]]:
                    device_dict[index[1]].update({index[59]: [0, 0]})


# TODO 统计数据到img_info_dict,device_dict
def count_img():
    global img_info_dict
    global device_dict
    global total_img_data
    global img_ng
    global img_g
    goto = False
    for name in img_info_dict:
        for file_data in total_img_data:
            for i in range(1, 4):
                if name + '_0{}.jpg'.format(i) not in file_data[1]:                         # 当前路径没有该图片,从下一个路径找
                    if i != 1:                                                              # 第一张没有可能是在之前目录里
                        goto = True
                    break
                if imghdr.what(os.path.join(file_data[0], name + '_0{}.jpg'.format(i))):    # 判断图片是否损坏
                    img_info_dict[name][2] += 1
                    if img_size(file_data[0], name + '_0{}.jpg'.format(i)):                 # 判断格式是否正确
                        img_g.append((file_data[0], name + '_0{}.jpg'.format(i)))
                        img_info_dict[name][3] += 1
                    else:
                        img_ng.append((file_data[0], name + '_0{}.jpg'.format(i)))
                else:
                    os.remove(file_data[0] + '/' + name + '_0{}.jpg'.format(i))
            if goto:
                goto = False
                break
    for k, v in img_info_dict.items():  # k:序号 v:部门编号等数据
        if v[2] == 1 and v[3] != 0:
            for n in total_img_data:
                for i in range(1, 4):
                    if k + '_0{}.jpg'.format(i) in n[1]:
                        img_ng.append((n[0], k + '_0{}.jpg'.format(i)))
                        img_g.remove((n[0], k + '_0{}.jpg'.format(i)))
                        v[3] = 0
                        goto = True
                        break
                if goto:
                    goto = False
                    break
    for value in img_info_dict:
        if img_info_dict[value][0] in device_dict:
            device_dict[img_info_dict[value][0]][img_info_dict[value][1]][0] += img_info_dict[value][2]
            device_dict[img_info_dict[value][0]][img_info_dict[value][1]][1] += img_info_dict[value][3]


# TODO 获取到的数据存储到本地.csv文件
def save_file(now_time):
    global device_dict
    list1 = ['hour_bmgk/', 'hour_fxcwsbbh/', 'hour_num/', 'hour_xcysbbh/']
    csv_dir = []
    zong_list = []
    hour_bmgk = [['部门', '拍照总次数', '合格次数', '不合格次数', '合格率']]
    hour_num = [['日期', '总照片数', '合规照片数', '不合规照片数', '合格率']]
    hour_xcysbbh = [['部门', '设备编号', '拍照总数', '合格数量', '不合格数量', '合格率']]
    hour_fxcwsbbh = [['部门', '拍照总数(无设备编号)', '合格数量', '不合格数量', '合格率']]
    s_num = 0                   # 总拍照次数
    r_num = 0                   # 总合格次数
    sum_num = 0                 # 有设备照片总数
    no_sum_num = 0              # 无设备照片总数
    regular_num = 0             # 有设备合格正确总数
    no_regular_num = 0          # 无设备合格正确总数
    for k, v in device_dict.items():  # k:部门,n:设备编号,m[0]:该设备拍照数,m[1]:该设备照片的格式正确数
        for n, m in v.items():
            if n == '':
                no_sum_num += m[0]
                if m[0] > 1:
                    no_regular_num += m[1]
            elif m[0] == 0:
                hour_xcysbbh.append([k, n, 0, 0, '0%'])  # 王燊说别改 少个零
            elif m[0] > 1:
                sum_num += m[0]
                regular_num += m[1]
                hour_xcysbbh.append([k, n, m[0], m[1], m[0]-m[1], str(round((m[1]/m[0])*100, 2))+'%'])
            else:
                hour_xcysbbh.append([k, n, m[0], 0, 0, '0%'])  # 这也是 不合格应该是1不是0
                sum_num += m[0]
        if no_sum_num == 0:
            hour_fxcwsbbh.append([k, 0, 0, 0, '0%'])
        else:
            hour_fxcwsbbh.append([k, no_sum_num, no_regular_num, no_sum_num-no_regular_num, str(round((no_regular_num/no_sum_num)*100, 2))+'%'])
        if sum_num == 0:
            hour_bmgk.append([k, 0, 0, 0, '0%'])
        else:
            hour_bmgk.append([k, sum_num+no_sum_num, regular_num+no_regular_num, sum_num+no_sum_num-regular_num-no_regular_num, str(round((regular_num+no_regular_num)/(sum_num+no_sum_num)*100, 2))+'%'])
        s_num = no_sum_num + sum_num + s_num
        r_num = no_regular_num + regular_num + r_num
        no_sum_num = sum_num = no_regular_num = regular_num = 0
    hour_num.append([now_time[:10], s_num, r_num, s_num-r_num, str(round((r_num/s_num)*100, 2))+'%'])
    zong_list.append(hour_bmgk)
    zong_list.append(hour_fxcwsbbh)
    zong_list.append(hour_num)
    zong_list.append(hour_xcysbbh)

    for i in list1:
        csv_dir.append(csv_dir_src + now_time[:8] + '/' + now_time[:10] + '/' + i)
    for i in csv_dir:
        if not os.path.exists(i):
            os.makedirs(i)
    for i in range(len(csv_dir)):
        with open(csv_dir[i] + now_time + list1[i][:-1] + '.csv', 'w') as f1:
            for bmgk in zong_list[i]:
                bmgk = [str(j) for j in bmgk]
                bmgk = ','.join(bmgk)
                f1.write(bmgk + '\n')


# TODO 遍历最近20天的480文件目录数据
def file_open(now_time):
    global total_img_data
    now_time_list = []
    time_array = time.strptime(now_time[:10], "%Y%m%d%H")
    timestamp = int(time.mktime(time_array))
    now_time_list.append(now_time[:10])
    for i in range(480):
        timestamp -= 3600
        now_time_list.append(time.strftime("%Y%m%d%H", time.localtime(timestamp)))
    for i in now_time_list:
        img_dir = img_dir_src + i[:8] + '/' + i + '/imgs'
        if os.path.exists(img_dir):
            for root, dirs, files in os.walk(img_dir):
                total_img_data.append((root, files))


# TODO 图片保存到合格不合格分类中
def file_metastasis():
    for i in img_ng:
        csv_dir = path_save_w+i[0][14:34]
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        shutil.move(i[0] + '/' + i[1], csv_dir + i[1])
    for i in img_g:
        csv_dir = path_save_r+i[0][14:34]
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        shutil.move(i[0] + '/' + i[1], csv_dir + i[1])


# TODO 调用其他方法执行证据监测
def main_(time_now):
    with open('out.log', 'a') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '遍历最近20天的480文件目录数据\n')
    file_open(time_now)
    with open('out.log', 'a') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '读取vio_surveil_xxx.dat文件,初始化img_info_dict,device_dict\n')
    device_dict_init(time_now)
    with open('out.log', 'a') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '读取统计数据\n')
    count_img()
    with open('out.log', 'a') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '保存成.csv文件\n')
    save_file(time_now)
    with open('out.log', 'a') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '图片分类开始\n')
    file_metastasis()
    with open('out.log', 'a') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '结束\n-----------------------------\n')


# TODO 定时任务每隔一小时开始执行一次
def find_file():
    # 获取当前时间的上一个小时的时间 如当前时间为2018-06-29 17:59:59  得到的是 20180629160000
    timearray = time.strptime(time.strftime('%Y%m%d%H', time.localtime(time.time())), "%Y%m%d%H")
    time_now = time.strftime("%Y%m%d%H%M%S", time.localtime(time.mktime(timearray)-3600))
    timer = threading.Timer(3600, find_file)  # 一小时触发一次
    timer.start()
    img_g.clear()
    img_ng.clear()
    total_img_data.clear()
    img_info_dict.clear()
    device_dict.clear()
    main_(time_now)


if __name__ == '__main__':
    find_file()
