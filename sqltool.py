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
            param.append("%" + course_id + "%")
        if course_name is not None and course_name != "":
            sql += " and cp.course_name like %s"
            param.append("%" + course_name + "%")
        if teacher_id is not None and teacher_id != "":
            sql += " and cp.teacher_id like %s"
            param.append("%" + teacher_id + "%")
        if teacher_name is not None and teacher_name != "":
            sql += " and ud.user_name like %s"
            param.append("%" + teacher_name + "%")
        if time is not None and time != "":
            sql += " and cd.time like %s"
            param.append("%" + time + "%")
        print(sql, param)
        result = cursor.execute(sql, param)
        result = cursor.fetchall()

        if cursor.rowcount > 0:
            for data in result:
                return_data.append(
                    {'course_id': data[0], 'course_name': data[1], 'teacher_id': data[2], 'teacher_name': data[3],
                     'capacity': data[4], 'selected': data[5], 'time': data[6], 'location': data[7]})
        return return_data
    except Exception as e:
        return return_data


def select_course(cursor, user_id, course_id, teacher_id):
    def check_schedule(course_time):
        day_dict = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5}
        schedule = [[0 for _ in range(13)] for __ in range(6)]
        for course in course_time:
            times = course.split(" ")
            for time in times:
                day = day_dict[time[0]]
                time = time[1:].split("-")
                start_time = int(time[0])
                end_time = int(time[1])
                for i in range(start_time, end_time + 1):
                    if schedule[day][i] != 0:
                        return False
                    schedule[day][i] = 1
        return True

    # 是否已选该课程
    sql = "select status from selected_course where user_id = %s and course_id = %s and teacher_id = %s"
    result = cursor.execute(sql, (user_id, course_id, teacher_id))
    if result > 0:
        return f"已选此课程(课程号:{course_id}, 教师号:{teacher_id})"
    # 判断时间冲突
    sql = "select cd.time from selected_course sc join course_detail cd on sc.course_id = cd.course_id and sc.teacher_id = cd.teacher_id where sc.user_id = %s"
    result = cursor.execute(sql, user_id)
    if result > 0:
        course_time = list()
        result = cursor.fetchall()
        for data in result:
            course_time.append(data[0])
        sql = "select time from course_detail where course_id = %s and teacher_id = %s"
        result = cursor.execute(sql, (course_id, teacher_id))
        if result > 0:
            result = cursor.fetchone()
            course_time.append(result[0])
        if not check_schedule(course_time):
            return f"课程时间冲突(课程号:{course_id}, 教师号:{teacher_id})"
    # 判断有无空位
    sql = "select capacity, selected from course_detail where course_id = %s and teacher_id = %s"
    result = cursor.execute(sql, (course_id, teacher_id))
    if result > 0:
        result = cursor.fetchall()
        capacity = result[0][0]
        selected = result[0][1]
        if selected < capacity:
            sql = "lock tables course_detail write, selected_course write, course_score write"
            cursor.execute(sql)
            sql = "update course_detail set selected = selected + 1 where course_id = %s and teacher_id = %s"
            cursor.execute(sql, (course_id, teacher_id))
            sql = "insert into selected_course(course_id, teacher_id, user_id, status) values (%s, %s, %s, %s)"
            cursor.execute(sql, (course_id, teacher_id, user_id, 1))
            sql = "insert into course_score(course_id, user_id) values (%s, %s)"
            cursor.execute(sql, (course_id, user_id))
            sql = "unlock tables"
            cursor.execute(sql)
            return f"选课成功(课程号:{course_id}, 教师号:{teacher_id})"
        else:
            return f"人数已满(课程号:{course_id}, 教师号:{teacher_id})"
    else:
        return f"不可选择此课程(课程号:{course_id}, 教师号:{teacher_id})"


def drop_course(cursor, user_id, course_id, teacher_id):
    print(user_id, course_id, teacher_id)
    # 是否已选该课程
    sql = "select status from selected_course where user_id = %s and course_id = %s and teacher_id = %s"
    result = cursor.execute(sql, (user_id, course_id, teacher_id))
    if result == 0:
        return f"未选此课程(课程号:{course_id}, 教师号:{teacher_id})"
    sql = "lock tables course_detail write, selected_course write, course_score write"
    cursor.execute(sql)
    sql = "update course_detail set selected = selected - 1 where course_id = %s and teacher_id = %s"
    cursor.execute(sql, (course_id, teacher_id))
    sql = "delete from selected_course where course_id = %s and teacher_id = %s and user_id = %s"
    result = cursor.execute(sql, (course_id, teacher_id, user_id))
    sql = "delete from course_score where course_id = %s and user_id = %s"
    cursor.execute(sql, (course_id, user_id))
    sql = "unlock tables"
    cursor.execute(sql)
    if result > 0:
        return f"退课成功(课程号:{course_id}, 教师号:{teacher_id})"
    return f"退课失败(课程号:{course_id}, 教师号:{teacher_id})"


def query_selected_course(cursor, user_id):
    sql = "select cp.course_id, cp.course_name, cp.teacher_id, ud.user_name, cd.capacity, cd.selected, cd.time, cr.location from selected_course sc join course_profile cp on sc.course_id = cp.course_id and sc.teacher_id = cp.teacher_id join coursesystem.course_detail cd on cp.course_id = cd.course_id and cp.teacher_id = cd.teacher_id join coursesystem.user_detail ud on cd.user_id = ud.user_id join coursesystem.classroom cr on cd.classroom_id = cr.classroom_id where sc.user_id = %s"
    result = cursor.execute(sql, user_id)
    return_data = list()
    if result == 0:
        return return_data
    result = cursor.fetchall()
    for data in result:
        return_data.append(
            {'course_id': data[0], 'course_name': data[1], 'teacher_id': data[2], 'teacher_name': data[3],
             'capacity': data[4], 'selected': data[5], 'time': data[6], 'location': data[7]})
    return return_data


def fetch_score(cursor, user_id):
    sql = "select cs.course_id, cp.course_name, ud.user_name, cs.final_score from course_score cs join selected_course sc on cs.course_id = sc.course_id and cs.user_id = sc.user_id join course_detail cd on sc.course_id = cd.course_id and sc.teacher_id = cd.teacher_id join course_profile cp on cd.course_id = cp.course_id join user_detail ud on cd.user_id = ud.user_id where cs.user_id = %s"
    result = cursor.execute(sql, user_id)
    print(result)
    return_data = list()
    if result == 0:
        return return_data
    result = cursor.fetchall()
    for data in result:
        return_data.append({'course_id': data[0], 'course_name': data[1], 'teacher_name': data[2], 'score': data[3]})
    return return_data
