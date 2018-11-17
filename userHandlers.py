
import re
import hashlib
from aiohttp import web
import json
import time
from models import User
import logging


COOKIE_NAME = 'aicolor_session'
_COOKIE_KEY = 'welcome_aicolor'


_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')  # 通常表现为40位的十六进制





# 计算加密cookie:
def _user2cookie(user, max_age):
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.username, user.passwd, expires, _COOKIE_KEY)
    L = [user.username, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


# 解密cookie:
async def cookie2user(dbm, cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    L = cookie_str.split('-')
    if len(L) != 3:
        return None
    username, expires, sha1 = L
    if int(expires) < time.time():
        return None
    user = await dbm.query(User, username=username)
    if user is None:
        return None
    s = '%s-%s-%s-%s' % (username, user.passwd, expires, _COOKIE_KEY)
    if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
        logging.debug('无效的SHA1信息')
        return None
    user.passwd = '******'
    return user


async def _create(dbm, username, password_hash):
    if not username or not username.strip() or len(username) > 50:
        raise ValueError('无法创建用户：用户名称无效')
    if not password_hash or not _RE_SHA1.match(password_hash):
        raise ValueError('无法创建用户：密码格式无效')
    users = await dbm.queryAll(User, 'username=?', (username,))
    if len(users) > 0:
        raise ValueError('注册失败', '用户名', '“' + username + '”已经被使用')
    sha1_passwd = '%s:%s' % (username, password_hash)
    user = User(username=username.strip(), passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest())

    await dbm.insert(user)
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, _user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '*******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


async def _authenticate(dbm, username, passwd):
    if not username or len(username) > 50:
        raise ValueError('用户名', '非法的用户名')
    if not passwd:
        raise ValueError('密码', '密码错误')
    users = await dbm.queryAll(User, 'username=?', (username, ))
    if len(users) == 0:
        raise ValueError('用户名', '用户名"%s"不存在' % username)
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.username.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise ValueError('密码', '密码错误')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, _user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


async def user_api_get_signin(redirect='/', message='欢迎登录AIColor，登录AIColor将允许您管理您的文件以及与其他用户进行交互。'):
    return {'__template__': 'signin.html', 'redirect': redirect, 'message': message}


async def user_api_get_signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/signin')  # 设置跳转页面
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.debug("用户退出登陆")
    return r



# post!
async def user_api_post_register(request, username, passwd_hash):
    dbm = request.__dbManager__
    return await _create(dbm, username, passwd_hash)


# get!
async def user_api_get_register(redirect='/zone'):
    return {'__template__': 'register.html', 'redirect': redirect}

# post
async def user_api_post_auth(request, username, passwd):
    dbm = request.__dbManager__
    return await _authenticate(dbm, username, passwd)
