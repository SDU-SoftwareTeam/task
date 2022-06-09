
import pymysql

from utils.commons import required_login, required_principal, required_admin
from utils.response_code import RET
from .base_handler import BaseHandler


class QueryHandler(BaseHandler):
    @required_login
    async def post(self):
        sql = """
        SELECT c_id, c_name,  c_capacity,c_max_capacity,c_end_time,c_teacher_name,
               c_teacher_name,  c_description, c_period,
               c_classroom
        FROM ms_course JOIN ms_user_info ON c_teacher_id=ui_id
        WHERE (c_id = %(id)s OR %(id)s is null OR %(id)s = "") AND 
              c_name like %(class_name)s AND 
              c_teacher_name like %(teacher_name)s AND 
              (ui_id=%(teacher_id)s OR %(teacher_id)s is null)
        ORDER BY c_id;
        """
        ret_keys = ['id', 'course_name', 'capacity','max_capacity','end_time','teacher_name',
                   'teacher_username', 'description','period','classroom']
        self.json_args['class_name'] = '%{}%'.format(self.json_args['class_name'])
        self.json_args['teacher_name'] = '%{}%'.format(self.json_args['teacher_name'])
        return self.write(dict(errcode=RET.OK, errmsg="OK", data=await self.query_with_ret_key(sql, self.json_args, ret_keys)))


class EditHandler(BaseHandler):
    @required_login
    @required_admin
    async def post(self):
        sql = """
        UPDATE ms_course
        SET  c_name=%(course_name)s,c_max_capacity=%(max_capacity)s,
         c_capacity=%(capacity)s, c_teacher_name=%(teacher_username)s,c_end_time=%(end_time)s,
        c_description=%(description)s, c_period=%(period)s, c_classroom=%(classroom)s
        WHERE c_id=%(id)s;
        """

        #查询已选课程量
        sql2 = """
                SELECT  c_capacity,c_max_capacity
                FROM ms_course
                WHERE c_id = %(id)s 
                """
        try:
            async with self.db.acquire() as conn:
                async with conn.cursor() as cur:
                    try:#查询已选课程量，判断是否可以修改最大课余量
                        await cur.execute(sql2, self.json_args)
                        res2 = await cur.fetchone()
                        has = int(res2[1]) - int(res2[0])
                        self.json_args['capacity'] = int(self.json_args['max_capacity']) - has;
                        if(has > int(self.json_args['max_capacity'])):
                            await conn.commit()
                            return self.write(dict(errcode=RET.PARAMERR, errmsg="最大课余量小于已选择该课程人数，拒绝修改"))
                    except Exception as e:
                        await conn.rollback()
                        return self.write(dict(errcode=RET.PARAMERR, errmsg="未找到相关课程,查询课余量信息出错"))
                    await cur.execute(sql, self.json_args)
                await conn.commit()
            return self.write(dict(errcode=RET.OK, errmsg="执行成功", data="ok"))
        except Exception as e:
            await conn.rollback()
            return self.write(dict(errcode=RET.PARAMERR, errmsg="出错"))


class AddHandler(BaseHandler):
    @required_login
    @required_admin
    async def post(self):
        sql = """
        INSERT INTO ms_course
        (c_name,c_capacity,c_max_capacity,
         c_teacher_id,c_description,c_period,c_end_time,c_teacher_name,
         c_classroom) VALUES
        (%(name)s, %(capacity)s, %(max_capacity)s,
         %(ept)s, %(description)s, %(period)s, %(end_time)s,%(teacher_name)s,
         %(classroom)s);
        """

        try:
            async with self.db.acquire() as conn:
                try:
                    async with conn.cursor() as cur:
                        for r in self.json_args:
                            r['ept'] = int(self.session.data['user_id'])
                            await cur.execute(sql, r)
                    await conn.commit()
                except pymysql.err.IntegrityError as e:
                    await conn.rollback()
                    return self.write(dict(errcode=RET.OK, errmsg="当前帐号异常", data="ok"))
                except Exception as e:
                    await conn.rollback()
                    return self.write(dict(errcode=RET.OK, errmsg="添加异常", data="ok"))
            return self.write(dict(errcode=RET.OK, errmsg="添加成功", data="ok"))
        except Exception as e:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="出错"))



class DeleteHandler(BaseHandler):
    @required_login
    @required_admin
    async def post(self):
        sql = """
        DELETE FROM ms_course
        WHERE c_id=%(id)s;
        """
        await self.execute(sql, self.json_args)

class QuerySelfHandler(BaseHandler):
    @required_login
    async def post(self):
        sql = """
        SELECT c_id, c_name, c_semester, c_year, c_capacity,c_max_capacity,c_end_time,
               c_teacher_id, c_teacher_name , c_description, c_period,
               c_classroom
        FROM ms_course JOIN ms_user_info ON c_teacher_id=ui_id
        WHERE  ui_username=%(username)s
        ORDER BY c_year,c_semester DESC;
        """
        ret_keys = ['id', 'course_name', 'semester', 'year', 'capacity','max_capacity','end_time',
                   'teacher_id', 'teacher_name', 'description','period','classroom']
        username = self.session.data['user_username']
        return self.write(dict(errcode=RET.OK, errmsg="OK", data=await self.query_with_ret_key(sql,{"username":username}, ret_keys)))
