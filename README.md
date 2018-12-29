## 微信自动聊天机器人
> python>=3.5

可以实现对特定好友消息的自动回复

### 参数设定
在`config.py`里修改参数
- `target_name` 自动回复对象的昵称
- `open_mode` 二维码打开模式
- `key` 图灵机器人key
> 注：key为自己申请的图灵key，[申请网址](http://www.tuling123.com/)

### 控制台打印二维码
此为实验功能，在`config.py`里修改`open_mode = 2`即可开启，实际效果由终端文字显示效果决定
> 若终端为黑底白字可修改 `inverse_mode = 1`

### 构建
#### pipenv
`pipenv install`  
`pipenv run run.py`
#### pip
`pip3 install requests`
`pip3 install pillow`
`pip3 install pyquery`

### 运行
`python run.py`
> 注：若出现报错以及心跳失败的情况，请检查手机上是否已经显示电脑版微信登录，若登录就退出，并重新运行程序

### 持久化
将 INFO 以上信息写入工程目录下 *log.txt* 文件
