from flask import Flask, jsonify, request
from flask_cors import cross_origin
import pymysql

app = Flask(__name__)
db = pymysql.Connect(host='127.0.0.1', port=3306, user='root', passwd='257908', db='coursesystem', charset='utf8',
                     autocommit=True)


def get_cursur():
    db.ping(reconnect=True)
    return db.cursor()


@app.route('/api/login', methods=['OPTIONS', 'POST'])
@cross_origin()
def user_login():
    cursor = get_cursur()
    json_data = request.json
    print('attempting login from ID:', json_data['id'])
    cursor.execute("SELECT * FROM user where user_id = %s and user_password = %s",
                   (json_data['id'], json_data['password']))
    result = cursor.fetchall()
    print(len(result))
    if len(result) == 0:
        response = jsonify(
            {"status": "Failed", "data": "用户名或密码错误"})
    else:
        response = jsonify(
            {"status": "Success", "data": {'userName': result[0][1], "roleId": result[0][3]}})
        response.status_code = 200
    cursor.close()
    return response


@app.route('/api/querycourses', methods=['OPTIONS', 'POST'])
@cross_origin()
def query_course():
    cursor = get_cursur()
    json_data = request.json
    sql = "SELECT * FROM course where 1 = 1"
    params = []
    if json_data['course_id'] is not None:
        print(json_data['course_id'])
        sql += " AND course_id like %s"
        params.append("%" + str(json_data['course_id']) + "%")
    if json_data['course_name'] is not None:
        print(json_data['course_name'])
        sql += " AND course_name like %s"
        params.append("%" + str(json_data['course_name']) + "%")
    if json_data['teacher_id'] is not None:
        print(json_data['teacher_id'])
        sql += " AND teacher_id like %s"
        params.append("%" + str(json_data['teacher_id']) + "%")
    if json_data['teacher_name'] is not None:
        print(json_data['teacher_name'])
        sql += " AND teacher_name like %s"
        params.append("%" + str(json_data['teacher_name']) + "%")
    if json_data['course_time'] is not None:
        print(json_data['course_time'])
        sql += " AND course_time like %s"
        params.append("%" + str(json_data['course_time']) + "%")
    cursor.execute(sql, params)
    result = cursor.fetchall()
    if len(result) == 0:
        response = jsonify()
        response.status_code = 204
    else:
        response_data = list()
        for data in result:
            response_data.append(
                {'course_id': data[1], 'course_name': data[2], 'teacher_id': data[3], 'teacher_name': data[4],
                 'capacity': data[5], 'selected': data[6], 'time': data[7]})
        response = jsonify(response_data)
        response.status_code = 200
    cursor.close()
    return response


@app.route('/api/queryselectedcourses', methods=['OPTIONS', 'GET'])
@cross_origin()
def query_selected_course():
    cursor = get_cursur()
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
    cursor = get_cursur()
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
    cursor = get_cursur()
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
    cursor = get_cursur()
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
    cursor = get_cursur()
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
    cursor = get_cursur()
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
