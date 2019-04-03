from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from flask_session import Session  # 导入Session 保存session
from config import config
from flask_sqlalchemy import SQLAlchemy
import redis


db = SQLAlchemy()


def creat_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    global redis_store
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    CSRFProtect(app)  # 开启对应用程序的保护，CSRFProtect只做验证工作，cookie中的 csrf_token 和表单中的 csrf_token 需要我们自己实现
    Session(app)
    return app
