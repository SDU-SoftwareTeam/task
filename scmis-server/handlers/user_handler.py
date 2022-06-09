
import hashlib
import pymysql
from sqlite3 import IntegrityError

import config
from utils.commons import required_login, required_admin
from utils.response_code import RET
from utils.session import Session
from .base_handler import BaseHandler


class LoginHandler(BaseHandler):
    async def post(self):
        # 获取参数
        username = self.json_args.get('username')
        passwd = self.json_args.get('password')
        remember = self.json_args.get('remember')

        # 检查参数
        if not all([username, passwd, remember]):
            return self.write(dict(errcode=RET.PARAMERR, errmsg="参数错误"))

        # 检查密码正确与否
        res = None
        try:
            async with self.db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('SELECT ui_password, ui_role,ui_id,ui_finish FROM ms_user_info WHERE ui_username=%(username)s', {"username": username})
                    res = await cursor.fetchone()
                await conn.commit()
            passwd = hashlib.sha256((passwd + config.passwd_hash_key).encode('utf-8')).hexdigest()
            if not (res and res[0] == passwd):
                return self.write(dict(errcode=RET.DATAERR, errmsg="账号或密码错误！"))
            # 成功，生成session数据
            self.session = await Session.create(self)
            self.session.data['user_username'] = username
            self.session.data['user_id'] = str(res[2])
            self.session.data['user_role'] = str(res[1])
            self.session.data['finish'] = str(res[3])
            await self.session.save()
            return self.write(dict(errcode=RET.OK, errmsg="登录成功", data="ok"))
        except Exception as e:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="账号或密码错误"))


class LogoutHandler(BaseHandler):
    @required_login
    async def get(self):
        # 清除session数据
        # sesssion = await Session.create(self)
        await self.session.clear()
        self.write(dict(errcode=RET.OK, errmsg="退出成功", data="ok"))

class RegisterHandler(BaseHandler):
    async def post(self):
        sql = """
                INSERT INTO ms_user_info
                ( ui_password, ui_name, ui_role,ui_username) VALUES
                (%(password)s, %(name)s,  %(role)s,%(username)s);
                """
        try:
            async with self.db.acquire() as conn:
                try:
                    async with conn.cursor() as cur:
                            # 密码加密处理
                        self.json_args['password'] = hashlib.sha256(
                                (self.json_args['password'] + config.passwd_hash_key).encode('utf-8')).hexdigest()
                        self.json_args['role'] = 2
                        await cur.execute(sql, self.json_args)
                        await conn.commit()
                except pymysql.err.IntegrityError as e:
                    await conn.rollback()
                    return self.write(dict(errcode=RET.PARAMERR, errmsg="用户名重复不执行"))
                except Exception as e:
                    await conn.rollback()
                    return self.write(dict(errcode=RET.PARAMERR, errmsg="添加用户异常"))
            return self.write(dict(errcode=RET.OK, errmsg="添加成功", data="ok"))
        except Exception as e:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="添加用户异常"))


class QueryHandler(BaseHandler):
    @required_login
    @required_admin
    async def post(self):
        sql = """
        SELECT ui_id, ui_name, ui_department, ui_major, ui_role, ui_class, ui_username
        FROM ms_user_info 
        WHERE ui_username like %(username)s AND
              ui_name like %(name)s 
        ORDER BY ui_id desc;
        """
        ret_keys = ['id', 'name',  'department', 'major', 'role', 'class', 'username']
        self.json_args['username'] = '%{}%'.format(self.json_args['username'])
        self.json_args['name'] = '%{}%'.format(self.json_args['name'])
        return self.write(dict(errcode=RET.OK, errmsg="OK", data=await self.query_with_ret_key(sql, self.json_args, ret_keys)))


class EditHandler(BaseHandler):
    @required_login
    async def post(self):
        sql = """
        UPDATE ms_user_info
        SET ui_name=%(name)s,ui_class=%(class)s,
            ui_major=%(major)s, ui_department=%(department)s
        WHERE ui_username=%(username)s;
        """
        sql2 = """
                UPDATE ms_user_info
                SET ui_finish=1
                WHERE ui_username=%(username)s;
                """
        self.json_args["username"] = self.session.data['user_username']

        #await self.execute(sql, self.json_args)
        try:
            async with self.db.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, self.json_args)

                    if (self.session.data['finish'] == "0"):
                        self.session = await Session.create(self)
                        self.session.data['finish'] = "1"
                        await self.session.save()
                        await cur.execute(sql2, self.json_args)
                await conn.commit()

            return self.write(dict(errcode=RET.OK, errmsg="执行成功", data="ok"))
        except Exception as e:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="出错"))

