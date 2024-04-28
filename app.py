from flask import Flask, jsonify, request
from flask_cors import cross_origin
import pymysql

app = Flask(__name__)
db = pymysql.Connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='257908',
    db='coursesystem',
    charset='utf8')


def check_db_connection():
    db.ping(reconnect=True)


@app.route('/api/login', methods=['OPTIONS', 'POST'])
@cross_origin()
def user_login():
    check_db_connection()
    cursor = db.cursor()
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
    check_db_connection()
    cursor = db.cursor()
    json_data = request.json
    sql = "SELECT * FROM course where 1 = 1"
    params = []
    # course_id: course_id,
    # course_name: course_name,
    # teacher_id: teacher_id,
    # teacher_name: teacher_name,
    # course_time: course_time
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
    print(sql)
    cursor.execute(sql, params)
    result = cursor.fetchall()
    # print(result)
    # course_id: selectedCourse.course_id,
    # course_name: selectedCourse.course_name,
    # teacher_id: selectedCourse.teacher_id,
    # teacher_name: selectedCourse.teacher_name,
    # capacity: selectedCourse.capacity,
    # selected_number: selectedCourse.selected,
    # time: selectedCourse.time
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
