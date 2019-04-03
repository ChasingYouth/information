
# 导入数据库扩展，添加配置信息
from flask import session
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from infor import creat_app, db
# 创建数据库实例
app = creat_app('development')
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    session['nam'] = 'maoweiwei'

    return 'index'


if __name__ == '__main__':
    manager.run()