class AdminEditHandler(BaseHandler):        #加这个是因为上面的端口搞混了，增加一个管理员修改用户信息的接口
    @required_login
    async def post(self):
        sql = """
        UPDATE ms_user_info
        SET ui_name=%(name)s,ui_class=%(class)s,
            ui_major=%(major)s, ui_department=%(department)s
        WHERE ui_username=%(username)s;
        """
        try:
            async with self.db.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, self.json_args)
                await conn.commit()
            return self.write(dict(errcode=RET.OK, errmsg="执行成功", data="ok"))
        except Exception as e:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="出错"))

class EditPassHandler(BaseHandler):
    """修改用户密码"""

    @required_login
    @required_admin
    async def post(self):
        sql = """
        UPDATE ms_user_info
        SET ui_password=%(password)s
        WHERE ui_username=%(username)s;
        """
        self.json_args["password"] = hashlib.sha256((self.json_args["password"] + config.passwd_hash_key).encode('utf-8')).hexdigest()
        await self.execute(sql, self.json_args)

class EditRoleHandler(BaseHandler):
    """修改用户角色"""

    @required_login
    @required_admin
    async def post(self):
        sql = """
        UPDATE ms_user_info
        SET ui_role=%(role)s
        WHERE ui_username=%(username)s;
        """
        await self.execute(sql, self.json_args)


class AddHandler(BaseHandler):
    """批量录入"""

    @required_login
    @required_admin
    async def post(self):
        sql = """
        INSERT INTO ms_user_info
        ( ui_password, ui_name, ui_department, ui_major, ui_role,ui_class,ui_username) VALUES
        (%(password)s, %(name)s, %(department)s, %(major)s, %(role)s,%(class)s,%(username)s);
        """
        try:
            async with self.db.acquire() as conn:
                try:
                    async with conn.cursor() as cur:
                        for r in self.json_args:
                            # 密码加密处理
                            r['password'] = hashlib.sha256((r['password'] + config.passwd_hash_key).encode('utf-8')).hexdigest()
                            await cur.execute(sql, r)
                        await conn.commit()
                except pymysql.err.IntegrityError as e:
                    await conn.rollback()
                    return self.write(dict(errcode=RET.PARAMERR, errmsg="用户名重复不执行"))
                except Exception as e:
                    await conn.rollback()
                    return self.write(dict(errcode=RET.PARAMERR, errmsg="添加用户异常"))
            return self.write(dict(errcode=RET.OK, errmsg="添加成功", data="ok"))
        except Exception as e:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="添加用户异常"))


class DeleteHandler(BaseHandler):
    """删除用户"""

    @required_login
    @required_admin
    async def post(self):
        sql = """
        DELETE FROM ms_user_info
        WHERE ui_username=%(username)s;
        """
        await self.execute(sql, self.json_args)


class QuerySelfHandler(BaseHandler):
    """查询本用户"""
    @required_login
    async def post(self):
        sql = """
        SELECT ui_id, ui_name, ui_department, ui_major, ui_role, ui_class, ui_username
        FROM ms_user_info 
        WHERE ui_username=%(username)s
        ORDER BY ui_id desc
        LIMIT 1;
        """
        ret_keys = ['id', 'name', 'department', 'major', 'role','class','username']
        return self.write(dict(errcode=RET.OK, errmsg="OK", data=await self.query_with_ret_key(sql, {'username': self.session.data['user_username']}, ret_keys)))


class EditSelfHandler(BaseHandler):
    """更新本用户信息"""

    @required_login
    async def post(self):
        sql = """
        UPDATE ms_user_info
        SET ui_password=%(newPassword)s 
        WHERE ui_username=%(username)s; 
        """
        # 验证用户密码
        res = None
        self.json_args['username'] = self.session.data['user_username']
        try:
            async with self.db.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT ui_password, ui_role FROM ms_user_info WHERE ui_username=%(username)s',
                                   {"username": self.json_args['username']})
                    res = await cur.fetchone()
                await conn.commit()
        except Exception as e:
            await conn.rollback()
            return self.write(dict(errcode=RET.PARAMERR, errmsg="出错"))
        self.json_args['password'] = hashlib.sha256(
            (self.json_args['password'] + config.passwd_hash_key).encode('utf-8')).hexdigest()
        if not (res and res[0] == self.json_args['password']):
            return self.write(dict(errcode=RET.DATAERR, errmsg="账号或密码错误！"))
        # 需要更改密码

        self.json_args['newPassword'] = hashlib.sha256(
                (self.json_args['newPassword'] + config.passwd_hash_key).encode('utf-8')).hexdigest()
        await self.execute(sql, self.json_args)
