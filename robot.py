# coding=utf-8

import logging
import os
import requests
import json
from constant import TULING_URL
from abc import ABCMeta, abstractmethod
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer


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
        if key is None:
            raise RuntimeError("未指定图灵机器人key")
        self.__key = key

    def filter(self, msg: str) -> bool:
        return True

    def get_reply(self, msg: str) -> str:
        res = requests.get(TULING_URL.format(key=self.__key, info=msg))
        res.encoding = 'utf-8'
        jd = json.loads(res.text)
        return jd['text']


class LocalRobot(Robot):
    def __init__(self):
        train = not os.path.exists('db.sqlite3')
        self.__logger = logging.getLogger("root")
        self.__chat_bot = ChatBot("robot")
        if train:
            self.__logger.debug("开始训练LocalRobot")
            trainer = ChatterBotCorpusTrainer(self.__chat_bot)
            trainer.train("chatterbot.corpus.chinese")

    def filter(self, msg: str) -> bool:
        return True

    def get_reply(self, msg: str) -> str:
        return str(self.__chat_bot.get_response(msg))
