'''
前几天看了几集斗破苍穹电视剧，突然想重新看看原版小说，奈何只能在网页看，无法下载。
一生气，就把斗破苍穹爬了下来....
'''

import requests
import re
import os

folder_path = 'D:/1/project/car/txt/'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
url_qian = 'https://doupocangqiong1.com'
url = 'https://doupocangqiong1.com/1/20.html'
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
while True:
    p = re.compile(r'<meta name="keywords" content="(.*?)" />')
    list1 = p.findall(response.text)
    p = re.compile(r'<a href="(.*?)" class="btn btn-primary"')
    url_next = p.findall(response.text)
    if list1[0][0] == '第':
        print(list1[0][:list1[0].find(',')])
        p1 = re.compile(r"\$\.get\('(.*?)',{},")
        url_txt = p1.findall(response.text)
        response1 = requests.get(url_qian+url_txt[0], headers=headers).json()
        with open('txt/doupo.txt', 'a') as f:
            f.write(list1[0][:list1[0].find(',')])
            f.write(response1['info'].replace('<br/><br/>', '\n'))
    elif list1[0][0] == '感':
        break
    response = requests.get(url_qian+url_next[0], headers=headers)
