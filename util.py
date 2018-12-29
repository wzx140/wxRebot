from PIL import Image


def get_image(data, width=40, height=40, mood=0):
    """
    二进制二维码转化为字符串
    :param data: 源
    :param width: 缩放图片大小
    :param height： 缩放图片大小
    :param mood： 0->正常 1->反色
    :return:
    """
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
