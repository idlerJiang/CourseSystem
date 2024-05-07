from flask import Flask, jsonify, request
from flask_cors import cross_origin
import pymysql
import sqltool

app = Flask(__name__)
db = pymysql.Connect(host='127.0.0.1', port=3306, user='root', passwd='257908', db='coursesystem', charset='utf8')


def get_cursor():
    db.ping(reconnect=True)
    return db.cursor()


def commit():
    db.ping(reconnect=True)
    db.commit()


@app.route('/api/login', methods=['OPTIONS', 'POST'])
@cross_origin()
def user_login():
    json_data = request.json
    print('attempting login by ID: ', json_data['id'])
    print('attempting login by password: ', json_data['password'])
    cursor = get_cursor()
    user_role, user_name = sqltool.login(cursor, json_data['id'], json_data['password'])
    if user_role == -1:
        response = jsonify(
            {"status": "Failed", "data": "系统错误！请联系管理员！"})
    elif user_role == 0:
        response = jsonify(
            {"status": "Failed", "data": "账号或密码错误！"})
    else:
        response = jsonify(
            {"status": "Success", "data": {'userName': user_name, "roleId": user_role}})
        response.status_code = 200
    cursor.close()
    commit()
    return response


@app.route('/api/querycourses', methods=['OPTIONS', 'POST'])
@cross_origin()
def query_course():
    cursor = get_cursor()
    json_data = request.json
    result = sqltool.query_course(cursor, json_data['course_id'], json_data['course_name'], json_data['teacher_id'], json_data['teacher_name'], json_data['course_time'])
    if len(result) == 0:
        response = jsonify()
        response.status_code = 204
    else:
        response = jsonify(result)
        response.status_code = 200
    cursor.close()
    commit()
    return response


@app.route('/api/queryselectedcourses', methods=['OPTIONS', 'GET'])
@cross_origin()
def query_selected_course():
    cursor = get_cursor()
    user_id = request.args.get("id")
    sql = "SELECT course_no FROM selectedcourse where student_id = %s"
    cursor.execute(sql, user_id)
    course_no_result = cursor.fetchall()
    if len(course_no_result) == 0:
        response = jsonify()
        response.status_code = 204
    else:
        result = []
        sql = "select * from course where course_no = %s"
        for course_no in course_no_result:
            cursor.execute(sql, course_no[0])
            result.append(cursor.fetchall())
        if len(result) == 0:
            response = jsonify()
            response.status_code = 204
        else:
            response_data = list()
            for data in result:
                data = data[0]
                response_data.append(
                    {'course_id': data[1], 'course_name': data[2], 'teacher_id': data[3], 'teacher_name': data[4],
                     'capacity': data[5], 'selected': data[6], 'time': data[7]})
            response = jsonify(response_data)
            response.status_code = 200
    cursor.close()
    return response


def check_schedule(user_id, course_time):
    schedule = [[0 for i in range(13)] for j in range(6)]
    cursor = get_cursor()
    sql = "SELECT time FROM course, selectedcourse where course.course_no = selectedcourse.course_no and selectedcourse.student_id = %s"
    cursor.execute(sql, user_id)
    result = cursor.fetchall()
    for temp in result:
        real_time = temp[0]
        for time in real_time.split(','):
            day = 0
            if time[0] == '一':
                day = 1
            elif time[0] == '二':
                day = 2
            elif time[0] == '三':
                day = 3
            elif time[0] == '四':
                day = 4
            elif time[0] == '五':
                day = 5
            time = time[1:].split('-')
            start = int(time[0])
            end = int(time[1])
            for i in range(start, end + 1):
                schedule[day][i] = 1
    for time in course_time.split(','):
        day = 0
        if time[0] == '一':
            day = 1
        elif time[0] == '二':
            day = 2
        elif time[0] == '三':
            day = 3
        elif time[0] == '四':
            day = 4
        elif time[0] == '五':
            day = 5
        time = time[1:].split('-')
        start = int(time[0])
        end = int(time[1])
        for i in range(start, end + 1):
            if schedule[day][i] != 0:
                return False
    return True


@app.route('/api/selectcourse', methods=['OPTIONS', 'POST'])
@cross_origin()
def select_course():
    hint = []
    cursor = get_cursor()
    json_data = request.json
    for course_info in json_data:
        sql = "SELECT * FROM selectedcourse where student_id = %s and course_id = %s"
        result = cursor.execute(sql, (course_info['user_id'], course_info['course_id']))
        if result != 0:
            hint.append(f"已选此课程 ({course_info['course_name']})")
        else:
            sql = "SELECT * FROM course where course_id = %s and teacher_id = %s"
            result = cursor.execute(sql, (course_info['course_id'], course_info['teacher_id']))
            if cursor.rowcount == 0:
                hint.append(f"课程不存在 ({course_info['course_name']})")
            else:
                result = cursor.fetchone()
                if result[5] <= result[6]:
                    hint.append(f"选课人数已满 ({course_info['course_name']})")
                elif not check_schedule(course_info['user_id'], result[7]):
                    hint.append(f"课程时间冲突 ({course_info['course_name']})")
                else:
                    sql = "UPDATE course SET selected = selected + 1 where course_id = %s and teacher_id = %s"
                    cursor.execute(sql, (result[1], result[3]))
                    sql = "INSERT INTO selectedcourse VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (result[0], result[1], result[3], course_info['user_id'], 0, 0, 0))
                    hint.append(f"选课成功 ({course_info['course_name']})")
    response = jsonify({"status": "Success", "data": hint})
    cursor.close()
    return response


