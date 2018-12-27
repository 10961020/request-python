#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# author: zhangtong
'''
2018-05-08
学习爬虫之后唯一一个拿得出手的爬虫脚本吧 红红火火恍恍惚惚
参考内容 https://blog.csdn.net/nonoroya_zoro/article/details/80108722  
脚本演示视频网址 https://weibo.com/tv/v/GfGnskP5d?fid=1034:4a0f4e88b659eedd7e56a6ae0ec49002
手动输入验证码 比如 8个照片 第3，4为正确选项 输入 2，3 即可 （12306验证模块以0开头 0-7 不是 1-8）
输入账号密码登入 （源码你都看的到 盗不了你的号）
输入起始点，抵达点 可以查票
输入车次 座位 乘车人名称 即可买票成功 
成功后可以去12306官网个人中心->火车票订票->未完成订单中查看

PS:验证码图片下载后弹出的方式有点不太友好 懒得改了 可以选择配合matplotlib展示，或者使用cv2 反正我是懒得改了
    没写循环 输入错误就直接退出 没加优化 只是为了练手
'''
import requests
from PIL import Image
from requests.packages import urllib3

# response = requests.get('http://httpbin.org/get')
# print(response.status_code)
# print(response.text)
# print(response.cookies)

stationNameToCode = dict()  # 始发站
stationCodeToName = dict()  # 终点站
trainDate = ''              # 乘车时间
fromStationName = ''
fromStationCode = ''        # 出发编码
toStationName = ''
toStationCode = ''          # 到达编码
fromStationTelecode = ''    # 要坐的站
toStationTelecode = ''      # 要到的站
trainSecretStr = ''         # 预定时要用
trainNo = ''                # 不知道什么串加车次
trainCode = ''              # 车次
leftTicket = ''             # leftTicket 12
seatType = ''               # 硬座 1 硬卧 3 软卧 4
trainLocation = ''          # trainLocation 15
submitToken = ''            # 提交令牌
passengerTicketStr = ''
oldPassengerStr = ''
orderId = ''
head = {
    'Host': 'kyfw.12306.cn',
    'Origin' : 'https://kyfw.12306.cn',
    'X-Requested-With' : 'XMLHttpRequest',
    'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer' : 'https://kyfw.12306.cn/otn/login/init',
    'Accept': '*/*',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Accept-Language' : 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}
session = requests.Session()
session.verify = False
urllib3.disable_warning()


def getlist(go, to):
    train_date = input('输入出发的时间(如 2018-04-20):')
    response = session.get('https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(train_date, go, to)).read().decode('utf-8')
    getlist_dict = response.json()['data']['result']
    return getlist_dict


def get_city_id():
    response = session.get('https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9051').read().decode('utf-8')
    from_station = input('输入出发城市(如 北京):')
    to_station = input('输入到达城市(如 永济):')
    id_list = response.text.split('|')
    return id_list[id_list.index(from_station)+1], id_list[id_list.index(to_station)+1]


def inquiry():
    a = {'车次': 3, '出发时间': 8, '到达时间': 9, '历时': 10, '商务座': 32, '一等座': 31, '二等座': 30, '软卧': 23, '硬卧': 28, '硬座': 29, '无座': 26}
    go, to = get_city_id()
    html = getlist(go, to)
    print(html)
    for i in range(len(html)):
        tmp_list = html[i].split('|')
        for k, j in a.items():
            print(k, tmp_list[j])
        print('~~~~~~~~~~~~~~~~~~~~~~~')


def login():
    print('~~~开始登入~~~')
    username = input('输入账号:')
    password = input('输入密码:')
    data = {'username': username, 'password': password, 'appid': 'oth'}
    response = session.post('https://kyfw.12306.cn/passport/web/login', headers=head, data=data)
    print(response.json())


def download_code():
    print('~~~下载验证码图片~~~')
    response = session.get('https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand')
    with open('test.jpg', 'wb') as f:
        f.write(response.content)
        f.close()
    image = Image.open('test.jpg', 'r')
    image.show()
    captcha_solution = input('请输入验证码对应序号，以","分割[例如2,5]:')
    image.close()
    return captcha_solution


def yanzheng(captcha_solution):
    so_lu = captcha_solution.split(',')
    yan_sol = ['0,0', '39,42', '115,45', '187,45', '262,45', '44,114', '104,114', '176,121', '257,119']
    yan_list = []
    for i in so_lu:
        yan_list.append(yan_sol[int(i)])
    yan_str = ','.join(yan_list)
    data = {'answer': yan_str, 'login_site': 'E', 'rand': 'sjrand'}
    response = session.post('https://kyfw.12306.cn/passport/captcha/captcha-check', headers=head, data=data).json()
    print('~~~' + response['result_message'] + '~~~')
    return response['result_code']


if __name__ == '__main__':
    i = yanzheng(download_code())
    if int(i) == 4:
        login()
