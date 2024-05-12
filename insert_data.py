import hashlib

import pymysql

db = pymysql.Connect(host='127.0.0.1', port=3306, user='root', passwd='257908', db='coursesystem', charset='utf8')


# def sql():
#     with open("course.txt", "r", encoding="utf-8") as file:
#         datas = file.readlines()
#         db.ping(reconnect=True)
#         cursor = db.cursor()
#         id = 10000001
#         count = 0
#         for data in datas:
#             data = data.split('\t')
#             # 学期	课程号	教师号	教师id	教室id	时间	容量
#             term_id = data[0].strip()
#             course_id = data[1].strip()
#             teacher_id = data[2].strip()
#             user_id = data[3].strip()
#             classroom = data[4].strip()
#             time = data[5].strip()
#             capacity = data[6].strip()
#
#             print(term_id, course_id, teacher_id, user_id, classroom, time, capacity)
#
#             sql = "insert into course_detail(course_id, teacher_id, term_id, user_id, time, classroom_id, capacity) values(%s,%s,%s,%s,%s,%s,%s)"
#             print(cursor.execute(sql, (course_id, teacher_id, term_id, user_id, time, classroom, capacity)))
#             db.commit()
#             # id += 1
#             # count += 1
#             # if id <= 10000045:
#             #     continue
#             # collage = count // 10 + 1
#             # # 待加密信息
#             # password = hashlib.md5((str(id) + name).encode("utf-8")).hexdigest()
#
#             # sql = "insert into user_profile (user_id, password, user_role) values (%s, %s, 2)"
#             # print(cursor.execute(sql, (id, password)))
#             # db.commit()
#             # sql = "insert into teacher_detail (user_id, teacher_name, collage_id) values (%s, %s, %s)"
#             # print(cursor.execute(sql, (id, name, collage)))
#             # db.commit()


def sql():
    for i in range(10000001, 10000047):
        password = hashlib.md5((str(i) + "123456").encode("utf-8")).hexdigest()
        sql = "update user_profile set password=%s where user_id=%s"
        db.ping(reconnect=True)
        cursor = db.cursor()
        print(cursor.execute(sql, (password, i)))
        db.commit()


if __name__ == '__main__':
    sql()
