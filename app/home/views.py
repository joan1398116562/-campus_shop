from . import home
from flask import render_template, redirect, url_for


@home.route("/")
def index():
    return render_template("home/base.html")


@home.route("/login/")
def login():
    """
    登录视图
    :return: login.html
    """
    return render_template("home/login.html")


@home.route("/register/")
def register():
    """
    注册视图
    :return: register.html
    """
    return render_template("home/register.html")


@home.route("/user/")
def user():
    """
    用户信息中心视图
    :return: user.html
    """
    return render_template("home/user.html")
