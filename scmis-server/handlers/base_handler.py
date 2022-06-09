

import json

from tornado.web import RequestHandler
from utils.exception import NoResultError
from utils.commons import row_to_obj
from utils.response_code import RET
from utils.session import Session


class BaseHandler(RequestHandler):
    """自定义基类"""

    def __init__(self, application, request, **kwargs):
        self.json_args = {}
        self.session = None
        super().__init__(application, request, **kwargs)

    @property
    def db(self):
        """作为RequestHandler对象的db属性"""
        return self.application.db

    @property
    def redis(self):
        """作为RequestHandler对象的redis属性"""
        return self.application.redis

    def prepare(self):
        """预解析json数据"""
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
            print(self.json_args)

#    def set_default_headers(self):
#        """设置默认json格式"""
#        self.set_header("Content-Type", "application/json; charset=UTF-8")
#        # cors
#        self.set_header('Access-Control-Allow-Origin', 'http://scmis.sduoj.online')
#        self.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
#        self.set_header('Access-Control-Allow-Credentials', 'true')
#        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

#    def options(self, *args, **kwargs):
#        self.set_default_headers()

    def write(self, chunk):
        if type(chunk) == dict and chunk.get('errcode') == RET.OK and chunk.get('data') is None:
            return
        return super().write(chunk)

    async def get_current_user(self):
        """判断用户是否登录"""
        if not self.session:
            self.session = await Session.create(self)
        return self.session.data

    async def is_admin(self):
        """判断用户是否为管理员"""
        return (await self.get_current_user()).get('user_role') == '0'

    async def is_principal(self):
        """判断用户是否为教务员"""
        return (await self.get_current_user()).get('user_role') != '2'

    async def execute(self, sql, parms):
        try:
            async with self.db.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, parms)
                await conn.commit()
            return self.write(dict(errcode=RET.OK, errmsg="执行成功", data="ok"))
        except Exception as e:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="出错"))

    async def query(self, sql, parms):
        try:
            async with self.db.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, parms)
                    ret = [row_to_obj(row, cur) for row in await cur.fetchall()]
                await conn.commit()
            return ret
        except Exception as e:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="出错"))

    async def query_with_ret_key(self, sql, parms, ret_keys):
        # 查询多项
        ret = []
        try:
            async with self.db.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, parms)
                    size = len(ret_keys)
                    for i in await cur.fetchall():
                        one = {}
                        for j in range(size):
                            one[ret_keys[j]] = str(i[j]) if i[j] is not None else None
                        ret.append(one)
                await conn.commit()
            return ret
        except Exception as e:
            self.write(dict(errcode=RET.PARAMERR, errmsg="出错"))
            return None

    async def queryone(self, sql, parms):
        results = await self.query(sql, parms)
        if len(results) == 0:
            raise NoResultError()
        elif len(results) > 1:
            raise ValueError("Expected 1 result, got %d" % len(results))
        return results[0]


