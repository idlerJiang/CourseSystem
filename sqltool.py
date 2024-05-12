import pymysql


def get_term(cursor):
    sql = "select * from term"
    return_data = list()
    try:
        cursor.execute(sql)
        if cursor.rowcount == 0:
            return return_data
        result = cursor.fetchall()
        for data in result:
            return_data.append({'term_id': data[0], 'term_name': data[1]})
        return return_data
    except Exception as e:
        print("SQL查询学期时出错: ", e)
        return list()


def get_term_id(cursor, term_name):
    sql = "select term_id from term where term_name = %s;"
    cursor.execute(sql, term_name)
    return cursor.fetchone()[0]


def login(cursor, user_id, password):
    sql = "select user_role from user_profile where user_id = %s and password = %s;"
    try:
        result = cursor.execute(sql, (user_id, password))
        if cursor.rowcount == 1:
            user_role = int(cursor.fetchone()[0])
            if user_role == 1:
                sql = "select student_name from student_detail where user_id = %s;"
            elif user_role == 2:
                sql = "select teacher_name from teacher_detail where user_id = %s;"
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


def query_course(cursor, term, course_id=None, course_name=None, teacher_id=None, teacher_name=None, time=None):
    try:
        term_id = get_term_id(cursor, term)
        sql = "select cp.course_id, cp.course_name, cd.teacher_id, td.teacher_name, cd.capacity, cd.selected, cd.time, cr.location from course_profile cp join coursesystem.course_detail cd on cp.course_id = cd.course_id join coursesystem.teacher_detail td on cd.user_id = td.user_id join coursesystem.classroom cr on cd.classroom_id = cr.classroom_id where cd.term_id = %s"
        param = list()
        param.append(term_id)
        if course_id is not None and course_id != "":
            sql += " and cp.course_id like %s"
            param.append("%" + course_id + "%")
        if course_name is not None and course_name != "":
            sql += " and cp.course_name like %s"
            param.append("%" + course_name + "%")
        if teacher_id is not None and teacher_id != "":
            sql += " and cd.teacher_id like %s"
            param.append("%" + teacher_id + "%")
        if teacher_name is not None and teacher_name != "":
            sql += " and td.teacher_name like %s"
            param.append("%" + teacher_name + "%")
        if time is not None and time != "":
            sql += " and cd.time like %s"
            param.append("%" + time + "%")
        print(sql, param)
        result = cursor.execute(sql, param)
        result = cursor.fetchall()
        return_data = list()
        if cursor.rowcount > 0:
            for data in result:
                return_data.append(
                    {'course_id': data[0], 'course_name': data[1], 'teacher_id': data[2], 'teacher_name': data[3],
                     'capacity': data[4], 'selected': data[5], 'time': data[6], 'location': data[7]})
        return return_data
    except Exception as e:
        return list()


