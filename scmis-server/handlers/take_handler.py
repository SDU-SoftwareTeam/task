
import re
import datetime

from utils.commons import required_login,required_admin
from utils.response_code import RET
from .base_handler import BaseHandler


class QueryHandler(BaseHandler):
    @required_login
    @required_admin
    async def post(self):
        sql = """
        SELECT ct_id, ui_username, ui_name, ct_course_id, c_name, ct_grade,ui_department,ui_major
        FROM ms_course_take JOIN ms_user_info ON ui_id=ct_student_id
                            JOIN ms_course ON c_id=ct_course_id
        WHERE (%(course_id)s is not null OR %(student_id)s is not null) AND
              (ct_student_id = %(student_id)s OR %(student_id)s is null) AND
              (ct_course_id = %(course_id)s OR %(course_id)s is null)
        ORDER BY ct_id DESC
        """
        ret_keys = ['id', 'student_username', 'name','course_id', 'course_name', 'grade','department','major']
        return self.write(dict(errcode=RET.OK, errmsg="OK", data=await self.query_with_ret_key(sql, self.json_args, ret_keys)))


class EditHandler(BaseHandler):
    @required_login
    async def post(self):
        # 验证用户是否为该课授课教师或管理员
        sql1 = """
        SELECT *
        FROM ms_course JOIN ms_user_info ON c_teacher_id=ui_id
        WHERE ui_username=%(teacher_id)s AND
              c_id=%(course_id)s;
        """
        # 修改数据库
        sql2 = """
                UPDATE ms_course_take
                SET ct_grade=%(grade)s
                WHERE ct_student_id=%(student_id)s and ct_course_id=%(course_id)s;
                """
        sql3 = """
        SELECT ui_id
        FROM ms_user_info
        WHERE ui_username = %(student_id)s;
        """
        username = self.session.data['user_username']
        try:
            async with self.db.acquire() as conn:
                try:
                    async with conn.cursor() as cur:
                        await cur.execute(sql1, {"course_id":self.json_args['course_id'], "teacher_id": username})
                        teacher = await cur.fetchone()
                        if not (teacher or int(self.session.data['user_role']) == 0):
                            await conn.commit()
                            return self.write(dict(errcode=RET.ROLEERR, errmsg="用户非该课授课教师"))
                        for r in self.json_args["details"]:
                            try:#通过username查找id
                                await cur.execute(sql3,r)
                                st_id = await cur.fetchone()
                                sql_parm = {
                                    "grade": r["grade"],
                                    "student_id": int(st_id[0]),
                                    "course_id": int(self.json_args['course_id'])
                                }
                            except Exception as e:
                                await conn.rollback()
                                return self.write(dict(errcode=RET.PARAMERR, errmsg="请传递学生正确学号"))
                            try:
                                await cur.execute(sql2, sql_parm)
                            except Exception as e:
                                await conn.rollback()
                                return self.write(dict(errcode=RET.PARAMERR, errmsg="未查到对应课程"))
                    await conn.commit()
                    return self.write(dict(errcode=RET.OK, errmsg="上传成功", data="ok"))
                except Exception as e:
                    await conn.rollback()
                    return self.write(dict(errcode=RET.PARAMERR, errmsg="异常"))
        except Exception as e:
            await conn.rollback()
            return self.write(dict(errcode=RET.PARAMERR, errmsg="异常"))




