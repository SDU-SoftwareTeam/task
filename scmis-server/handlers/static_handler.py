

from tornado.web import StaticFileHandler


class StaticHandler(StaticFileHandler):
    """自定义静态文件处理类, 在用户获取html页面的时候设置_xsrf的cookie"""

    def __init__(self, *args, **kwargs):
        super(StaticHandler, self).__init__(*args, **kwargs)
        self.xsrf_token
