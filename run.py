import os
from mongoengine import *
from mongoengine.context_managers import switch_db
from flask import flash
from flask import Flask
from flask_bootstrap import Bootstrap
from flask import render_template
from flask import request
from moduls.student import Student

local_username = os.environ['LOCAL_USERNAME']
local_password = os.environ['LOCAL_PASSWORD']
local_host = os.environ['LOCAL_HOST']
local_db = os.environ['LOCAL_DB']
remote_username = os.environ['REMOTE_USERNAME']
remote_password = os.environ['REMOTE_PASSWORD']
remote_host = os.environ['REMOTE_HOST']
remote_db = os.environ['REMOTE_DB']

connect(db=remote_db,
        host=remote_host,
        username=remote_username,
        password=remote_password,
        alias='remote_db')

connect(db=local_db,
        host=local_host,
        username=local_username,
        password=local_password,
        alias='local_db')


app_secret_key = os.environ['APP_SECRET_KEY']
app = Flask(__name__)
app.config.from_object(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'hard to guess'
app.secret_key = app_secret_key


def get_macs():
    pid = get_pid()
    mycommand = "create_ap --list-clients " + pid
    info = os.popen(mycommand)
    info = info.read()
    info = info.split('\n')
    ip_mac = {}
    i = 0
    for each in info:
        ip = None
        mac = None
        print(each)
        theinfo = each.split(' ')
        for each2 in theinfo:
          if ':' in each2:
           each2 = each2.replace(':','-')
           mac = each2
          else:
              if each2.startswith('192'):
                  ip = each2
        ip_mac[ip] = mac
    return ip_mac


def get_pid():
    k = os.popen("create_ap  --list-running")
    k = k.read()
    k = k.split('\n')
    k = k[2].split(' ')
    pid = k[0]
    return pid


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/register', methods={'POST', 'GET'})
def register():
    from moduls.student import Student
    with switch_db(Student, 'local_db') as Student:
        if request.method == 'GET':
            return render_template('register.html')
        macs = get_macs()
        ip = request.remote_addr
        mac = macs[ip]
        mac = mac.replace(':', '-')
        address_mac = mac.lower()
        form = request.form
        name = form.get('name')
        student_id = form.get('student_id')
        class_id = form.get('class_number')
        if len(mac) != 17:
            flash('mac长度有误，请确认后再输入！')
            return render_template('register.html')
        if (mac[2] != '-' or mac[5] != '-' or mac[8] != '-' or mac[11] != '-'):
            flash('输入格式错误，请检查您的输入是否包含非法符号！')
            return render_template('register.html')
        if Student.objects(name=name):
            flash('姓名与数据库中信息冲突，请确认后，重新输入！')
            return render_template('register.html')
        elif Student.objects(address_mac=mac):
            flash('mac地址与数据库中信息冲突，请确认后，重新输入！')
            return render_template('register.html')
        else:
            student = Student(name=name, class_id=class_id, address_mac=address_mac, student_id=student_id)
            student.save()
            flash('注册成功！')
            return render_template('register.html')


# @app.route('/query', methods={'POST', 'GET'})
# def query():
#     app.config['MONGODB_SETTINGS'] = {  # 配置MongoDB
#         'db': mongo_db,
#         'host': mongo_host,
#         'port': int(mongo_port),
#         'username': mongo_username,
#         'password': mongo_password
#     }
#     if request.method == 'GET':
#         return render_template('query.html')
#     form = request.form
#     name = form.get('name')
#     date = form.get('date')
#     student_sign_infos = 1
#     conn.open_connection('qiandao_last_info')
#     student_sign_infos = conn.getIds('info', {'name': name, 'date': date})
#     student_sign_info = next(student_sign_infos, None)
#     # 储存给前端页面的签到信息
#     sign_info = []
#     if student_sign_info == None:
#         flash('对不起，没有该学生签到信息，请确认后，重新输入！')
#         return render_template('query.html')
#     else:
#         while student_sign_info:
#             # print(_id)
#             sign_info.append(student_sign_info)
#             student_sign_info = next(student_sign_infos, None)
#         print(sign_info)
#         return render_template('query.html',sign_info = sign_info)


if __name__ == '__main__':
    app.run()