@app.route('/api/dropcourse', methods=['OPTIONS', 'POST'])
@cross_origin()
def drop_course():
    hint = []
    cursor = get_cursor()
    json_data = request.json
    for course_info in json_data:
        sql = "SELECT * FROM selectedcourse where student_id = %s and course_id = %s"
        result = cursor.execute(sql, (course_info['user_id'], course_info['course_id']))
        if result == 0:
            hint.append(f"未选此课程 ({course_info['course_name']})")
        else:
            sql = "DELETE FROM selectedcourse where course_id = %s and student_id = %s"
            cursor.execute(sql, (course_info['course_id'], course_info['user_id']))
            sql = "UPDATE course SET selected = selected - 1 where course_id = %s and teacher_id = %s"
            cursor.execute(sql, (course_info['course_id'], course_info['teacher_id']))
            hint.append(f"退课成功 ({course_info['course_name']})")
    response = jsonify({"status": "Success", "data": hint})
    cursor.close()
    return response


@app.route('/api/fetchscore', methods=['OPTIONS', 'GET'])
@cross_origin()
def fetch_score():
    user_id = request.args.get("id")
    response_data = []
    cursor = get_cursor()
    sql = "SELECT course.course_id, course.course_name, course.teacher_name, selectedcourse.student_total_score FROM course,selectedcourse where selectedcourse.student_id = %s and course.course_no = selectedcourse.course_no"
    result = cursor.execute(sql, user_id)
    if cursor.rowcount == 0:
        response = jsonify()
    else:
        for data in cursor.fetchall():
            response_data.append(
                {'course_id': data[0], 'course_name': data[1], 'teacher_name': data[2], 'score': data[3]})
        response = jsonify(response_data)
    cursor.close()
    response.status_code = 200
    return response


@app.route('/api/teachers/fetchcourse', methods=['OPTIONS', 'GET'])
@cross_origin()
def teacher_fetch_course():
    user_id = request.args.get("id")
    response_data = []
    cursor = get_cursor()
    sql = "SELECT * FROM course where teacher_id = %s"
    result = cursor.execute(sql, user_id)
    if cursor.rowcount == 0:
        response = jsonify()
    else:
        for data in cursor.fetchall():
            response_data.append(
                {'course_id': data[1], 'course_name': data[2], 'teacher_id': data[3], 'teacher_name': data[4],
                 'capacity': data[5], 'selected': data[6], 'time': data[7]})
        response = jsonify(response_data)
    cursor.close()
    response.status_code = 200
    return response


@app.route('/api/teachers/fetchstudent', methods=['OPTIONS', 'POST'])
@cross_origin()
def teacher_fetch_student():
    json_data = request.json
    response_data = []
    cursor = get_cursor()
    sql = (
        "SELECT user.user_name, selectedcourse.course_id, selectedcourse.teacher_id, selectedcourse.student_id, selectedcourse.student_usual_score, selectedcourse.student_exam_score FROM user, selectedcourse where selectedcourse.teacher_id = %s and selectedcourse.course_id = %s and user.user_id = selectedcourse.student_id")
    result = cursor.execute(sql, (json_data['user_id'], json_data['course_id']))
    if cursor.rowcount == 0:
        response = jsonify()
        response.status_code = 204
    else:
        for data in cursor.fetchall():
            response_data.append(
                {'course_id': data[1], 'teacher_id': data[2], 'student_id': data[3],
                 'student_name': data[0], 'daily_score': data[4], 'examination_score': data[5]})
        response = jsonify(response_data)
        response.status_code = 200
    cursor.close()
    return response


@app.route('/api/teachers/submitscore', methods=['OPTIONS', 'POST'])
@cross_origin()
def teacher_submit_score():
    json_data = request.json
    cursor = get_cursor()
    for data in json_data:
        sql = "UPDATE selectedcourse SET student_usual_score = %s, student_exam_score = %s, student_total_score = 0.4 * %s + 0.6 * %s WHERE course_id = %s and student_id = %s"
        result = cursor.execute(sql, (
        data['daily_score'], data['examination_score'], data['daily_score'], data['examination_score'],
        data['course_id'], data['student_id']))
    response = jsonify()
    cursor.close()
    response.status_code = 200
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
