## 微信自动聊天机器人
> python>=3.5

可以实现对特定好友消息的自动回复，**若出现报错，心跳失败，长期未出现心跳成功或者无法接受消息的情况，请先在手机上退出电脑版微信登录并重新运行程序**

### 如何使用
```bash
usage: run.py [-h] [--sync_frequency SYNC_FREQUENCY]
              [--target_name TARGET_NAME] [--open_mode {0,1,2}]
              [--inverse_mode INVERSE_MODE] [--key KEY]

wx聊天机器人

optional arguments:
  -h, --help            show this help message and exit
  --sync_frequency SYNC_FREQUENCY
                        心跳频率, 越大机器人回复的越慢, 默认5
  --target_name TARGET_NAME
                        只对此人自动回复，昵称(不是微信号)中不能包含表情，默认为对所有人自动回复
  --open_mode {0,1,2}   二维码打开方式，默认0。0 只显示二维码url；1 控制台打印二维码；2 调用系统图片查看器打开二维码
  --inverse_mode INVERSE_MODE
                        是否反色(二维码), 默认false
  --key KEY             图灵机器人key
```
> [图灵key申请网址](http://www.tuling123.com/)

### 自定义机器人
已经实现了调用[ChatterBot](https://github.com/gunthercox/ChatterBot) 的本地机器人(效果较差)和调用图灵api的机器人(效果较好但有每天次数限制)。

如要实现自己的机器人，需要在[robot.py](robot.py)下继承`Robot`并在[run.py](run.py)中注册此机器人。注册多个机器人会导致重复发送消息
```python
# robot.py
class ExampleRobot(Robot):
    def filter(self, msg: str) -> bool:
        return True

    def get_reply(self, msg: str) -> str:
        return msg.replace('吗', '').replace('？', '！')

# run.py
example_robot = ExampleRobot()
wx.register(example_robot)
```


### 构建环境
```bash
pip install -r requirement.txt
```

### 运行
```bash
python run.py --target_name xx
```
