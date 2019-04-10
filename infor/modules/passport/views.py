import datetime
import random

from flask import session

from infor import db
from infor.libs.yuntongxun.sms import CCP
from infor.models import User
from . import passport_blu
from flask import request, make_response, current_app, jsonify
from infor.utils.captcha.captcha import captcha
from infor import redis_store, constants
from infor.utils.response_code import RET
import re


@passport_blu.route('/image_code')
def get_image_code():
    """
     1.获取参数
     2.调用方法生成验证码及图片
     3.保存到redis中
     4.返回响应
    """
    code_id = request.args.get('code_id')
    pre_id = request.args.get('pre_id')
    name, text, image = captcha.generate_captcha()
    try:
        redis_store.set('ImageCode_' + code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        if pre_id:
            redis_store.delete('ImageCode:' + pre_id)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))

    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response


@passport_blu.route('/login', methods=['POST'])
def login():
# 获取参数
    dict_data = request.json
    mobile = dict_data.get('mobile')
    password = dict_data.get('password')
    if not all([mobile, password]):
        return jsonify(error=RET.PARAMERR, errmsg='参数不缺哦')
    if not re.match('1[3456789]\\d{9}', mobile):
        return jsonify(error=RET.PARAMERR, errmsg='手机号码可是不对哦！！')
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='查询失败了！！！')
    if not user:
        return jsonify(error=RET.PARAMERR, errmsg='没有这个用户SB！！！！')
    if not user.check_passowrd(password):
        return jsonify(error=RET.PARAMERR, errmsg='密码错了SB！！')
    user.last_login = datetime.datetime.now()
    return jsonify(error=RET.OK, errmsg="OK")
# 校验参数
# 校验短信校验密码
# 保存用户登录状态
# 返回结果

@passport_blu.route('/register', methods=['POST'])
def register():
#  获取参数
    dict_date = request.json
    mobile = dict_date.get('mobile')
    sms_code = dict_date.get('sms_code')
    password = dict_date.get('password')
# 校验参数
    if not all([mobile, sms_code, password]):
        return jsonify(error=RET.PARAMERR, errmsg='注册参数不全')
    try:
        redis_sms_code = redis_store.get('SMS'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='获取手机号码失败了')
    if not redis_sms_code:
        return jsonify(error=RET.NODATA, errmsg='短信验证码过期了')
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = password
    user.last_login = datetime.datetime.now()
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='保存异常')
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    return jsonify(error=RET.OK, errmsg="注册成功了！！！")
# 获取redis中短信验证码
# 判断是否过期
# 判断短信验证码是否正确
# 创建用户对象，
# 保存到数据库中
# 返回注册前端页面


@passport_blu.route('/smscode', methods=['POST'])
def smscode():
    """
    1.接受提交的参数
    2.校验手机号码
    3.根据传入的图片验证码去redis中取验证码内容
    4.进行验证码比对
    5.生成短信验证码内容并且发送
    6.保存短信验证码到redis中
    7.返回发送成功的响应
    """
    param_dict = request.json
    mobile = param_dict.get("mobile")
    image_code = param_dict.get("image_code")
    image_code_id = param_dict.get("image_code_id")
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全啊，sb！')
# 校验手机号码
    if not re.match('^1[3578][0-9]{9}$', mobile):
        return jsonify(error=RET.PARAMERR, errmsg='你输入的手机号码格式不对啊！！！')
    try:
        real_image_code = redis_store.get('ImageCode_'+image_code_id)
        if not real_image_code:
            return jsonify(errno=RET.NODATA, errmsg='验证码过期了！！')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg='验证码找不到数据')
    if image_code.lower() != real_image_code.decode().lower():
        # 验证码输入错误
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误A！！！")
    sms_code = "%06d" % random.randint(0, 999999)
    # result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], '1')
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg='短信验证码发送失败！！！！！！')
    current_app.logger.debug('短信验证码是：%s' %sms_code)
    try:
        redis_store.set('SMS'+mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存短信验证码失败了！')
    return jsonify(errno=RET.OK, errmsg='发送成功了！！！！！！！！！！！！！！！！')


