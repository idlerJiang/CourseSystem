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
    sql = "select course_profile.course_id, course_profile.course_name, course_profile.teacher_id, user_detail.user_name, course_detail.capacity, course_detail.selected, course_detail.time, classroom.location from course_profile, course_detail, classroom, user_detail where true"
    param = list()
    return_data = list()
    try:
        if course_id is not None:
            sql += " and course_id like %s"
            param.append("%"+course_id+"%")
        if course_name is not None:
            sql += " and course_name like %s"
            param.append("%"+course_name+"%")
        if teacher_id is not None:
            sql += " and teacher_id like %s"
            param.append("%"+teacher_id+"%")
        if teacher_name is not None:
            sql += " and teacher_name like %s"
            param.append("%"+teacher_name+"%")
        if time is not None:
            sql += " and time like %s"
            param.append("%"+time+"%")
        result = cursor.execute(sql, param)
        if cursor.rowcount > 0:
            for data in result:
                return_data.append(
                    {'course_id': data[0], 'course_name': data[1], 'teacher_id': data[2], 'teacher_name': data[3],
                     'capacity': data[4], 'selected': data[5], 'time': data[6], 'location': data[7]})
        return return_data
    except Exception as e:
        return return_data
