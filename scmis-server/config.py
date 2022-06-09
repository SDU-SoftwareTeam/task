# -*- coding: utf-8 -*-
# !/usr/bin/env python
# Copyright 2018 ZhangT. All Rights Reserved.
# Author: ZhangT
# Author-Github: github.com/zhangt2333
# config.py 2018/12/3 21:13

import os

# 前端页面路径
front_end_dir = os.path.join(os.path.dirname(__file__), "../scmis-web/")

# Application配置参数
app_settings = dict(
    static_path=os.path.join(front_end_dir, "static"),
    cookie_secret="your_secret",
    xsrf_cookies=False,
    debug=False
)


# 数据库配置参数
mysql_settings = dict(
    host="localhost",
    port=3306,
    db="scmis",
    user="scmis",
    password="4tFCmjcbkAPi8Xyp",
    autocommit=False
)

# Redis配置参数
redis_settings = dict(
    address="redis://localhost:6379"
)


# 密码加密密钥
passwd_hash_key = "your_secret"
