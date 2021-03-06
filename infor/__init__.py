from logging.handlers import RotatingFileHandler
import redis, logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_session import Session  # 导入Session 保存session
from config import config
from flask_sqlalchemy import SQLAlchemy
from infor.modules.index import index_blu
from flask_wtf.csrf import generate_csrf

from infor.utils.common import do_index_class

redis_store = None

db = SQLAlchemy()

def setup_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def creat_app(config_name):
    app = Flask(__name__)
    app.add_template_filter(do_index_class, 'index_class')

    app.config.from_object(config[config_name])
    db.init_app(app)
    global redis_store
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    CSRFProtect(app)  # 开启对应用程序的保护，CSRFProtect只做验证工作，cookie中的 csrf_token 和表单中的 csrf_token 需要我们自己实现
    Session(app)
    setup_log(config_name)
    app.register_blueprint(index_blu)
# 注册蓝图
    from infor.modules.passport import passport_blu
    app.register_blueprint(passport_blu)
    from infor.modules.news import news_blu
    app.register_blueprint(news_blu)

    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie('csrf_token', csrf_token)
        return response
    return app



