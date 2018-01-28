from . import home
from flask import render_template, redirect, url_for


@home.route("/")
def index():
    return render_template("home/home.html")


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
