# 模拟请求头
HEADERS = {'Host': 'wx.qq.com', 'Referer': 'https://wx.qq.com/?&lang=zh_CN', 'Origin': 'https://wx.qq.com',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3534.4 Safari/537.36'}

UUID_URL = 'https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb'

# 获取二维码
QR_URL = 'https://login.weixin.qq.com/qrcode/{uuid}'

LOGIN_URL = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={uuid}&tip=0'

KEY_URL = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?pass_ticket={pass_ticket}&lang=ch_ZN'

# 接收信息
REC_URL = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid={sid}&skey={skey}&lang=zh_CN&pass_ticket={pass_ticket}'

# 心跳包
SYNC_URL = 'https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck?r={r}&skey={skey}&sid={sid}&uin={uin}&deviceid={deviceid}&synckey={synckey}&_={_}'

# 开启通知
N_URL = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify?lang=zh_CN&pass_ticket={pass_ticket}'

# send
SEND_URL = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&pass_ticket={pass_ticket}'

# 获取联系人
CONTACT_URL = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?pass_ticket={pass_ticket}&r={r}&seq=0&skey={skey}'

# 图灵机器人接口
TULING_URL = 'http://www.tuling123.com/openapi/api?key={key}&info={info}'