class AddHandler(BaseHandler):
    @required_login
    async def post(self):

        sql4 = """
                                    SELECT c_period, ct_course_id
                                    FROM ms_course_take JOIN ms_course ON ct_course_id=c_id
                                    WHERE ct_student_id=%(student_id)s AND 
                                    c_year=%(year)s AND 
                                    c_semester=%(semester)s 
                                    """
        sql = """
               INSERT INTO ms_course_take
               (ct_student_id, ct_course_id) VALUES
               (%(student_id)s, %(course_id)s);
               """
        sql2 = """
               UPDATE ms_course
               SET c_capacity=c_capacity-1
               WHERE c_id=%(course_id)s and c_capacity>0;
               """
        class_id = self.json_args.get('course_id')

        if (self.session.data['finish'] == "0"):
            return self.write(dict(errcode=RET.DATAERR, errmsg="未完善个人信息，不允许选课"))

        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    self.json_args["student_id"] = self.session.data['user_id']
                    # 获取课容量和上课时间
                    await cursor.execute(
                        'SELECT c_capacity,c_period,c_year,c_semester,c_end_time  FROM ms_course WHERE c_id=%(id)s',
                        {"id": class_id})
                    res2 = await cursor.fetchone()
                    classEndTime = res2[4]
                    if not (res2 and res2[0] > 0):
                        await conn.commit()
                        return self.write(dict(errcode=RET.DATAERR, errmsg="课程已满"))
                    if(classEndTime == None or classEndTime < datetime.datetime.now()) :
                        await conn.commit()
                        return self.write(dict(errcode=RET.DATAERR, errmsg="已过该课选课阶段"))
                    # 添加课程
                    await cursor.execute(sql,self.json_args)
                    # 更新课余量
                    await cursor.execute(sql2, self.json_args)
                    await conn.commit()
                except Exception as e:
                    await conn.rollback()
                    return self.write(dict(errcode=RET.PARAMERR, errmsg="添加课程异常"))
        return self.write(dict(errcode=RET.OK, errmsg="执行成功", data="ok"))



class DeleteHandler(BaseHandler):
    @required_login
    async def post(self):
        sql = """
        DELETE FROM ms_course_take
        WHERE ct_student_id=%(student_id)s and ct_course_id=%(course_id)s;
        """
        sql2 = """
        SELECT ui_username,ct_grade
        FROM ms_user_info JOIN ms_course_take ON ct_student_id=ui_id
        WHERE ct_student_id=%(student_id)s and ct_course_id=%(course_id)s;
        """
        sql4 ="""
        SELECT c_end_time
        FROM ms_course
        WHERE c_id=%(course_id)s
        """
        sql3 = """
        UPDATE ms_course
        SET c_capacity=c_capacity+1
        WHERE c_id=%(course_id)s;
        """
        username = self.session.data['user_username']

        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    self.json_args['student_id']=self.session.data['user_id']
                    # 查询是否为该用户课程
                    await cursor.execute(sql2, self.json_args)
                    res3 = await cursor.fetchone()
                    if not (res3 and res3[0] == username):
                        await conn.commit()
                        return self.write(dict(errcode=RET.DATAERR, errmsg="非本用户课程无法删除"))
                    #判断是否无法退选
                    if(res3[1] is not None):
                        await conn.commit()
                        return self.write(dict(errcode=RET.DATAERR, errmsg="已评分课程无法退选"))
                    await cursor.execute(sql4, self.json_args)
                    res4 = await cursor.fetchone()
                    if(res4[0] == None or res4[0] < datetime.datetime.now()):
                        await conn.commit()
                        return self.write(dict(errcode=RET.DATAERR, errmsg="已过退选阶段，无法退选"))
                    # 课容量增加
                    await cursor.execute(sql3, self.json_args)
                    # 退选课程
                    await cursor.execute(sql, self.json_args)
                    await conn.commit()

                except Exception as e:
                    await conn.rollback()
                    return self.write(dict(errcode=RET.PARAMERR, errmsg="异常"))
        return self.write(dict(errcode=RET.OK, errmsg="执行成功", data="ok"))


class QueryselfHandler(BaseHandler):
    @required_login
    async def post(self):
        sql = """
        SELECT  c_name, ct_course_id, c_year, c_capacity,c_max_capacity, c_teacher_name , c_end_time ,
        c_period, c_classroom, c_semester, c_description, ct_grade,c_teacher_name
        FROM ms_course_take JOIN ms_course ON c_id=ct_course_id
                            JOIN ms_user_info S ON S.ui_id=ct_student_id 
                            JOIN ms_user_info T ON T.ui_id=c_teacher_id
        WHERE S.ui_username=%(username)s
        ORDER BY ct_id desc
        """
        self.json_args["username"] = self.session.data['user_username']
        ret_keys = [ 'course_name', 'course_id','year', 'capacity', 'max_capacity','teacher_username','end_time',
                    'period', 'classroom', 'semester', 'description', 'grade','teacher_name']
        return self.write(dict(errcode=RET.OK, errmsg="OK", data=await self.query_with_ret_key(sql, self.json_args, ret_keys)))

