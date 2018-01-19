from . import home
from flask import render_template, redirect, url_for


@home.route("/")
def index():
    return render_template("home/home.html")


@home.route("/login/")
def login():
    return render_template("home/login.html")
