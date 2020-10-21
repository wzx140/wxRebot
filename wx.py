# coding=utf-8

import json
import logging
import random
import requests
import re
from pyquery import PyQuery as pq
from typing import List, Tuple
import robot
from constant import *
from util import *


class Wx(object):

    def __init__(self):
        # 保存cookie的会话
        self.__req = requests.Session()
        # 日志
        self.__logger = logging.getLogger("root")
        # 用户信息
        self.__info = {}
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
        # 联系人信息
        self.__id2name = {}
        self.__name2id = {}
        # 回复机器人
        self.__robots = []

    def register(self, robo: robot) -> None:
        """
        注册机器人
        """
        self.__robots.append(robo)
        self.__logger.debug("register " + robo.__class__.__name__)

    def login(self, open_mode: int, inverse_mode: bool) -> str:
        """
        模拟登录
        :param open_mode: 二维码打开模式
        :param inverse_mode: 二维码打印模式
        :return url
        """

        # 获取二维码地址
        res = self.__req.get(url=UUID_URL, headers=HEADERS)
        res.raise_for_status()

        text = res.content.decode('utf-8')
        pattern = re.compile('"(.+)"')
        uuid = re.findall(pattern, text)[0]
        if not uuid:
            raise ValueError(text)

        res = self.__req.get(url=QR_URL.format(uuid=uuid), headers=HEADERS)
        res.raise_for_status()

        if open_mode == 2:
            im = Image.open(res.content)
            im.show()
        elif open_mode == 1:
            print(get_image(res.content, mood=inverse_mode))
        elif open_mode == 0:
            print('请打开二维码连接：' + QR_URL.format(uuid=uuid))

        self.__logger.debug('登录二维码加载成功')

        # 模拟登录
        while True:
            res = self.__req.get(LOGIN_URL.format(uuid=uuid), headers=HEADERS)
            res.raise_for_status()

            text = res.content.decode('utf-8')
            if 'redirect_uri' in text:
                pattern = re.compile('redirect_uri="(.+)"')
                url = re.findall(pattern, text)[0]
                if url:
                    self.__logger.info('登录成功')
                    return url
                else:
                    raise ValueError(text)
            elif 'userAvatar' in text:
                self.__logger.debug('用户已扫码')
                time.sleep(5)
            elif '400' in text:
                raise RuntimeError('二维码已过期，请重启')

    def fetch_user_info(self, url: str) -> None:
        """
        获取并保存用户信息
        :param url:
        """

        # 获得信息
        res = self.__req.get(url + '&fun=new&version=v2&lang=zh_CN', headers=HEADERS)
        res.raise_for_status()
        res.encoding = 'utf-8'

        doc = pq(res.text)
        skey = doc('skey').text()
        sid = doc('wxsid').text()
        uin = doc('wxuin').text()
        pass_ticket = doc('pass_ticket').text()

        if not (skey and sid and uin and pass_ticket):
            raise ValueError(res.text)

        # DeviceID巨坑，其实是随机生成的,但要不断变化
        base_request = {'uin': uin, 'sid': sid, 'skey': skey, 'DeviceID': 'e' + repr(random.random())[2:17]}
        data = {'BaseRequest': base_request}
        # post的是json格式
        dump_json_data = json.dumps(data)

        res = self.__req.post(KEY_URL.format(pass_ticket=pass_ticket), headers=HEADERS, data=dump_json_data)
        res.raise_for_status()

        # 获取key
        json_res = json.loads(res.content.decode('utf-8'))
        sync_key_all = json_res['SyncKey']

        if not sync_key_all:
            raise ValueError(json_res['SyncKey'])

        sync_key = ''
        for key in sync_key_all['List']:
            sync_key += str(key['Key']) + '_' + str(key['Val']) + '|'
        sync_key = sync_key[:-1]

        from_user_name = json_res['User']['UserName']

        self.__info['skey'] = skey
        self.__info['sid'] = sid
        self.__info['uin'] = uin
        self.__info['pass_ticket'] = pass_ticket
        self.__info['from_user_name'] = from_user_name
        self.__info['BaseRequest'] = base_request
        self.__info['SyncKey'] = sync_key_all
        self.__info['synckey'] = sync_key

        self.__logger.debug('基本信息获取完毕')

    def open_notify(self) -> None:
        """
        开启通知
        """

        data = {'BaseRequest': self.__info['BaseRequest'], 'Code': 3, 'FromUserName': self.__info['from_user_name'],
                'ToUserName': self.__info['from_user_name'], 'ClientMsgId': get_time_stamp()}
        json_data = json.dumps(data)
        res = self.__req.post(N_URL.format(pass_ticket=self.__info['pass_ticket']), headers=HEADERS, data=json_data)
        res.raise_for_status()
        json_data = json.loads(res.content.decode('utf-8'))
        ret = json_data['BaseResponse']['Ret']
        if ret == 0:
            self.__logger.info('开启通知成功')
        else:
            raise RuntimeError('开启通知失败')

    def __sync(self) -> str:
        """
        发送心跳包，需要循环调用以维持连接
        :return: ret_code
        """

        try:
            res = self.__req.get(
                SYNC_URL.format(r=get_time_stamp(), skey=self.__info['skey'], sid=self.__info['sid'],
                                uin=self.__info['uin'],
                                deviceid='e' + repr(random.random())[2:17],
                                synckey=self.__info['synckey'], headers=HEADERS, _=get_time_stamp()), timeout=60)
            res.raise_for_status()

            text = res.content.decode('utf-8')
            pattern = re.compile(r'retcode:"(\d+)",selector:"(\d)"')
            ret_code, selector = re.findall(pattern, text)[0]
            if ret_code == '0':
                self.__logger.debug('心跳成功')
                return selector
            else:
                self.__logger.error('心跳失败')
        except requests.exceptions.RequestException:
            self.__logger.exception('心跳失败')

    def __get_message(self) -> List[Tuple[str, str]]:
        """
        接收消息并更新synckey
        :return: 消息列表
        """

        data = {'BaseRequest': self.__info['BaseRequest'], 'rr': ~int(time.time()), 'SyncKey': self.__info['SyncKey']}
        dump_json_data = json.dumps(data)
        res = self.__req.post(
            REC_URL.format(sid=self.__info['sid'], skey=self.__info['skey'], pass_ticket=self.__info['pass_ticket']),
            data=dump_json_data,
            headers=HEADERS)
        res.raise_for_status()
        json_data = json.loads(res.content.decode('utf-8'))

        # 更新synckey
        keys = json_data['SyncKey']['List']
        synckey = ''
        for key in keys:
            synckey += str(key['Key']) + '_' + str(key['Val']) + '|'
        synckey = synckey[:-1]
        self.__info['synckey'] = synckey
        self.__info['SyncKey'] = json_data['SyncKey']

        # 获取信息
        add_msg_count = int(json_data['AddMsgCount'])
        add_msg_list = json_data['AddMsgList']
        if add_msg_count != 0:
            msg_list: List[Tuple[str, str]] = []
            for msg in add_msg_list:
                from_user_name = msg['FromUserName']
                content = msg['Content']
                if content == '' and from_user_name == self.__info['from_user_name']:
                    self.__logger.debug('检测到微信其他端有空操作')

                elif from_user_name == self.__info['from_user_name']:
                    self.__logger.info('微信其他端发出消息: {message}'.format(message=content))

                else:
                    msg_list.append((from_user_name, content))
                    self.__logger.info('接收到' + str(len(msg_list)) + '个消息')
                    return msg_list

    def __send(self, message: str, to_user_name: str) -> None:
        """
        发送消息
        :param message:
        :param to_user_name:
        """

        if message is None:
            return

        # 这里有个坑，ClientMsgId为，时间戳左移4位随后补上4位随机数
        msg = {'ClientMsgId': int(str(get_time_stamp()) + repr(random.random())[2:6]), 'Content': message,
               'FromUserName': self.__info['from_user_name'],
               'LocalID': int(str(get_time_stamp()) + repr(random.random())[2:6]),
               'ToUserName': to_user_name, 'Type': 1}
        data = {'BaseRequest': self.__info['BaseRequest'], 'Msg': msg, 'Scene': 0}

        # 要这样设置，不然会乱码
        json_dump_data = json.dumps(data, ensure_ascii=False)
        temp_headers = HEADERS
        temp_headers['Content-Type'] = 'application/json;charset=UTF-8'
        res = self.__req.post(SEND_URL, data=json_dump_data.encode('utf-8'), headers=temp_headers)
        res.raise_for_status()

        json_data = json.loads(res.content.decode('utf-8'))
        if json_data['BaseResponse']['Ret'] == 0:
            self.__logger.info('发送给 {name}: {message}'.format(name=self.__id2name.get(to_user_name, to_user_name),
                                                              message=message))
        else:
            self.__logger.error(
                '发送给 {name}: {message} 失败'.format(name=self.__id2name.get(to_user_name, to_user_name),
                                                  message=message))

    def fetch_contact(self):
        """
        获取并缓存联系人
        """

        # 昵称中表情会乱码
        res = self.__req.get(
            CONTACT_URL.format(pass_ticket=self.__info['pass_ticket'], r=get_time_stamp(), skey=self.__info['skey']),
            headers=HEADERS)
        res.raise_for_status()

        json_data = json.loads(res.content.decode('utf-8'))
        member_list = json_data['MemberList']

        if not member_list:
            raise RuntimeError(res.text)

        for member in member_list:
            self.__id2name[member['UserName']] = member['NickName']
            self.__name2id[member['NickName']] = member['UserName']

    def run(self, target_name: str, sync_frequency: int):
        try:
            target_id = ''

            # 找到昵称对应id
            if target_name is None:
                target_id = 'ALL'
            elif target_name in self.__name2id.keys():
                target_id = self.__name2id[target_name]

            if target_id:
                self.__logger.debug('找到目标' + str(target_id))
                while True:
                    ret_code = self.__sync()
                    if ret_code == '2':
                        # 收到消息
                        msg_list = self.__get_message()
                        if msg_list:
                            for user_id, content in msg_list:
                                self.__logger.info('收到信息 ' + self.__id2name.get(user_id, user_id) + '：' + content)
                                if user_id in ['ALL', target_id]:
                                    # 调用所有机器人
                                    for robo in self.__robots:
                                        self.__send(robo.reply(content), user_id)

                    time.sleep(sync_frequency)

            else:
                raise RuntimeError('找不到用户：' + target_name)

        except Exception as e:
            self.__logger.exception(e)
