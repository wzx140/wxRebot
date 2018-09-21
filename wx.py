import json
import random
import time

import requests
import re
from PIL import Image
from pyquery import PyQuery as pq

# 模拟请求头
headers = {'Host': 'wx.qq.com', 'Referer': 'https://wx.qq.com/?&lang=zh_CN', 'Origin': 'https://wx.qq.com',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3534.4 Safari/537.36'}

uuid_url = 'https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb'

# 获取二维码
qr_url = 'https://login.weixin.qq.com/qrcode/{uuid}'

login_url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={uuid}&tip=0'

# 接收信息
rec_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid={sid}&skey={skey}&lang=zh_CN&pass_ticket={pass_ticket}'

# 心跳包
Sync_url = 'https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck?r={r}&skey={skey}&sid={sid}&uin={uin}&deviceid={deviceid}&synckey={synckey}&_={_}'

# 保存cookie的会话
req = requests.Session()

# 开启通知
n_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify?lang=zh_CN&pass_ticket={pass_ticket}'

# send
send_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&pass_ticket={pass_ticket}'

# 获取联系人
contact_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?pass_ticket={pass_ticket}&r={r}&seq=0&skey={skey}'

# 用户信息
info = {}
'''
skey  
sid
uin
pass_ticket
from_user_name  本机用户id
BaseRequest
SyncKey  字典格式
synkey  心跳包请求格式
'''


def login(is_auto_open):
    # 获取二维码地址
    res = req.get(url=uuid_url, headers=headers)
    text = res.content.decode('utf-8')
    pattern = re.compile('"(.+)"')
    uuid = re.findall(pattern, text)[0]

    if is_auto_open:
        res = req.get(url=qr_url.format(uuid=uuid), headers=headers)
        # print(len(res.content))
        with open('temp.jpg', 'wb') as f:
            f.write(res.content)

        im = Image.open('temp.jpg')
        im.show()
    else:
        print('请打开二维码连接：' + qr_url.format(uuid=uuid))

    # 模拟登录
    while (True):
        res = req.get(login_url.format(uuid=uuid), headers=headers)
        text = res.content.decode('utf-8')
        # print(res.url)
        if 'redirect_uri' in text:
            pattern = re.compile('redirect_uri="(.+)"')
            url = re.findall(pattern, text)[0]
            # print(res)
            # print(text)
            if url:
                print('登录成功')
                return url
                # print(url)
        elif 'userAvatar' in text:
            # print(res)
            # print(text)
            print('您已扫码，请点击登录')
            time.sleep(5)
        elif '400' in text:
            print(res)
            print(text)
            print('二维码已过期，请关闭程序，并重新打开')
            time.sleep(1)


def get_user_info(url):
    # 获得信息
    res = req.get(url + '&fun=new&version=v2&lang=zh_CN', headers=headers)
    res.encoding = 'utf-8'
    # print(res.text)

    # 获得信息
    doc = pq(res.text)
    skey = doc('skey').text()
    sid = doc('wxsid').text()
    uin = doc('wxuin').text()
    pass_ticket = doc('pass_ticket').text()

    # DeviceID巨坑，其实是随机生成的,但要不断变化
    BaseRequest = {'uin': uin, 'sid': sid, 'skey': skey, 'DeviceID': 'e' + repr(random.random())[2:17]}
    data = {'BaseRequest': BaseRequest}
    # post的是json格式
    dump_json_data = json.dumps(data)

    res = req.post(
        'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?pass_ticket={pass_ticket}&lang=ch_ZN'.format(
            pass_ticket=pass_ticket),
        headers=headers, data=dump_json_data)

    # 获取key
    json_res = json.loads(res.content.decode('utf-8'))
    SyncKey = json_res['SyncKey']
    synkey = ''
    for key in SyncKey['List']:
        synkey += str(key['Key']) + '_' + str(key['Val']) + '|'
    synkey = synkey[:-1]

    from_user_name = json_res['User']['UserName']

    info['skey'] = skey
    info['sid'] = sid
    info['uin'] = uin
    info['pass_ticket'] = pass_ticket
    info['from_user_name'] = from_user_name
    info['BaseRequest'] = BaseRequest
    info['SyncKey'] = SyncKey
    info['synckey'] = synkey
    # get_key7()
    # info['synckey7'] = synckey7


# 开启通知
def open_notify():
    data = {'BaseRequest': info['BaseRequest'], 'Code': 3, 'FromUserName': info['from_user_name'],
            'ToUserName': info['from_user_name'], 'ClientMsgId': get_time()}
    json_data = json.dumps(data)
    res = req.post(n_url.format(pass_ticket=info['pass_ticket']), headers=headers, data=json_data)
    json_data = json.loads(res.content.decode('utf-8'))
    return json_data['BaseResponse']['Ret']


# 获得时间戳13位
def get_time():
    t = time.time()
    return int(round(t * 1000))


# 发送心跳包，需要循环
def Sync():
    res = req.get(
        Sync_url.format(r=get_time(), skey=info['skey'], sid=info['sid'], uin=info['uin'],
                        deviceid='e' + repr(random.random())[2:17],
                        synckey=info['synckey'], headers=headers, _=get_time()), timeout=60)
    # print(info['synckey'])
    # retcode = synccheck['']
    text = res.content.decode('utf-8')
    # print(info['synckey'])
    # print(text)
    pattern = re.compile('retcode:"(\d+)",selector:"(\d)"')
    retcode, selector = re.findall(pattern, text)[0]
    if retcode == '0':
        print('心跳成功')
        return selector
    else:
        print('心跳失败,若多次失败请重启程序')


# 获取信息以及更新synckey
def get_message():
    data = {'BaseRequest': info['BaseRequest'], 'rr': ~int(time.time()), 'SyncKey': info['SyncKey']}
    dump_json_data = json.dumps(data)
    res = req.post(rec_url.format(sid=info['sid'], skey=info['skey'], pass_ticket=info['pass_ticket']),
                   data=dump_json_data,
                   headers=headers)
    # print(res.content)
    json_data = json.loads(res.content.decode('utf-8'))

    # 更新synckey
    keys = json_data['SyncKey']['List']
    synckey = ''
    for key in keys:
        synckey += str(key['Key']) + '_' + str(key['Val']) + '|'
    synckey = synckey[:-1]
    info['synckey'] = synckey
    info['SyncKey'] = json_data['SyncKey']

    # 获取信息
    AddMsgCount = int(json_data['AddMsgCount'])
    AddMsgList = json_data['AddMsgList']
    if AddMsgCount != 0:
        msg_list = []
        for msg in AddMsgList:
            FromUserName = msg['FromUserName']
            Content = msg['Content']
            if Content == '' and FromUserName == info['from_user_name']:
                print('检测到微信其他端有空操作')

            elif FromUserName == info['from_user_name']:
                print('微信其他端发出消息：' + Content)

            else:
                msg_list.append((FromUserName, Content))
                print('接收到' + str(len(msg_list)) + '个消息')
                return msg_list


def send(message, ToUserName):
    # 这里有个坑，ClientMsgId为，时间戳左移4位随后补上4位随机数
    msg = {'ClientMsgId': int(str(get_time()) + repr(random.random())[2:6]), 'Content': message,
           'FromUserName': info['from_user_name'], 'LocalID': int(str(get_time()) + repr(random.random())[2:6]),
           'ToUserName': ToUserName, 'Type': 1}
    data = {'BaseRequest': info['BaseRequest'], 'Msg': msg, 'Scene': 0}

    # 要这样设置，不然会乱码
    json_dump_data = json.dumps(data, ensure_ascii=False)
    temp_headers = headers
    temp_headers['Content-Type'] = 'application/json;charset=UTF-8'
    res = req.post(send_url, data=json_dump_data.encode('utf-8'), headers=temp_headers)
    json_data = json.loads(res.content.decode('utf-8'))
    # print(json_data)
    if json_data['BaseResponse']['Ret'] == 0:
        print('发送：' + message)
    return json_data['BaseResponse']['Ret']


# 获取联系人
def get_contact():
    # 昵称中表情会乱码
    res = req.get(contact_url.format(pass_ticket=info['pass_ticket'], r=get_time(), skey=info['skey']), headers=headers)
    json_data = json.loads(res.content.decode('utf-8'))
    member_list = json_data['MemberList']
    list = []
    for member in member_list:
        mber = {}
        mber['NickName'] = member['NickName']
        mber['UserName'] = member['UserName']
        list.append(mber)
    return list

# if __name__ == '__main__':
#     url = login()
#     get_user_info(url)
#     ret = open_notify()
#     contact_list = get_contact()
#     if ret == 0:
#         print('开启通知成功')
#         while (True):
#             sel = Sync()
#             if sel == '2':
#                 msg_list = get_message()
#                 # if msg_list:
#                 #     send('实验，勿回', msg_list[0][0])
#                 send('实验，勿回', 'filehelper')
#             time.sleep(2)
#     else:
#         print('开启通知失败')
# print(info['synckey'])
