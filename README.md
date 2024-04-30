# Todo
1. 修改数据库中teacher_id存储以及检索方式
2. bug待测试
3. 存储混乱待优化

# 数据库结构
create table user
(
    user_id         int auto_increment
        primary key,
    user_name       varchar(64) not null,
    user_password   varchar(32) not null,
    user_role       tinyint     not null,
    user_collage_id int         not null,
    constraint user_id_UNIQUE
        unique (user_id)
);

create table course
(
    course_no    int auto_increment
        primary key,
    course_id    varchar(8)                     not null,
    course_name  varchar(32) default '暂无名称' not null,
    teacher_id   varchar(8)                     not null,
    teacher_name varchar(64) default '暂无老师' not null,
    capacity     int                            not null,
    selected     int         default 1          not null,
    time         tinytext                       not null,
    status       tinyint     default 1          not null,
    constraint course_no_UNIQUE
        unique (course_no)
);

create table selectedcourse
(
    course_no           int              not null
        primary key,
    course_id           int              not null,
    teacher_id          int              not null,
    student_id          int              not null,
    student_usual_score double default 0 null,
    student_exam_score  double default 0 null,
    student_total_score double default 0 null
);

## 下表实际未使用

create table collages
(
    collage_id   int         not null
        primary key,
    collage_name varchar(32) not null
);





