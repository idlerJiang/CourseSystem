from flask import Flask, jsonify, request
from flask_cors import cross_origin
import pymysql

app = Flask(__name__)
db = pymysql.Connect(host='127.0.0.1', port=3306, user='root', passwd='257908', db='coursesystem', charset='utf8')


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
            print( "???",course_no[0])
            cursor.execute(sql, course_no[0])
            result.append(cursor.fetchall())
            print("!!!",result)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
