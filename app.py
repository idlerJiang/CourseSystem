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


@app.route('/api/getterm', methods=['OPTIONS', 'GET'])
@cross_origin()
def get_term():
    cursor = get_cursor()
    result = sqltool.get_term(cursor)

    if len(result) == 0:
        response = jsonify()
        response.status_code = 204
    else:
        response = jsonify(result)
        response.status_code = 200
    cursor.close()
    commit()
    return response


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
    result = sqltool.query_course(cursor, json_data['term'], json_data['course_id'], json_data['course_name'],
                                  json_data['teacher_id'],
                                  json_data['teacher_name'], json_data['course_time'])
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
    term = request.args.get("term")
    result = sqltool.query_selected_course(cursor, term, user_id)
    response = jsonify(result)
    if len(result) == 0:
        response.status_code = 204
    commit()
    cursor.close()
    return response


@app.route('/api/selectcourse', methods=['OPTIONS', 'POST'])
@cross_origin()
def select_course():
    result = []
    cursor = get_cursor()
    json_data = request.json
    for course_info in json_data:
        result.append(
            sqltool.select_course(cursor, course_info['term'], course_info['user_id'], course_info['course_id'],
                                  course_info['teacher_id']))
        commit()
    response = jsonify({"status": "Success", "data": result})
    commit()
    cursor.close()
    return response


@app.route('/api/dropcourse', methods=['OPTIONS', 'POST'])
@cross_origin()
def drop_course():
    result = []
    cursor = get_cursor()
    json_data = request.json
    for course_info in json_data:
        result.append(
            sqltool.drop_course(cursor, course_info['term'], course_info['user_id'], course_info['course_id'],
                                course_info['teacher_id']))
        commit()
    response = jsonify({"status": "Success", "data": result})
    commit()
    cursor.close()
    return response


@app.route('/api/fetchscore', methods=['OPTIONS', 'GET'])
@cross_origin()
def fetch_score():
    user_id = request.args.get("id")
    term = request.args.get("term")
    response_data = []
    cursor = get_cursor()
    result = sqltool.fetch_score(cursor, term, user_id)
    if len(result) == 0:
        response = jsonify()
        response.status_code = 204
    else:
        response = jsonify(result)
        response.status_code = 200
    commit()
    cursor.close()
    return response


@app.route('/api/teachers/fetchcourse', methods=['OPTIONS', 'GET'])
@cross_origin()
def teacher_fetch_course():
    user_id = request.args.get("id")
    term = request.args.get("term")
    cursor = get_cursor()
    result = sqltool.teacher_fetch_course(cursor, term, user_id)
    if len(result) == 0:
        response = jsonify()
        response.status_code = 204
    else:
        response = jsonify(result)
        response.status_code = 200
    commit()
    cursor.close()
    return response


@app.route('/api/teachers/fetchstudent', methods=['OPTIONS', 'POST'])
@cross_origin()
def teacher_fetch_student():
    json_data = request.json
    user_id = json_data['user_id']
    course_id, teacher_id = json_data['course'].split('-')
    term = json_data['term']
    cursor = get_cursor()

    result = sqltool.teacher_fetch_student(cursor, term, course_id, teacher_id)
    if len(result) == 0:
        response = jsonify()
        response.status_code = 204
    else:
        response = jsonify(result)
        response.status_code = 200
    commit()
    cursor.close()
    return response


@app.route('/api/teachers/submitscore', methods=['OPTIONS', 'POST'])
@cross_origin()
def teacher_submit_score():
    json_data = request.json
    cursor = get_cursor()
    for data in json_data:
        result = sqltool.teacher_submit_score(cursor, data)
    response = jsonify()
    response.status_code = 200
    commit()
    cursor.close()
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
