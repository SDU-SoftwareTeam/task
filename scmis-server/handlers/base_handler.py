# -*- coding: utf-8 -*-
# !/usr/bin/env python
# Copyright 2018 ZhangT. All Rights Reserved.
# Author: ZhangT
# Author-Github: github.com/zhangt2333
# base_handler.py 2018/12/3 21:20

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

   