"""
注册蓝图
"""
import os
import os.path as op

from jinja2 import Markup

from flask import Flask, render_template, url_for, redirect, request, abort, flash

from wtforms import form, fields, validators
import flask_login as login
import flask_admin as admin
from flask_admin import Admin, form
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_admin import expose
from flask_babelex import Babel  # flask-admin的国际化

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.event import listens_for

from werkzeug.security import generate_password_hash, check_password_hash

from app.models import db
from models import User, Product, Tag, Comment, AdminUser
from home.forms import AdminLoginForm ,RegistrationForm

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")  # 上传文件路径
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

file_path = op.join(op.dirname(__file__), 'static/uploads/products/')  # 商品文件上传路径

app = Flask(__name__)

babel = Babel(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FACE_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")  # 头像路径

app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'  # 修改后台翻译为中文

app.config.from_object('config')

"""
flask-login
"""
# 初始化flask-login


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # 创建管理员加载函数
    @login_manager.user_loader
    def load_user(adminuser_id):
        return db.session.query(AdminUser).get(adminuser_id)

# 创建定制的model view class


class MyModelView(sqla.ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated

    def on_model_change(self, form, model, is_created):
        AdminUser.password = form.password_hash.data


# 创建定制的flask-admin主页视图(注册和登录逻辑):
class MyAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=("GET", "POST"))
    def login_view(self):
        """管理员登录"""
        form = AdminLoginForm(request.form)
        if admin_helpers.validate_form_on_submit(form):
            adminuser = form.get_user()
            login.login_user(adminuser)
            flash(u'你已经成功登录')

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = '<p>还没有账户？ <a href="' + url_for('.register_view') + '">点击这里注册</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if admin_helpers.validate_form_on_submit(form):
            adminuser = AdminUser()

            form.populate_obj(adminuser)

            adminuser.password = generate_password_hash(form.password.data)

            db.session.add(adminuser)

            try:
                db.session.commit()
            except:
                db.session.rollback()

            login.login_user(adminuser)
            return redirect(url_for('.index'))

        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">点击这里登录.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


# 初始化flask_login
init_login()


"""
flask-admin
"""

admin = Admin(app, name=u'校园商铺管理系统', template_mode='bootstrap3',
                   index_view=MyAdminIndexView(), base_template='my_master.html')

admin.add_view(MyModelView(AdminUser, db.session, name=u'管理员管理'))

admin.add_view(ModelView(User, db.session, name=u'用户管理'))
admin.add_view(ModelView(Product, db.session, name=u'商品管理'))
admin.add_view(ModelView(Tag, db.session, name=u'标签管理'))
admin.add_view(ModelView(Comment, db.session, name=u'评论管理'))


class UserView(ModelView):
    pass


class ProductView(ModelView):
    # 设置缩略图
    def _list_thumbnail(view, context, model, name):
        if not model.head_img:
            return ''
        return Markup(
            '<img src="%s">' % url_for('static/uploads/products', filename=form.thumbgen_filename(model.head_img)))

    # 格式化列表图像显示
    column_formatters = {
        'head_img': _list_thumbnail
    }
    # 扩展列表显示的头像为60*60像素
    form_extra_fields = {
        'head_img': form.ImageUploadField('Image',
                                          base_path=file_path,
                                          relative_path='uploadFile/',
                                          thumbnail_size=(60, 60, True))
    }

    # 监听删除图片, 当该商品被删除时,同时在磁盘上把图片删除
    @listens_for(Product, 'after_delete')
    def del_image(mapper, connection, target):
        if target.head_img:
            # Delete image
            try:
                os.remove(op.join(file_path, target.head_img))
            except OSError:
                pass

            # Delete thumbnail
            try:
                os.remove(op.join(file_path,
                                  form.thumbgen_filename(target.head_img)))
            except OSError:
                pass


class TagView(ModelView):
    pass


class CommentView(ModelView):
    pass


# 开启调试模式
app.debug = True

from app.home import home as home_blueprint

app.register_blueprint(home_blueprint)

"""
定制错误界面
"""


@app.errorhandler(404)
def page_not_found(error):
    """
    404错误
    :param error:
    :return: home/404.html
    """
    return render_template("home/404.html"), 404
