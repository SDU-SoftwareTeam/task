# -*- coding: utf-8 -*-
# !/usr/bin/env python
# Copyright 2018 ZhangT. All Rights Reserved.
# Author: ZhangT
# Author-Github: github.com/zhangt2333
# urls.py 2018/12/3 21:13

import os

import config
from handlers import user_handler,course_handler, take_handler
from handlers.static_handler import StaticHandler

urls = [
    (r"/api/user/login", user_handler.LoginHandler),
    (r"/api/user/logout", user_handler.LogoutHandler),
    (r"/api/user/query", user_handler.QueryHandler),
    (r"/api/user/edit", user_handler.EditHandler),
    (r"/api/user/adminEdit", user_handler.AdminEditHandler),
    (r"/api/user/add", user_handler.AddHandler),
    (r"/api/user/register", user_handler.RegisterHandler),
    (r"/api/user/delete", user_handler.DeleteHandler),
    (r"/api/user/editRole", user_handler.EditRoleHandler),
    (r"/api/user/editPassword", user_handler.EditPassHandler),
    (r"/api/user/querySelf", user_handler.QuerySelfHandler),
    (r"/api/user/editSelf", user_handler.EditSelfHandler),

    (r"/api/course/query", course_handler.QueryHandler),
    (r"/api/course/edit", course_handler.EditHandler),
    (r"/api/course/add", course_handler.AddHandler),
    (r"/api/course/delete", course_handler.DeleteHandler),
    (r"/api/course/querySelf", course_handler.QuerySelfHandler),

    (r"/api/take/query", take_handler.QueryHandler),
    (r"/api/take/edit", take_handler.EditHandler),
    (r"/api/take/add", take_handler.AddHandler),
    (r"/api/take/delete", take_handler.DeleteHandler),
    (r"/api/take/querySelf", take_handler.QueryselfHandler),


    (r"/(.*)", StaticHandler, dict(path=config.front_end_dir, default_filename="login.html"))
]
