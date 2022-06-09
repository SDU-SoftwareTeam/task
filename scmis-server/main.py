
import tornado.ioloop
import tornado.options
import tornado.httpserver
import tornado.locks
import config
from application import Application

from urls import urls
from tornado.options import options, define

define("port", default=8000, type=int, help="run server on the given port")


async def main():

    tornado.options.parse_command_line()
    app = await Application.create(
        urls,
        config.app_settings,
        config.mysql_settings,
        config.redis_settings
    )
    app.listen(options.port)
    shutdown_event = tornado.locks.Event()
    await shutdown_event.wait()


if __name__ == "__main__":
    tornado.ioloop.IOLoop.current().run_sync(main)