import logging
import sys
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, datefmt='%a, %d %b %Y %H:%M:%S',
                        format='%(name)s: %(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')


import middlewares
from handlers import *
from userHandlers import *
from socialHandlers import *
from onBrowserHandler import *
from filters import *
from aiohttp import web
from bases import RouterCallBack
import dbManager
import argparse


from jinja2 import Environment, FileSystemLoader







parser = argparse.ArgumentParser(description="AIColorizer")
parser.add_argument('--port', default=9999)
parser.add_argument('--addr', default='127.0.0.1')
parser.add_argument('--dbusername', default='aitest')
parser.add_argument('--dbpasswd', default='test123')
parser.add_argument('--dbname', default='aicolor')
parser.add_argument('--dbaddr', default='127.0.0.1')
parser.add_argument('--dbport', default=3306)



# 确保文件夹存在
_essential_dirs = ['./gallery', './gallery/colorized', './gallery/styled', './gallery/upload']
for edir in _essential_dirs:
    if not os.path.exists(edir):
        os.mkdir(edir)


def shutdown_signal_handler(dbManager):
    async def on_shutdown(app):
        await dbManager.close()

    return on_shutdown

def run_server():

    args = parser.parse_args()

    dbm = dbManager.DBManager(username=args.dbusername, password=args.dbpasswd, dbname=args.dbname, host=args.dbaddr, port=args.dbport)
    app = web.Application(middlewares=[middlewares.post_json_factory(),
                                       middlewares.db_factory(dbm),
                                       middlewares.auth_factory(),
                                       middlewares.response_factory()])
    app.add_routes([
        web.post('/api/v1/upload', RouterCallBack(store_upload_images)),
        web.get('/api/v1/getStyled', RouterCallBack(process_styled_image)),
        web.get('/api/v1/getColorized', RouterCallBack(process_colorized_image)),
        web.get('/api/v1/getImage', RouterCallBack(get_imageById)),
        web.get('/upload', RouterCallBack(get_uploadRequest)),
        web.get('/api/v1/getImageItem', RouterCallBack(get_ImageItem)),
        web.get('/api/v1/getModels', RouterCallBack(basic_api_get_userBasedModel))
    ])
    # 用户管理部分
    app.add_routes([
        web.get('/register', RouterCallBack(user_api_get_register)),
        web.post('/api/v1/register', RouterCallBack(user_api_post_register)),
        web.post('/api/v1/authenticate', RouterCallBack(user_api_post_auth)),
        web.get('/signin', RouterCallBack(user_api_get_signin)),
        web.get('/signout', RouterCallBack(user_api_get_signout))
    ])
    # 社交管理
    app.add_routes([
        web.get('/zone', RouterCallBack(social_zone)),
        web.get('/', RouterCallBack(social_flow)),
        web.get('/api/v1/getImages', RouterCallBack(social_api_get_getAllImages)),
        web.get('/api/v1/getComments', RouterCallBack(social_api_get_getComments_inPost)),
        web.post('/api/v1/insertComment', RouterCallBack(social_api_post_insertComment)),
        web.get('/api/v1/getLikes', RouterCallBack(social_api_get_getLikes_inPost)),
        web.post('/api/v1/flipLikeStatus', RouterCallBack(social_api_post_flipLikeStatus)),
        web.get('/api/v1/getImageTimeline', RouterCallBack(social_api_get_getImageTimeline)),
        web.post('/api/v1/createPost', RouterCallBack(social_api_post_createPost)),
        web.get('/api/v1/getPostTimeLine', RouterCallBack(social_api_get_postTimeLine)),
        web.get('/api/v1/getUserLikedPosts', RouterCallBack(social_api_getUserLikeStatus)),
        web.get('/viewPost', RouterCallBack(social_view_post)),
        web.get('/processer', RouterCallBack(social_image_processer))
    ])
    # 浏览器处理
    app.add_routes([
        web.get('/styleChanger', RouterCallBack(browser_get_style_transfer))
    ])
    # 添加静态资源
    app.router.add_static('/static', './static')
    app.router.add_static('/templates', './templates')
    # Jinja2 模板
    kw = dict()  # Jinja2 模板的参数
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )
    env = Environment(loader=FileSystemLoader('./templates'), **options)
    filters = {'datetime': datetime_filter}
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app.template = env
    # 信号
    app.on_shutdown.append(shutdown_signal_handler(dbm))
    web.run_app(app, port=args.port, host=args.addr)

run_server()