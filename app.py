from flask import Flask, jsonify
from flask_cors import cross_origin

app = Flask(__name__)


@app.route('/api/users/123/pwd', methods=['OPTIONS', 'POST'])
@cross_origin()
def hello_world():  # put application's code here
    print('hello world')
    response = jsonify({"code" : 200, "data":{'userName': 'This is the response to OPTIONS request', "roleId": 1}})
    response.status_code = 200
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
