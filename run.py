# coding=utf-8

import logging
import time

from log import setup_logging
from config import target_name, open_mode, inverse_mode, sync_frequency
from wx import login, get_user_info, open_notify, get_contact, sync, get_message, send
from robo import replay


def main():
    setup_logging()
    logger = logging.getLogger("root")

    try:
        url = login(open_mode, inverse_mode)
        get_user_info(url)
        id2name, name2id = get_contact()
        target_id = ''

        # 找到昵称对应id
        if target_name == '1':
            target_id = 'ALL'
        elif target_name in name2id.keys():
            target_id = name2id[target_name]

        if target_id:
            logger.debug('找到目标' + str(target_id))
            open_notify()
            while True:
                sel = sync()
                if sel == '2':
                    # 收到消息
                    msg_list = get_message()
                    if msg_list:
                        for msg in msg_list:
                            logger.info('收到信息 ' + id2name[msg[0]] + '：' + msg[1])
                            if target_id == 'ALL':
                                send(replay(msg[1]), msg[0])
                            elif msg[0] == target_id:
                                send(replay(msg[1]), msg[0])
                time.sleep(sync_frequency)

        else:
            raise RuntimeError('找不到用户：' + target_name)

    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    main()
