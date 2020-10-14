# coding=utf-8

import json
import logging
import random
import time
from io import BytesIO
import requests
import re
from PIL import Image
from pyquery import PyQuery as pq
from util import get_image

# 模拟请求头
headers = {'Host': 'wx.qq.com', 'Referer': 'https://wx.qq.com/?&lang=zh_CN', 'Origin': 'https://wx.qq.com',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3534.4 Safari/537.36'}

uuid_url = 'https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb'

# 获取二维码
qr_url = 'https://login.weixin.qq.com/qrcode/{uuid}'

login_url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={uuid}&tip=0'

key_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?pass_ticket={pass_ticket}&lang=ch_ZN'

# 接收信息
rec_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid={sid}&skey={skey}&lang=zh_CN&pass_ticket={pass_ticket}'

# 心跳包
Sync_url = 'https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck?r={r}&skey={skey}&sid={sid}&uin={uin}&deviceid={deviceid}&synckey={synckey}&_={_}'

# 保存cookie的会话
req = requests.Session()

logger = logging.getLogger("root")

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


def login(open_mode, mode):
    try:
        # 获取二维码地址
        res = req.get(url=uuid_url, headers=headers)
        res.raise_for_status()

        text = res.content.decode('utf-8')
        pattern = re.compile('"(.+)"')
        uuid = re.findall(pattern, text)[0]
        if not uuid:
            raise RuntimeError(uuid_url + ' 规则改变')

        res = req.get(url=qr_url.format(uuid=uuid), headers=headers)
        res.raise_for_status()

        data = BytesIO()
        data.write(res.content)

        if open_mode == 2:
            im = Image.open(data)
            im.show()
        elif open_mode == 1:
            print(get_image(data, mood=mode))
        elif open_mode == 0:
            print('请打开二维码连接：' + qr_url.format(uuid=uuid))

        logger.debug('登录二维码加载成功')

        # 模拟登录
        while True:
            res = req.get(login_url.format(uuid=uuid), headers=headers)
            res.raise_for_status()

            text = res.content.decode('utf-8')
            if 'redirect_uri' in text:
                pattern = re.compile('redirect_uri="(.+)"')
                url = re.findall(pattern, text)[0]
                if url:
                    logger.info('登录成功')
                    return url
                else:
                    raise RuntimeError(url + '规则改变')
            elif 'userAvatar' in text:
                logger.debug('用户已扫码')
                time.sleep(5)
            elif '400' in text:
                raise RuntimeError('二维码已过期，请重启')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(e, e.request.url + ' 访问失败')


def get_user_info(url):
    try:
        # 获得信息
        res = req.get(url + '&fun=new&version=v2&lang=zh_CN', headers=headers)
        res.raise_for_status()
        res.encoding = 'utf-8'

        doc = pq(res.text)
        skey = doc('skey').text()
        sid = doc('wxsid').text()
        uin = doc('wxuin').text()
        pass_ticket = doc('pass_ticket').text()

        if not (skey and sid and uin and pass_ticket):
            raise RuntimeError(url + ' 规则改变')

        # DeviceID巨坑，其实是随机生成的,但要不断变化
        base_request = {'uin': uin, 'sid': sid, 'skey': skey, 'DeviceID': 'e' + repr(random.random())[2:17]}
        data = {'BaseRequest': base_request}
        # post的是json格式
        dump_json_data = json.dumps(data)

        res = req.post(key_url.format(pass_ticket=pass_ticket), headers=headers, data=dump_json_data)
        res.raise_for_status()

        # 获取key
        json_res = json.loads(res.content.decode('utf-8'))
        sync_key_all = json_res['SyncKey']

        if not sync_key_all:
            raise RuntimeError(key_url.format(pass_ticket=pass_ticket) + ' 规则改变')

        sync_key = ''
        for key in sync_key_all['List']:
            sync_key += str(key['Key']) + '_' + str(key['Val']) + '|'
        sync_key = sync_key[:-1]

        from_user_name = json_res['User']['UserName']

        info['skey'] = skey
        info['sid'] = sid
        info['uin'] = uin
        info['pass_ticket'] = pass_ticket
        info['from_user_name'] = from_user_name
        info['BaseRequest'] = base_request
        info['SyncKey'] = sync_key_all
        info['synckey'] = sync_key

        logger.debug('基本信息获取完毕')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(e, e.request.url + ' 访问失败')


# 开启通知
def open_notify():
    try:
        data = {'BaseRequest': info['BaseRequest'], 'Code': 3, 'FromUserName': info['from_user_name'],
                'ToUserName': info['from_user_name'], 'ClientMsgId': get_time()}
        json_data = json.dumps(data)
        res = req.post(n_url.format(pass_ticket=info['pass_ticket']), headers=headers, data=json_data)
        res.raise_for_status()
        json_data = json.loads(res.content.decode('utf-8'))
        ret = json_data['BaseResponse']['Ret']
        if ret == 0:
            logger.info('开启通知成功')
        else:
            raise RuntimeError('开启通知失败')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(e, e.request.url + ' 访问失败')


# 获得时间戳13位
def get_time():
    t = time.time()
    return int(round(t * 1000))


# 发送心跳包，需要循环
def sync():
    try:
        res = req.get(
            Sync_url.format(r=get_time(), skey=info['skey'], sid=info['sid'], uin=info['uin'],
                            deviceid='e' + repr(random.random())[2:17],
                            synckey=info['synckey'], headers=headers, _=get_time()), timeout=60)
        res.raise_for_status()

        text = res.content.decode('utf-8')
        pattern = re.compile(r'retcode:"(\d+)",selector:"(\d)"')
        ret_code, selector = re.findall(pattern, text)[0]
        if ret_code == '0':
            logger.debug('心跳成功')
            return selector
    except requests.exceptions.RequestException:
        logger.error('心跳失败')


# 获取信息以及更新synckey
def get_message():
    try:
        data = {'BaseRequest': info['BaseRequest'], 'rr': ~int(time.time()), 'SyncKey': info['SyncKey']}
        dump_json_data = json.dumps(data)
        res = req.post(rec_url.format(sid=info['sid'], skey=info['skey'], pass_ticket=info['pass_ticket']),
                       data=dump_json_data,
                       headers=headers)
        res.raise_for_status()
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
        add_msg_count = int(json_data['AddMsgCount'])
        add_msg_list = json_data['AddMsgList']
        if add_msg_count != 0:
            msg_list = []
            for msg in add_msg_list:
                from_user_name = msg['FromUserName']
                content = msg['Content']
                if content == '' and from_user_name == info['from_user_name']:
                    logger.debug('检测到微信其他端有空操作')

                elif from_user_name == info['from_user_name']:
                    logger.info('微信其他端发出消息：' + content)

                else:
                    msg_list.append((from_user_name, content))
                    logger.info('接收到' + str(len(msg_list)) + '个消息')
                    return msg_list
    except requests.exceptions.RequestException as e:
        raise RuntimeError(e, e.request.url + ' 访问失败')


def send(message, to_user_name):
    try:
        # 这里有个坑，ClientMsgId为，时间戳左移4位随后补上4位随机数
        msg = {'ClientMsgId': int(str(get_time()) + repr(random.random())[2:6]), 'Content': message,
               'FromUserName': info['from_user_name'], 'LocalID': int(str(get_time()) + repr(random.random())[2:6]),
               'ToUserName': to_user_name, 'Type': 1}
        data = {'BaseRequest': info['BaseRequest'], 'Msg': msg, 'Scene': 0}

        # 要这样设置，不然会乱码
        json_dump_data = json.dumps(data, ensure_ascii=False)
        temp_headers = headers
        temp_headers['Content-Type'] = 'application/json;charset=UTF-8'
        res = req.post(send_url, data=json_dump_data.encode('utf-8'), headers=temp_headers)
        res.raise_for_status()

        json_data = json.loads(res.content.decode('utf-8'))
        if json_data['BaseResponse']['Ret'] == 0:
            logger.info('发送：' + message)
        else:
            logger.error(message + '发送失败')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(e, e.request.url + ' 访问失败')


# 获取联系人
def get_contact():
    # 昵称中表情会乱码
    res = req.get(contact_url.format(pass_ticket=info['pass_ticket'], r=get_time(), skey=info['skey']), headers=headers)
    res.raise_for_status()

    json_data = json.loads(res.content.decode('utf-8'))
    member_list = json_data['MemberList']

    if not member_list:
        raise RuntimeError(
            contact_url.format(pass_ticket=info['pass_ticket'], r=get_time(), skey=info['skey']) + ' 规则改变')

    id2name = {}
    name2id = {}
    for member in member_list:
        id2name[member['UserName']] = member['NickName']
        name2id[member['NickName']] = member['UserName']

    return id2name, name2id