def select_course(cursor, term, user_id, course_id, teacher_id):
    print("args: ", term, user_id, course_id, teacher_id)

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

    try:
        if course_id is None or course_id == "":
            return f"未给出课程号(课程号:{course_id}, 教师号:{teacher_id})"
        if teacher_id is None or teacher_id == "":
            return f"未给出教师号(课程号:{course_id}, 教师号:{teacher_id})"

        term_id = get_term_id(cursor, term)
        # 是否已选该课程
        sql = "select status from selected_course where user_id = %s and course_id = %s"
        result = cursor.execute(sql, (user_id, course_id))
        if result > 0:
            return f"已选此课程(课程号:{course_id}, 教师号:{teacher_id})"
        # 判断时间冲突
        sql = "select cd.time from selected_course sc join course_detail cd on sc.course_id = cd.course_id and sc.teacher_id = cd.teacher_id where sc.user_id = %s and cd.term_id = %s"
        result = cursor.execute(sql, (user_id, term_id))
        if result > 0:
            course_time = list()
            result = cursor.fetchall()
            for data in result:
                course_time.append(data[0])
            sql = "select time from course_detail where course_id = %s and teacher_id = %s and term_id = %s"
            result = cursor.execute(sql, (course_id, teacher_id, term_id))
            if result > 0:
                result = cursor.fetchone()
                course_time.append(result[0])
            if not check_schedule(course_time):
                return f"课程时间冲突(课程号:{course_id}, 教师号:{teacher_id})"
        # 判断有无空位
        sql = "select capacity, selected from course_detail where course_id = %s and teacher_id = %s and term_id = %s"
        result = cursor.execute(sql, (course_id, teacher_id, term_id))
        if result > 0:
            result = cursor.fetchall()
            capacity = result[0][0]
            selected = result[0][1]
            if selected < capacity:
                sql = "lock tables course_detail write, selected_course write, course_score write"
                cursor.execute(sql)
                sql = "update course_detail set selected = selected + 1 where course_id = %s and teacher_id = %s and term_id = %s"
                cursor.execute(sql, (course_id, teacher_id, term_id))
                sql = "insert into selected_course(term_id, course_id, teacher_id, user_id, status) values (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (term_id, course_id, teacher_id, user_id, 1))
                sql = "insert into course_score(course_id, user_id) values (%s, %s)"
                cursor.execute(sql, (course_id, user_id))
                sql = "unlock tables"
                cursor.execute(sql)
                return f"选课成功(课程号:{course_id}, 教师号:{teacher_id})"
            else:
                return f"人数已满(课程号:{course_id}, 教师号:{teacher_id})"
        else:
            return f"不可选择此课程(课程号:{course_id}, 教师号:{teacher_id})"
    except Exception as e:
        print("Error!", e)
        print("args: ", term, user_id, course_id, teacher_id)
        sql = "unlock tables"
        cursor.execute(sql)
        return f"数据库出错(课程号:{course_id}, 教师号:{teacher_id})"


def drop_course(cursor, term, user_id, course_id, teacher_id):
    term_id = get_term_id(cursor, term)
    # 是否已选该课程
    sql = "select status from selected_course where user_id = %s and course_id = %s and teacher_id = %s"
    result = cursor.execute(sql, (user_id, course_id, teacher_id))
    if result == 0:
        return f"未选此课程(课程号:{course_id}, 教师号:{teacher_id})"
    sql = "lock tables course_detail write, selected_course write, course_score write"
    cursor.execute(sql)
    sql = "update course_detail set selected = selected - 1 where course_id = %s and teacher_id = %s and term_id = %s"
    cursor.execute(sql, (course_id, teacher_id, term_id))
    sql = "delete from selected_course where course_id = %s and teacher_id = %s and user_id = %s"
    result = cursor.execute(sql, (course_id, teacher_id, user_id))
    sql = "delete from course_score where course_id = %s and user_id = %s"
    cursor.execute(sql, (course_id, user_id))
    sql = "unlock tables"
    cursor.execute(sql)
    if result > 0:
        return f"退课成功(课程号:{course_id}, 教师号:{teacher_id})"
    return f"退课失败(课程号:{course_id}, 教师号:{teacher_id})"


def query_selected_course(cursor, term, user_id):
    term_id = get_term_id(cursor, term)
    sql = "select cp.course_id, cp.course_name, cd.teacher_id, td.teacher_name, cd.capacity, cd.selected, cd.time, cr.location from selected_course sc join course_profile cp on sc.course_id = cp.course_id join course_detail cd on cp.course_id = cd.course_id join teacher_detail td on cd.user_id = td.user_id join classroom cr on cd.classroom_id = cr.classroom_id where sc.user_id = %s and cd.term_id = %s"
    result = cursor.execute(sql, (user_id, term_id))
    return_data = list()
    if result == 0:
        return return_data
    result = cursor.fetchall()
    for data in result:
        return_data.append(
            {'course_id': data[0], 'course_name': data[1], 'teacher_id': data[2], 'teacher_name': data[3],
             'capacity': data[4], 'selected': data[5], 'time': data[6], 'location': data[7]})
    return return_data


