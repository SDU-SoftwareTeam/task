# -*- coding: utf-8 -*-
# !/usr/bin/env python
# Copyright 2018 ZhangT. All Rights Reserved.
# Author: ZhangT
# Author-Github: github.com/zhangt2333
# user_handler.py 2018/12/3 21:13
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

