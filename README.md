## 微信自动聊天机器人
> python>=3.5

可以实现对特定好友消息的自动回复，若出现报错以及心跳失败的情况，请检查手机上是否已经显示电脑版微信登录，若登录就退出，并重新运行程序

### 参数设定
在`config.py`里修改参数
- `target_name` 自动回复对象的昵称
- `open_mode` 二维码打开模式
    - 0 只显示二维码url
    - 1 控制台打印二维码
    - 2 调用系统图片查看器打开二维码
- `inverse_mode` 二维码打印模式
    - 0
    - 1 反色，因为有的控制台是黑底白字
- `sync_frequency` 心跳频率
- `key` 图灵机器人key
> 注：key为自己申请的图灵key，[申请网址](http://www.tuling123.com/)

### 构建环境
如果使用 anaconda，使用下面任选一种方式即可导入依赖
- 导入包：`conda install --yes --file requirements.txt`
- 或者创建新的环境：`conda create --name <env> --file requirements.txt`

也可以使用pip安装以下依赖
- `pip install requests`
- `pip install pillow`
- `pip install pyquery`
- `pip install pyyaml`

### 运行
`python run.py`
