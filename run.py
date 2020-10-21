# coding=utf-8

from log import setup_logging
from config import target_name, open_mode, inverse_mode, sync_frequency, key
from robot import TuLingRobot
from wx import Wx


def main():
    setup_logging()
    wx = Wx()
    robot = TuLingRobot(key)
    wx.register(robot)
    url = wx.login(open_mode, inverse_mode)
    wx.fetch_user_info(url)
    wx.fetch_contact()
    wx.open_notify()
    wx.run(target_name, sync_frequency)


if __name__ == '__main__':
    main()
