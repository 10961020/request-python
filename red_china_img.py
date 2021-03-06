# !/usr/bin/python  
# encoding: utf-8
# author: zhangtong
'''
爬取 红动中国 图片素材
    # folder_path   保存文件路径 文件夹不存在都可以，无需手动创建
    # url           在此网站里搜索素材的结果网址(不懂把下边的url的网址复制打开一看便知)
    修改这俩就可以把当前搜索到的所有数据获取下来
    
    PS 红动中国下载的图片在下方都会有高度为 30xp 的黑背景水印 19到25行 执行即可去除这段水印 修改walk参数路径为图片文件夹路径即可
    遇到ImportError 提示没什么库 自行装什么库 cv2库安装名为 opencv-python 比较特殊一些
'''
import cv2
import time
import os
import re
import requests

# TODO 图片裁剪去下半部分水印
# for root, dirs, files in os.walk('c:/Users/Administrator/Desktop/DeepLearn_img/fog/no_fog/'):
#     for i in files:
#         image = cv2.imread(root+'/'+i)
#         height = image.shape[0]
#         print(i+': ', height)
#         copy_image = image[:height-30, :]
#         cv2.imwrite(root+'/'+i[:-4]+'_1.jpg', copy_image)

# TODO 收集图片
value = 10
folder_path = 'D:/1/project/photo_fog'
url_path = 'http://so.redocn.com'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
url = 'http://so.redocn.com/fengjing/b9abc2b7b7e7beb0.htm'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}
while True:
    response = requests.get(url, headers=headers)
    p = re.compile(r'<a  target="_blank"  href="(.*?)">')
    list_1 = p.findall(response.text)
    for i in list_1:
        response_2 = requests.get(i, headers=headers)
        p = re.compile(r'<div class="img_box"><img src="(.*?)"')
        list_2 = p.findall(response_2.text)
        print(list_2[0])

        response_3 = requests.get(list_2[0], headers=headers)
        img_name = folder_path + list_2[0][list_2[0].rfind('/'):]
        with open(img_name, 'wb') as file:
            file.write(response_3.content)
        value += 1
        if not value % 10:
            time.sleep(2)
    p = re.compile(r'<a class="next" href="(.*?)">')
    list1 = p.findall(response.text)
    if not list1:
        break
    url = url_path+list1[0]
    print('先让我休息一下 已经下载了{}张图片'.format(value-10))
    time.sleep(2)
    print('爬介个: '+url+'\n')
print('我爬完啦!我下载了{}张图片呢'.format(value-10))






