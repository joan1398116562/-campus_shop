from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime


# 实例化app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:177036@127.0.0.1:3306/shop"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)


class User(db.Model):
    """会员数据模型"""
    __tablename__ = "user"
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 昵称
    name = db.Column(db.String(100), unique=True)
    # 密码字段
    pwd = db.Column(db.String(100))
    # 邮箱
    email = db.Column(db.String(100), unique=True)
    # 手机
    phone = db.Column(db.String(11), unique=True)
    # 银行卡
    card = db.Column(db.String(255), unique=True)
    # 头像
    face = db.Column(db.String(255))
    # 收货地址
    address = db.Column(db.String(255))
    # 添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # 用户评论外键关系关联
    comments = db.relationship('Comment', backref='user')

    def __repr__(self):
        return "<User %r>" % self.name


class Product(db.Model):
    """商品数据模型"""
    __tablename__ = "product"
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 名称
    name = db.Column(db.Integer, unique=True)
    # 价格
    price = db.Column(db.Float)
    # 图片
    pic = db.Column(db.String(255), unique=True)

    # 商品所属分类
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    # 商品评论外键关系关联
    comments = db.relationship("Comment", backref='product')

    def __repr__(self):
        return "<Product %r>" % self.name


class Tag(db.Model):
    """商品属性分类"""
    __tablename__ = "tag"
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 标题
    name = db.Column(db.String(100), unique=True)
    # 添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # 商品外键关系关联
    products = db.relationship("Product", backref='tag')

    def __repr__(self):
        return "<Tag %r>" % self.name


class Comment(db.Model):
    """评论"""
    __tablename__ = "comment"
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 评论内容
    content = db.Column(db.Text)
    # 所属商品
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    # 所属用户
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "<Comment %r>" % self.id





