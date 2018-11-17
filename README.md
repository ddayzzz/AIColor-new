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
## 客户端配置
![Web 客户端支持的浏览器版本](docs/uikiy_support_browsers.jpg)
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