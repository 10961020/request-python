# !/usr/bin/python
# encoding: utf-8
# author: zhangtong
'''
    爬取汽车之家图片
'''
import requests
import re
import os
import time

folder_path = 'D:/1/project/car/photo/'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
url = 'https://car.autohome.com.cn/AsLeftMenu/As_LeftListNew.ashx?typeId=2%20&brandId=0%20&fctId=0%20&seriesId=0'
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
p = re.compile(r"<a href='/pic/brand-(\d+?).html'>")
list1 = p.findall(response.text)
for i in list1:
    url_num2 = 'https://car.autohome.com.cn/pic/brand-{}.html'.format(i)
    response_2 = requests.get(url_num2, headers=headers)
    p_2 = re.compile(r'<div><span class="fn-left"><a href="(.*?)"')
    list_2 = p_2.findall(response_2.text)
    for j in list_2:
        url_num3 = 'https://car.autohome.com.cn' + j[:j.find('.')] + '-1.html'
        response_3 = requests.get(url_num3, headers=headers)
        p_3 = re.compile(r'target="_blank"><img src="(.*?)"')
        list_3 = p_3.findall(response_3.text)
        for y in list_3:
            url_num4 = 'https:' + y[:y.find('t_')] + y[y.find('t_')+2:]
            response_4 = requests.get(url_num4, headers=headers)

            img_name = folder_path + y[y.find('_'):]
            with open(img_name, 'wb') as file:
                file.write(response_4.content)
        time.sleep(1)
        print('~~~~~~~~~~~~~~~我没死')
