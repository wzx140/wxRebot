
import requests
import json
from config import key

url = 'http://www.tuling123.com/openapi/api?key={key}&info={info}'


def replay(msg):
    # info = urllib.parse.urlencode(msg)
    res = requests.get(url.format(key=key, info=msg))
    res.encoding = 'utf-8'
    jd = json.loads(res.text)
    return jd['text']


if __name__ == '__main__':
    replay('哈哈')
