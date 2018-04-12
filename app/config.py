import os

# secret_key
SECRET_KEY = '19950927'

CSRF_ENABLED = True

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")  # 上传文件路径
FACE_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")  # 头像路径
PRODUCT_FOlDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/products")
