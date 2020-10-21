# coding=utf-8

import requests
import json
from constant import TULING_URL
from abc import ABCMeta, abstractmethod


class Robot(metaclass=ABCMeta):
    @abstractmethod
    def filter(self, msg: str) -> bool:
        """
        过滤需要回复的信息
        """
        pass

    @abstractmethod
    def get_reply(self, msg: str) -> str:
        """
        回复信息
        """
        pass

    def reply(self, msg: str) -> str:
        """
        回复信息
        """
        if self.filter(msg):
            return self.get_reply(msg)


class TuLingRobot(Robot):
    def __init__(self, key: str):
        self.__key = key

    def filter(self, msg: str) -> bool:
        return True

    def get_reply(self, msg: str) -> str:
        res = requests.get(TULING_URL.format(key=self.__key, info=msg))
        res.encoding = 'utf-8'
        jd = json.loads(res.text)
        return jd['text']
