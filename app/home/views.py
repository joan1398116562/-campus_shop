import os
from functools import wraps  # 登录装饰器

from werkzeug.utils import secure_filename

from . import home
from flask import render_template, redirect, url_for, flash, session, request

from werkzeug.security import generate_password_hash

from app import db

from home.forms import RegisterForm, LoginForm, UserForm, PasswordForm, AdminLoginForm

from app.models import User, AdminUser, Userlog, Product, Tag


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])  # 上传通过检查


def allowed_file(filename):
    """
    上传通过检查
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def user_login_dec(f):
    """
    登录装饰器
    已登录就可以访问，否则重定向至登录，next页面为当前请求的url
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for('home.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@home.route("/login/", methods=["GET", "POST"])
def login():
    """
    登录视图
    :return: login.html
    """
    if request.method == 'GET':  # get请求
        form = LoginForm()
        return render_template('home/login.html', form=form)
    else:   # post请求
        form = LoginForm(request.form)
        if form.validate_on_submit():
            data = form.data
            user = User.query.filter_by(name=data['name']).first()
            if user:
                if not user.check_password(data['password']):
                    flash("密码错误", 'err')
                    return redirect(url_for('home.login'))
            else:
                flash("输入的账户不存在", 'err')
                return redirect(url_for('home.login'))

            session['user'] = user.name
            session['user_id'] = user.id
            userlog = Userlog(
                user_id=user.id
            )
            db.session.add(userlog)
            db.session.commit()
            return redirect(url_for('home.user'))
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
            password=generate_password_hash(data["password"])
        )
        db.session.add(user)
        db.session.commit()
        #     数据库事务回滚
        # except
        #     db.session.rollback()

        flash("你已经成功注册", "ok")

    return render_template("home/register.html", form=form)


@home.route("/user/", methods=["GET", "POST"])
@user_login_dec
def user():
    """
    用户信息中心视图
    :return: user.html
    """
    form = UserForm()
    user = User.query.get(int(session['user_id']))
    form.face.validators = []
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
    if form.validate_on_submit():
        data = form.data
        if form.face.data != "":
            file_face = secure_filename(form.face.data.filename)
            if not os.path.exists(app.config["FACE_FOLDER"]):
                os.makedirs(app.config["FACE_FOLDER"])
                os.chmod(app.config["FACE_FOLDER"])

        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']

        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()

        flash("你的信息已经修改成功", 'ok')
        return redirect(url_for('home.user'))

    return render_template("home/user.html", form=form, user=user)


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
        db.session.commit()
        return redirect(url_for('home.login'))
    return render_template("home/pwd.html", form=form)


@home.route("/logout/")
def logout():
    """
    退出登录视图
    :return: redirect to login
    """
    session.pop("user", None)
    session.pop("user_id", None)

    return redirect(url_for('home.login'))


@home.route("/<int:page>/", methods=['GET'])
@home.route("/", methods=["GET"])
def index(page=None):
    tags = Tag.query.all()
    page_data = Product.query
    # 分类
    tid = request.args.get("tid", 0)
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))
    # 时间
    time = request.args.get("time", 0)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(Product.add_time.desc())
        else:
            page_data = page_data.order_by(Product.add_time.asc())
    # 销量
    sell = request.args.get("sell", 0)
    if int(sell) != 0:
        if int(sell) == 1:
            page_data = page_data.order_by(Product.sell.desc())
        else:
            page_data = page_data.order_by(Product.sell.asc())
    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=8)
    p = dict(
        tid=tid,
        time=time,
        sell=sell,
    )
    return render_template("home/index.html", tags=tags, p=p, page_data=page_data)


@home.route("/order/", methods=['GET'])
def order():
    return render_template("home/order.html")


