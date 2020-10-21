# coding=utf-8

import time
from io import BytesIO
from PIL import Image


def get_image(source, width=40, height=40, mood=0):
    """
    二进制二维码转化为字符串
    :param source: 源数据
    :param width: 缩放图片大小
    :param height： 缩放图片大小
    :param mood： 0->正常 1->反色
    :return:
    """

    data = BytesIO()
    data.write(source)
    image = Image.open(data)
    image = image.resize((width, height), Image.NEAREST)
    code = ''

    for y in range(height):
        for x in range(width):
            pix = image.getpixel((x, y))
            if mood == 0:
                if pix < 10:
                    code += '██'
                if pix > 200:
                    code += '  '
            else:
                if pix > 200:
                    code += '██'
                if pix < 10:
                    code += '  '
        code += '\n'

    return code


def get_time_stamp() -> int:
    """
    获得时间戳13位
    :return: 时间戳
    """
    t = time.time()
    return int(round(t * 1000))
