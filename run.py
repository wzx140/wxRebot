# coding=utf-8

from argparse import ArgumentParser
from log import setup_logging
from robot import LocalRobot, TuLingRobot
from wx import Wx

if __name__ == '__main__':
    # 解析参数
    parser = ArgumentParser(description='wx聊天机器人')
    parser.add_argument('--sync_frequency', type=int, default=5, help='心跳频率, 越大机器人回复的越慢')
    parser.add_argument('--target_name', type=str, default=None, help="只对此人自动回复，昵称(不是微信号)中不能包含表情，默认为对所有人自动回复")
    parser.add_argument('--open_mode', type=int, choices=[0, 1, 2], default=0, help='二维码打开方式')
    parser.add_argument('--inverse_mode', type=bool, default=False, help='是否反色')
    parser.add_argument('--key', type=str, default=None, help='图灵机器人key')
    args = vars(parser.parse_args())

    setup_logging()
    wx = Wx()
    robot = LocalRobot()
    # robot = TuLingRobot(args['open_mode'])
    # todo 动态注册机器人
    wx.register(robot)
    url = wx.login(args['open_mode'], args['inverse_mode'])
    wx.fetch_user_info(url)
    wx.fetch_contact()
    wx.open_notify()
    wx.run(args['target_name'], args['sync_frequency'])
