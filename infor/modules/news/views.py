from infor.models import News
from infor.utils.common import user_login_data
from infor.utils.response_code import RET
from . import news_blu
from flask import request, current_app, jsonify, render_template, g, session


@news_blu.route('/newslist')
def newslist():
    """
        获取指定分类的新闻列表
        1. 获取参数
        2. 校验参数
        3. 查询数据
        4. 返回数据
        :return:
    """
    cid = request.args.get('cid', 1)
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
        per_page = 10
    filters = []
    if cid != '1':
        # 这里在python中，列表不仅可以保存字符串，还可以保存对象，以及属性等。此处保存的就是News对象的操作或称属性
        filters.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
        totalPage = paginate.pages
        currentPage = paginate.page
        items = paginate.items
    except Exception as e:
        current_app.logger.error(e)
    newsList=[]
    for news in items:
        newsList.append(news.to_dict())
    return jsonify(error=RET.OK, errmsg='成功', cid=cid, totalPage=totalPage, currentPage=currentPage, newsList=newsList)


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    data = {'user_info': g.user.to_dict() if g.user else None}
    return render_template('news/detail.html', data=data)


@news_blu.route('/passport/logout', methods=['POST'])
def logout():
    session.pop('user_id')
    session.pop('nick_name')
    session.pop('mobile')
    return jsonify(error=RET.OK, errmsg='OK!')
