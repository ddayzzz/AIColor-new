"""
中间间
"""
from aiohttp import web
import json
import traceback
import logging
from userHandlers import COOKIE_NAME, cookie2user


def auth_factory():

    @web.middleware
    async def auth_middleware(request, handler):
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        user = ''
        if cookie_str:
            if 'deleted' not in cookie_str:
                user = await cookie2user(request.__dbManager__, cookie_str)
            if user:
                logging.debug('从cookies中设置当前的用户: %s' % user.username)
                request.__user__ = user
        return (await handler(request))
    return auth_middleware


def db_factory(dbManager):

    @web.middleware
    async def db_middleware(request, handler):
        request.__dbManager__ = dbManager
        return (await handler(request))
    return db_middleware


# POST 数据上传为JSON的中间件的抽象工厂
def post_json_factory():

    @web.middleware
    async def post_json_middleware(request, handler):
        if request.method == 'POST':
            # 检查HTTP头的Content-Type
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()  # 格式化为JSON
                logging.debug('接受JSON格式数据: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()  # 这个是表格的
                logging.debug('接受的表格: %s' % str(request.__data__))
        return (await handler(request))
    return post_json_middleware


# 响应的抽象工厂
def response_factory():
    """
    用于处理处理器返回的数据，同时对结果、或者错误进行最终的处理
    :return: 返回一个封装的可调用对象
    """

    @web.middleware
    async def response(request, handler):
        try:
            r = await handler(request)  # 等待logger的处理完成
            if isinstance(r, web.Response):
                return r  # 直接返回响应
            if isinstance(r, web.FileResponse):
                return r
            if isinstance(r, web.StreamResponse):
                # 字节流。客户端默认下载的是字节流(header是application/octet-stream)。需要修改请求的类型
                accept_type = request.headers.get('accept')
                if accept_type:
                    last_com = accept_type.find(',')
                    if last_com > 0:
                        r.content_type = accept_type[:last_com]
                return r
            if isinstance(r, bytes):
                resp = web.Response(body=r)
                resp.content_type = 'application/octet-stream'
                return resp
            if isinstance(r, str):
                if r.startswith('redirect:'):
                    return web.HTTPFound(r[9:])
                resp = web.Response(body=r.encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
            if isinstance(r, dict):
                if r.get('__template__'):
                    resp = web.Response(
                        body=request.app.template.get_template(r['__template__']).render(**r).encode('utf-8'))
                    resp.content_type = 'text/html;charset=utf-8'
                    return resp
                else:
                    dictData = {'status': r.get('status', 0), 'data': r}
                    resp = web.Response(
                        body=json.dumps(dictData, ensure_ascii=False, default=lambda o: o.__dict__()).encode('utf-8'))
                    resp.content_type = 'application/json;charset=utf-8'
                    return resp
            if isinstance(r, int) and r >= 100 and r < 600:  # 这个是保留的响应代码。有的可能需要
                return web.Response(status=r)
            # default:
            resp = web.Response(body=str(r).encode('utf-8'))
            resp.content_type = 'text/plain;charset=utf-8'
            return resp
            # 由于 websocket 可能返回特殊的响应，如果这种情况，系统会自动处理
        except web.HTTPNotFound as ne:
            logging.error('{req}:{code}'.format(req=request.path, code=ne.status), exc_info=True)
            return web.Response(status=ne.status, body='Not Found')
        except web.HTTPBadRequest as ne:
            logging.error('{req}:{code}'.format(req=request.path, code=ne.status), exc_info=True)
            return web.Response(status=ne.status, body='Bad Request')
        except web.HTTPForbidden as ne:
            logging.error('{req}:{code}'.format(req=request.path, code=ne.status), exc_info=True)
            return web.Response(status=ne.status, body='Forbidden: Please login before.')
        except web.HTTPMethodNotAllowed as ne:
            logging.error('{req}:{code}'.format(req=request.path, code=ne.status), exc_info=True)
            return web.Response(status=ne.status, body='MethodNotAllowed')
        except Exception as e:
            logging.error('内部错误：', exc_info=True)
            dictData = {'status': 5, 'data': {
                'exception': e.__class__.__name__,
                'traceback': traceback.format_exc(),
                'message': repr(e)
            }}
            resp = web.Response(status=501, body=json.dumps(dictData, ensure_ascii=False).encode('utf-8'))
            resp.content_type = 'application/json;charset=utf-8'
            return resp
    return response  # 处理完成 现在都是Response的对象 接下来就有路由关联的函数处理，也就是ResponseHandler