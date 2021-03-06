

import aiomysql
import aioredis
import tornado.web


class Application(tornado.web.Application):
    @classmethod
    async def create(cls, urls, app_settings, mysql_settings, redis_settings):
        self = Application(urls, **app_settings)
        self.db = await aiomysql.create_pool(**mysql_settings)
        await self.init_database()
        self.redis = await aioredis.create_redis_pool(**redis_settings)
        return self

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)

    async def init_database(self):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute("SELECT COUNT(*) FROM ms_user_info LIMIT 1")
                    await cur.fetchone()
                except Exception as e:
                    with open("DBInit.sql") as f:
                        await cur.execute(f.read())