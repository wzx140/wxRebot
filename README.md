## 微信自动聊天机器人
> python>=3.5

可以实现对特定好友消息的自动回复

### 参数设定
在config.py里修改参数
- `target_name` 自动回复对象的昵称
- `is_auto_open` 是否自动打开二维码
- `key` 图灵机器人
> 注：key为自己申请的图灵key，[申请网址](http://www.tuling123.com/)

### 构建与运行
#### pipenv
`pipenv install`  
`pipenv run run.py`
#### pip
`pip3 install requests`
`pip3 install pillow`
`pip3 install pyquery`

### 运行
`python run.py`
> 注：若出现报错以及失败的情况，请检查手机上是否已经显示电脑版微信登录，若登录就退出，并重新运行程序，