
# 导入数据库扩展，添加配置信息
from flask import session
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from infor import creat_app, db, models
# 创建数据库实例
app = creat_app('production')
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)
if __name__ == '__main__':
    manager.run()