def fetch_score(cursor, term, user_id):
    term_id = get_term_id(cursor, term)
    sql = "select cs.course_id, cp.course_name, td.teacher_name, cs.final_score from course_score cs join selected_course sc on cs.course_id = sc.course_id and cs.user_id = sc.user_id join course_detail cd on sc.course_id = cd.course_id and sc.teacher_id = cd.teacher_id join course_profile cp on cd.course_id = cp.course_id join teacher_detail td on cd.user_id = td.user_id where cs.user_id = %s and cd.term_id = %s"
    result = cursor.execute(sql, (user_id, term_id))
    return_data = list()
    if result == 0:
        return return_data
    result = cursor.fetchall()
    for data in result:
        return_data.append({'course_id': data[0], 'course_name': data[1], 'teacher_name': data[2], 'score': data[3]})
    return return_data


def teacher_fetch_course(cursor, term, user_id):
    term_id = get_term_id(cursor, term)
    sql = "select cp.course_id, cp.course_name, cd.teacher_id, cd.capacity, cd.selected, cd.time, cr.location from selected_course sc join course_profile cp on sc.course_id = cp.course_id join course_detail cd on cp.course_id = cd.course_id join classroom cr on cd.classroom_id = cr.classroom_id where cd.user_id = %s and cd.term_id = %s"
    result = cursor.execute(sql, (user_id, term_id))
    return_data = list()
    if result == 0:
        return return_data
    result = cursor.fetchall()
    for data in result:
        return_data.append(
            {'course_id': data[0], 'course_name': data[1], 'teacher_id': data[2],
             'capacity': data[3], 'selected': data[4], 'time': data[5], 'location': data[6]})
    return return_data


def teacher_fetch_student(cursor, term, course_id, teacher_id):
    term_id = get_term_id(cursor, term)
    sql = "SELECT sd.student_name, sc.user_id, cs.usual_score, cs.final_score, cs.contribution FROM selected_course sc join course_score cs on sc.course_id = cs.course_id and sc.user_id = cs.user_id join student_detail sd on sc.user_id = sd.user_id where sc.course_id = %s and sc.teacher_id = %s and sc.term_id = %s"
    result = cursor.execute(sql, (course_id, teacher_id, term_id))
    print("!!!", result)
    return_data = list()
    if cursor.rowcount == 0:
        return return_data
    else:
        for data in cursor.fetchall():
            return_data.append({'student_name': data[0], 'student_id': data[1], 'daily_score': data[2],
                                'examination_score': data[3], 'contribution': data[4]})
            return return_data
        # sql = "SELECT * FROM selected_course sc join course_score cs on sc.course_id = cs.course_id and sc.user_id = cs.user_id join student_detail sd on sc.user_id = sd.user_id where sc.course_id = %s and sc.teacher_id = %s and sc.term_id = %s"
        # cursor.execute(sql, (course_id, teacher_id, term_id))
        # print(course_id, teacher_id, term_id)
        # print(cursor.fetchall())


def teacher_submit_score(cursor, data):
    course_id, teacher_id = data['course'].split('-')
    student_id = data['student_id']
    daily_score = data['daily_score']
    exam_score = data['examination_score']
    contribution = data['contribution']
    daily_contribute, exam_contribute = contribution.split(' ')
    sql = "lock tables course_score write"
    cursor.execute(sql)
    sql = "UPDATE course_score SET usual_score = %s, exam_score = %s, contribution = %s, final_score = usual_score * %s / 10 + exam_score * %s / 10 WHERE course_id = %s and user_id = %s"
    result = cursor.execute(sql, (
        daily_score, exam_score, contribution, daily_contribute, exam_contribute, course_id, student_id))
    sql = "unlock tables"
    cursor.execute(sql)
    if result == 0:
        return False
    return True
