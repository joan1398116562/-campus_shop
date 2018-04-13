import os
import datetime
from functools import wraps  # 登录装饰器

from werkzeug.utils import secure_filename

from . import home
from flask import render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash

from app import db, config
from sqlalchemy import desc

from home.forms import RegisterForm, LoginForm, UserForm, PasswordForm, AdminLoginForm

from app.models import User, AdminUser, Userlog, Product, Tag


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])  # 上传通过检查


def allowed_file(filename):
    """
    上传通过检查
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def change_name(filename):
    """
    修改文件名称
    """
    file_info = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + file_info[-1]
    return filename


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
        form.card.data = user.card
        form.info.data = user.info
        form.address.data = user.address
        form.location.data = user.location
    if form.validate_on_submit():
        data = form.data
        if form.face.data != "":
            file_face = secure_filename(form.face.data.filename)
            if not os.path.exists(config.FACE_FOLDER):
                os.makedirs(config.FACE_FOLDER)
                os.chmod(config.FACE_FOLDER)
            user.face = change_name(file_face)
            form.face.data.save(config.FACE_FOLDER + user.face)

        name_count = User.query.filter_by(name=data['name']).count()
        if data['name'] != user.name and name_count == 1:
            flash("用户名已经存在", 'err')
            return redirect(url_for('home.user'))

        email_count = User.query.filter_by(email=data['email']).count()
        if data['email'] != user.email and email_count == 1:
            flash("邮箱已经存在", 'err')
            return redirect(url_for('home.user'))

        phone_count = User.query.filter_by(phone=data['phone']).count()
        if data['phone'] != user.phone and phone_count == 1:
            flash("手机号码已经存在", 'err')
            return redirect(url_for('home.user'))

        card_count = User.query.filter_by(card=data['card']).count()
        if data['card'] != user.card and card_count == 1:
            flash("银行卡号码已经存在", 'err')
            return redirect(url_for('home.user'))

        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        user.card = data['card']
        user.info = data['info']
        user.address = data['address']
        user.location = data['location']

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


@home.route("/hot_sale/", methods=['GET'])
def hot_sale():
    # hots = Product.query.order_by('sell desc').all()
    page = request.args.get("page", 1, type=int)
    page_data = Product.query.order_by(Product.sell.desc())
    page_data = page_data.paginate(page=page, per_page=8, error_out=False)
    hots = page_data.items
    # print(hots)
    return render_template("home/hotsale.html", hots=hots, page_data=page_data, page=page)

#
# @home.route("/product_list/", methods=['GET'])
# def product_list():
#


@home.route('/detail/<product_id>/')
def detail(product_id):
    product_model = Product.query.filter(Product.id == product_id).first()
    return render_template('home/detail.html', product=product_model)

# @home.route("/detail/", methods=['GET'])
# def detail(id):
#     product = Product.query.filter_by(id=id).first()
#
#     return render_template("home/detail.html", product=product)


@home.route("/order/", methods=['GET'])
def order():
    return render_template("home/order.html")


@home.route("/try/", methods=['GET'])
def try_do():
    pic = Product.query.order_by(Product.sell.desc()).all()

    return render_template("home/try.html", pic=pic)





