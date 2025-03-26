from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from os import path
from flask_login import LoginManager
from datetime import datetime
from base64 import b64encode
import base64
from io import BytesIO

db = SQLAlchemy()
DB_NAME = "database.db"
UPLOAD_FOLDER = '/home/helpusfly/mysite/website/static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
STATIC_ROOT = '/home/helpusfly/mysite/website/static'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "blogapp"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app)

    from .views import views
    app.register_blueprint(views, url_prefix="/")
    from .auth import auth
    app.register_blueprint(auth, url_prefix="/")
    from .models import User, Post, Comment
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.signin"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Database Created")
