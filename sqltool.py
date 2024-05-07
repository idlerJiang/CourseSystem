import pymysql


def login(cursor, user_id, password):
    sql = "select user_role from user_profile where user_id = %s and password = %s;"
    try:
        result = cursor.execute(sql, (user_id, password))
        if cursor.rowcount == 1:
            user_role = int(cursor.fetchone()[0])
            sql = "select user_name from user_detail where user_id = %s;"
            result = cursor.execute(sql, user_id)
            if cursor.rowcount == 1:
                user_name = cursor.fetchone()[0]
                return user_role, user_name
            else:
                return -1, "Nothing"
        else:
            return 0, "Nothing"
    except Exception as e:
        print("SQL处理登录时出错: ", e)
        return -1, "Nothing"


def query_course(cursor, course_id=None, course_name=None, teacher_id=None, teacher_name=None, time=None):
    sql = "select cp.course_id, cp.course_name, cp.teacher_id, ud.user_name, cd.capacity, cd.selected, cd.time, cr.location from course_profile cp join coursesystem.course_detail cd on cp.course_id = cd.course_id and cp.teacher_id = cd.teacher_id join coursesystem.user_detail ud on cd.user_id = ud.user_id join coursesystem.classroom cr on cd.classroom_id = cr.classroom_id where true"
    param = list()
    return_data = list()
    try:
        if course_id is not None and course_id != "":
            sql += " and cp.course_id like %s"
            param.append("%"+course_id+"%")
        if course_name is not None and course_name != "":
            sql += " and cp.course_name like %s"
            param.append("%"+course_name+"%")
        if teacher_id is not None and teacher_id != "":
            sql += " and cp.teacher_id like %s"
            param.append("%"+teacher_id+"%")
        if teacher_name is not None and teacher_name != "":
            sql += " and ud.user_name like %s"
            param.append("%"+teacher_name+"%")
        if time is not None and time != "":
            sql += " and cd.time like %s"
            param.append("%"+time+"%")
        print(sql, param)
        result = cursor.execute(sql, param)
        result = cursor.fetchall()

        print("!!!", result)
        if cursor.rowcount > 0:
            for data in result:
                print("!!!", data)
                return_data.append(
                    {'course_id': data[0], 'course_name': data[1], 'teacher_id': data[2], 'teacher_name': data[3],
                     'capacity': data[4], 'selected': data[5], 'time': data[6], 'location': data[7]})
        return return_data
    except Exception as e:
        return return_data


def select_course(cursor, user_id, course_id, teacher_id):
    print(user_id, course_id, teacher_id)
    # 是否已选该课程
    sql = "select status from selected_course where user_id = %s and course_id = %s and teacher_id = %s"
    result = cursor.execute(sql, (user_id, course_id, teacher_id))
    if result > 0:
        return f"已选此课程(课程号:{course_id}, 教师号:{teacher_id})"
    # 判断有无空位
    sql = "select capacity, selected from course_detail where course_id = %s and teacher_id = %s"
    result = cursor.execute(sql, (course_id, teacher_id))
    if result > 0:
        result = cursor.fetchall()
        capacity = result[0][0]
        selected = result[0][1]
        if selected < capacity:
            sql = "lock tables course_detail write, selected_course write"
            cursor.execute(sql)
            sql = "update course_detail set selected = selected + 1 where course_id = %s and teacher_id = %s"
            cursor.execute(sql, (course_id, teacher_id))
            sql = "insert into selected_course(course_id, teacher_id, user_id, status) values (%s, %s, %s, %s)"
            cursor.execute(sql, (course_id, teacher_id, user_id, 1))
            sql = "unlock tables"
            cursor.execute(sql)
            return f"选课成功(课程号:{course_id}, 教师号:{teacher_id})"
        else:
            return f"人数已满(课程号:{course_id}, 教师号:{teacher_id})"
    else:
        return f"不可选择此课程(课程号:{course_id}, 教师号:{teacher_id})"