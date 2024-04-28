from flask import Flask, jsonify, request
from flask_cors import cross_origin
import pymysql

app = Flask(__name__)


@app.route('/api/login', methods=['OPTIONS', 'POST'])
@cross_origin()
def user_login():
    db = pymysql.Connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        passwd='257908',
        db='coursesystem',
        charset='utf8')
    cursor = db.cursor()
    json_data = request.json
    print('attempting login with ID:', json_data['id'])
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
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
