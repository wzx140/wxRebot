# coding=utf-8
import time

import log
from config import target_name, open_mode,inverse_mode
from wx import login, get_user_info, open_notify, get_contact, Sync, get_message, send
from robo import replay


def get_nick_name(user_name, contact_list):
    nick_name = ''
    for contact in contact_list:
        if contact['UserName'] == user_name:
            nick_name = contact['NickName']
    if nick_name:
        return nick_name
    else:
        return '未知联系人'


def main():
    try:
        url = login(open_mode,inverse_mode)
        get_user_info(url)
        contact_list = get_contact()
        target_id = ''

        if target_name == '1':
            target_id = 'ALL'
        else:
            for contact in contact_list:
                if contact['NickName'] == target_name:
                    target_id = contact['UserName']

        if target_id:
            log.log_debug('找到目标' + str(target_id))
            open_notify()
            while (True):
                sel = Sync()
                if sel == '2':
                    msg_list = get_message()
                    if msg_list:
                        for msg in msg_list:
                            log.log_info('收到信息 ' + get_nick_name(msg[0], contact_list) + '：' + msg[1])
                            if target_id == 'ALL':
                                send(replay(msg[1]), msg[0])
                            elif msg[0] == target_id:
                                send(replay(msg[1]), msg[0])
                    # send('实验，勿回', 'filehelper')
                time.sleep(5)

        else:
            raise RuntimeError('找不到用户：' + target_name)
    except Exception as e:
        log.log_exception(e)


if __name__ == '__main__':
    main()
