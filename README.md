## 微信自动聊天机器人

- 对特定好友消息的自动回复
- 加载自定义回复机器人
- **若出现报错，心跳失败，长期未出现心跳成功或者无法接受消息的情况，请先在手机上退出电脑版微信登录等待一段时间并重新运行程序**

### 如何使用
```bash
usage: run.py [-h] [--sync_frequency SYNC_FREQUENCY]
              [--target_name TARGET_NAME] [--open_mode {0,1,2}]
              [--inverse_mode INVERSE_MODE] [--robot ROBOT [ROBOT ...]]
              [--key KEY]

wx聊天机器人

optional arguments:
  -h, --help            show this help message and exit
  --sync_frequency SYNC_FREQUENCY
                        心跳频率, 越大机器人回复的越慢
  --target_name TARGET_NAME
                        只对此人自动回复, 昵称(不是微信号)中不能包含表情, 默认为对所有人自动回复
  --open_mode {0,1,2}   二维码打开方式: 0.url; 1.console, 2.img
  --inverse_mode INVERSE_MODE
                        控制台打印二维码是否反色
  --robot ROBOT [ROBOT ...]
                        自定义回复机器人类名
  --key KEY             图灵机器人key

```
[图灵key申请网址](http://www.tuling123.com/)



- `open_mode`默认为0，在控制台中打印二维码的url
- `open_mode`若为1，则在控制台打印二维码，需要在`inverse_mode`中指定true或者false，这是因为有的控制台是黑底白字的，打印的二维码需要反色
- `open_mode`若为2，则自动调用系统默认图片查看器打开二维码

### 自定义机器人
已经实现了调用[ChatterBot](https://github.com/gunthercox/ChatterBot) 的本地机器人(效果较差)和调用图灵api的机器人(效果较好但有每天次数限制)。

如要实现自己的机器人，需要在[robot.py](robot.py)下继承`Robot`
```python
# robot.py
class ExampleRobot(Robot):
    def filter(self, msg: str) -> bool:
        return True

    def get_reply(self, msg: str) -> str:
        return msg.replace('吗', '').replace('？', '！')
```
运行时通过`--robot`选项指定机器人类名。注册多个机器人会触发多个机器人的回复信息
```bash
python -m run --robot ExampleRobot
```

### 构建环境
```bash
pip install -r requirements.txt
python -m spacy download en
```

### 运行
```bash
python run.py --target_name xx
```
