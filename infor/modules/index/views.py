from infor import constants
from infor.utils.common import user_login_data

from . import index_blu
from flask import render_template, current_app, session, g

# from infor import db


@index_blu.route('/', methods=['GET', 'POST'])
@user_login_data
def index():
    # user_id = session.get('user_id')
    # user = None
    # if user_id:
    #     try:
    #         from infor.models import User
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    try:
        from infor.models import News
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)
    click_news_list = []
    for news in news_list:
        click_news_list.append(news.to_dict())
    from infor.models import Category
    categories = Category.query.all()
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())
    data = {'user_info': g.user.to_dict() if g.user else None,
            'click_news_list': click_news_list,
            'category_list': category_list
            }

    return render_template('news/index.html', data=data)
    # return render_template('news/index.html')


@index_blu.route('/favicon.ico')
def web_log():
    return current_app.send_static_file('news/favicon.ico')

