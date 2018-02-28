"""
注册蓝图
"""
from flask import Flask
# from flask_bootstrap import Bootstrap

from flask_admin import Admin, BaseView, expose

app = Flask(__name__)
# Bootstrap(app)

# 开启调试模式
app.debug = True

from app.home import home as home_blueprint
# from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
# app.register_blueprint(admin_blueprint, url_prefix="/admin")