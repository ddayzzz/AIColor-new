# AIColor
## 文件夹
- `docs`：开发文档和配置脚本
- `gallery`：运行时产生，用户上传、风格化以及彩色化的图片文件夹
- `genColorForAnimation`：采用 `Animation` 模型的彩色化功能模块
- `static`：服务器的静态资源
- `styleChanger`：在线风格化功能模块
- `templates`：`jinja2` 模板文件以
- `templates\genStyleOnBrowser`：离线的风格化处理功能模块
- `templates\errors`：出错处理模板文件
## 文件
- `bases.py`：基本功能中使用的各种通用函数和常量定义
- `colorInterface.py`：彩色化的颜色转换功能接口
- `dbManager.py`：数据管理功能
- `filter.py`：jinja2 模板渲染过程中使用的过滤器
- `handlers.py`：基本的请求处理路由
- `middlewares.py`：Http请求的中间件
- `models.py`：ORM 关系模型的数据表项到数据模型的映射关系
- `onBrowserHandler.py`：离线处理的相关模块
- `orm.py`：ORM 实现的基础元类、数据域等相关定义
## API部分
- [基本API](docs/APIs.md)
- [模型获取相关API](docs/modelAPIs.md)
- [用户管理与控制API](docs/User%20manager%20APIs.md)
## 服务端配置
- 数据库：[建立数据库](docs/How%20to%20install%20colorize%20module.md)
- 模型下载：
1. 下载彩色化模型：运行 `genColor/download_color_imagenet_model.sh` 和 `genColor/download_color_model.sh`
2. 离线风格化模块：位于 `templates/genStyleOnBrowser/pretrained` 目录下
3. 服务端命令行：`webServer.py --<option>`

开关|意义|是否必要|默认值|示例
-|-|-|-|-
port|服务端绑定的端口|否|9999|9999
addr|服务端绑定的IP|否|127.0.0.1|1.2.3.4
dbusername|数据的登录名|否|aitest|myname
dbpasswd|数据登录密码|否|test123|test123
dbname|数据库名|否|aicolor|mydb
dbaddr|数据服务器监听的地址|否|127.0.0.1|127.0.0.1
dbport|数据服务器监听的端口|否|3306|3306(MySQL)
4. 建议在服务端上使用 Docker 进行，我们已经做好了配置：
- [链接：https://pan.baidu.com/s/1KzlWS_DOy04Z9H0QNceLyQ](https://pan.baidu.com/s/1KzlWS_DOy04Z9H0QNceLyQ)，提取码：`rv74`
- Docker 运行命令行：`docker run -d -p 9999:9999 -v /path/to/AIColor:/root/AIColor -w /root/AIColor shu/torch7 python3 webServer.py --port=9999 --addr=0.0.0.0 --dbaddr=172.17.0.1 --python_exec=/usr/bin/python3`

## 客户端配置
![Web 客户端支持的浏览器版本](docs/uikiy_support_browsers.jpg)
- 离线风格化需要支持 `Tensorflow.js` 的浏览器版本，具体[参见](https://js.tensorflow.org/#getting-started)
- 在使用过程需要从服务器中加载模型。
## 模型训练

#### 使用的框架
- 图像预测及输出：Tensorflow.js
- 前端框架：uikit
- 异步请求发起：axios.js
- MVVM 框架：Vue.js 
# 系统环境
- CUDA（可选，需要使用 GPU）
- Torch7（Torch7 用于彩色化）
- Lua

# 需要的 Python 库
- 异步 http 服务框架：aiohttp
- 异步数据库访问库：aiomysql
- Tensorflow
- Keras
- Chainer
- cupy
- lutorpy
- 模板引擎：jinja2