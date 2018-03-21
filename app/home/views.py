import os
from functools import wraps  # 登录装饰器

from werkzeug.utils import secure_filename

from . import home
from flask import render_template, redirect, url_for, flash, session, request

from werkzeug.security import generate_password_hash

from app import db

from home.forms import RegisterForm, LoginForm, UserForm, PasswordForm, AdminLoginForm

from app.models import User, AdminUser


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])  # 上传通过检查


def allowed_file(filename):
    """
    上传通过检查
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def user_login_dec(f):
    """
    登录装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for('home.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@home.route("/")
def index():
    """
    首页视图
    :return: index.html
    """
    return render_template("home/index.html")


@home.route("/login/", methods=["GET", "POST"])
def login():
    """
    登录视图
    :return: login.html
    """
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if user:
            if not user.check_password(data["password"]):
                flash("输入的密码错误", "error")
                return redirect(url_for('home.login'))
        else:
            flash("账户不存在", "error")
            return redirect(url_for('home.login'))
        session["user"] = user.name
        session["user_id"] = user.id
        try:
            db.session.commit()
        except:
            db.session.rollback()
        # return redirect(url_for('home.user'))
    return render_template('home/login.html', form=form)


@home.route("/register/", methods=["GET", "POST"])
def register():
    """
    注册视图
    :return: register.html
    """
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            password=data["password"]
        )
        db.session.add(user)
        try:
            db.session.commit()
        #     数据库事务回滚
        except:
            db.session.rollback()

        flash("你已经成功注册", "ok")
    return render_template("home/register.html", form=form)


@home.route("/user/", methods=["GET", "POST"])
@user_login_dec
def user():
    """
    用户信息中心视图
    :return: user.html
    """
    form = UserForm
    user = User.query.get(int(session["user"]))
    form.face.validators = []
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
    if form.validate_on_submit():
        data = form.data
        # if form.face.data != "":
        #     file_face = secure_filename(form.face.data.filename)
        #     if not os.path.exists(app.config["FACE_FOLDER"]):
        #         os.makedirs(app.config["FACE_FOLDER"])
        #         os.chmod(app.config["FACE_FOLDER"])
    return render_template("home/user.html")


@home.route("/pwd/", methods=["GET", "POST"])
@user_login_dec
def pwd():
    """
    修改密码视图
    :return:  pwd.html
    """
    form = PasswordForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=session["user"]).first()
        if not user.check_password(data["old_password"]):
            flash("旧密码错误", "error")
            return redirect(url_for('home.pwd'))
        user.pwd = generate_password_hash(data["new_password"])
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
    return render_template("home/pwd.html")

