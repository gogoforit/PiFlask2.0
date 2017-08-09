import os
import time
import datetime
from mongoengine import *
from mongoengine.context_managers import switch_db
from flask import flash
from flask_bootstrap import Bootstrap
from flask import Flask, Response, redirect, url_for, request, session, abort, render_template
from flask.ext.login import LoginManager, UserMixin, \
    login_required, login_user, logout_user

local_username = os.environ['LOCAL_USERNAME']
local_password = os.environ['LOCAL_PASSWORD']
local_host = os.environ['LOCAL_HOST']
local_db = os.environ['LOCAL_DB']
remote_username = os.environ['REMOTE_USERNAME']
remote_password = os.environ['REMOTE_PASSWORD']
remote_host = os.environ['REMOTE_HOST']
remote_db = os.environ['REMOTE_DB']
remarks_username = os.environ['REMARKS_USERNAME']
remarks_password = os.environ['REMARKS_PASSWORD']

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

app = Flask(__name__)
app.config.from_object(__name__)
bootstrap = Bootstrap(app)

# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

users = User('wxwifisign')


def get_macs():
    pid = get_pid()
    mycommand = "create_ap --list-clients " + pid
    info = os.popen(mycommand)
    info = info.read()
    info = info.split('\n')
    ip_mac = {}
    for each in info:
        ip = None
        mac = None
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

def get_now_datetime():
    now_hour = time.strftime('%H')
    now_min = time.strftime('%M')
    now_sec = time.strftime('%S')
    now_time = datetime.time(int(now_hour), int(now_min), int(now_sec))
    return now_time

def get_class_num():
    now_time = get_now_datetime()
    info = {}
    class_time_start_1 = datetime.time(8, 0, 0)
    class_time_end_1 = datetime.time(10, 0, 0)
    class_time_start_2 = datetime.time(10, 5, 0)
    class_time_end_2 = datetime.time(12, 0, 0)
    class_time_start_3 = datetime.time(14, 30, 0)
    class_time_end_3 = datetime.time(16, 0, 0)
    class_time_start_4 = datetime.time(16, 0, 0)
    class_time_end_4 = datetime.time(18, 0, 0)
    if now_time > class_time_start_1 and now_time < class_time_end_1:
        info['class_num'] = '1'
    elif now_time > class_time_start_2 and now_time < class_time_end_2:
        info['class_num'] = '2'
    elif now_time > class_time_start_3 and now_time < class_time_end_3:
        info['class_num'] = '3'
    elif now_time > class_time_start_4 and now_time < class_time_end_4:
        info['class_num'] = '4'
    else:
        info['class_num'] = '5'
    return info['class_num']


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
        if (mac[2] != '-' or mac[5] != '-' or mac[8] != '-' or mac[11] != '-'):
            flash('输入格式错误，请检查您的输入是否包含非法符号！')
        if Student.objects(name=name):
            flash('姓名与数据库中信息冲突，请确认后，重新输入！')
        elif Student.objects(address_mac=mac):
            flash('mac地址与数据库中信息冲突，请确认后，重新输入！')
        else:
            student = Student(name=name, class_id=class_id, address_mac=address_mac, student_id=student_id)
            student.save()
            flash('注册成功！')
        return render_template('register.html')


@app.route('/query', methods={'POST', 'GET'})
def query():
    from moduls.student_info import StudentInfo
    with switch_db(StudentInfo, 'remote_db') as StudentInfo:
        if request.method == 'GET':
            return render_template('query.html')
        form = request.form
        name = form.get('name')
        date = form.get('date')
        class_id = form.get('class_id')
        if not StudentInfo.objects(name=name, date=date, class_id=class_id):
            flash('对不起，没有该学生签到信息，请确认后，重新输入！')
            return render_template('query.html')
        else:
            students_sign_info = StudentInfo.objects(name=name, date=date, class_id=class_id)
            sign_info = []
            for student_sign_info in students_sign_info:
                sign_info.append(student_sign_info)
            return render_template('query.html', sign_info=sign_info)


@app.route('/modify_information', methods={'POST', 'GET'})
def modify_information():
    if request.method == 'GET':
        return render_template('modify_information.html')
    form = request.form
    name = form.get('name')
    mac_old = form.get('mac-old')
    macs = get_macs()
    ip = request.remote_addr
    mac = macs[ip]
    mac = mac.lower()
    mac_old = mac_old.lower()
    if len(mac) != 17:
        flash('新的mac长度有误，请确认后再输入！')
    if(mac[2] != '-' or mac[5] != '-' or mac[8] != '-' or mac[11] != '-'):
        flash('新的mac输入格式错误，请检查您的输入是否包含非法符号！')
    if len(mac_old) != 17:
        flash('旧的mac长度有误，请确认后再输入！')
    if (mac_old[2] != '-' or mac_old[5] != '-' or mac_old[8] != '-' or mac_old[11] != '-'):
        flash('旧的mac输入格式错误，请检查您的输入是否包含非法符号！')
    from moduls.student import Student
    with switch_db(Student, 'local_db') as Student:
        if not Student.objects(name=name):
            flash('数据库中没有您的信息，请确认后，重新输入！')
        elif not Student.objects(address_mac=mac_old):
            flash('您旧的MAC地址错误，请确认后，重新输入！')
        elif Student.objects(address_mac=mac):
            flash('该mac已经被注册，请确认后，重新输入！')
        else:
            student = Student.objects(name=name).first()
            student.address_mac = mac
            student.save()
            flash('修改成功！')
    return render_template('modify_information.html')


# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == remarks_password and username == remarks_username:
            id = remarks_username
            user = User(id)
            login_user(user)
            return redirect(url_for('remarks'))
        else:
            return abort(401)
    else:
        return render_template('login.html')


@app.route('/remarks', methods=['GET', 'POST'])
@login_required
def remarks():
    from moduls.remarks import Remarks
    if request.method == 'GET':
        return render_template('remarks.html')
    else:
        with switch_db(Remarks, 'local_db') as Remarks:
            if Remarks.objects(class_id=request.form['class_id'],
                               class_num=get_class_num()):
                remarks_info = Remarks.objects(class_id=request.form['class_id'],
                                          class_num=get_class_num()).first()
                remarks_info['remarks'] = request.form['remarks']
                remarks_info.save()
                flash('修改成功')
                return render_template('remarks.html')
            else:
                remarks = Remarks(class_id=request.form['class_id'],
                                  class_num=get_class_num(),
                                  remarks=request.form['remarks'])
                remarks.save()
                flash('设置成功')
                return render_template('remarks.html')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)


if __name__ == '__main__':
    app.run(port=8899)