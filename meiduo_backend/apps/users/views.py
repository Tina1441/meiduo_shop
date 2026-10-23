from django.http import JsonResponse
from django.shortcuts import render
import json
from datetime import timedelta
import re
from django.contrib.auth import logout
# Create your views here.

'''
    1. 判断用户名是否重复的功能
        前端 后端
    后（思路）：
        请求  : 接收用户名
        业务逻辑  ：
            根据用户名查询数据库，如果查询结果数量等于0，说明没有注册
            如果查询数量等于1，说明有注册
        响应  ： JSON
        {code:0,count:0/1,errmsg:ok}
        路由 ： GET usernames/(?<username>/count/)
        步骤：
        1. 接收用户名
        2. 根据用户名查询数据库
        3. 返回响应
    前：当用户输入用户名后 失去焦点发送一个 axios 请求

'''

from django.views import View
from apps.users.models import User
class UsernameCountView(View):

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})

class MobileView(View):
    # / mobiles / ' + this.mobile + ' / count /
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})

class RegisterView(View):
    def post(self, request):
        print("========== 进入 RegisterView ==========", flush=True)

        body_dict = json.loads(request.body.decode('utf-8'))

        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        sms_code = body_dict.get('sms_code')
        allow = body_dict.get('allow')

        # 2.验证数据
        if not all([username, password, password2, mobile, sms_code, allow]):
            return JsonResponse({'code': 0, 'errmsg': '注册信息不全'})
        user_count = User.objects.filter(mobile=mobile).count()
        mobile_count = User.objects.filter(mobile=mobile).count()

        if user_count:
            return JsonResponse({'code': 0, 'errmsg': '用户名已存在，请重新输入'})
        if mobile_count:
            return JsonResponse({'code': 0, 'errmsg': '该手机号已存在，请重新输入'})
        if password != password2:
            return JsonResponse({'code': 0, 'errmsg': '两次输入的密码不一致，请重新输入'})
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        redis_message_code = redis_cli.get(mobile)
        if not redis_message_code:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码失效'})
        if redis_message_code.decode() != sms_code:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码不正确'})

        user = User.objects.create_user(
            username=username,
            password=password,
            mobile=mobile
        )

        print("========== 用户创建成功 ==========", flush=True)

        from django.contrib.auth import login
        login(request, user)

        print("========== login 执行完成 ==========", flush=True)
        print("session_key:", request.session.session_key, flush=True)
        print("user_id:", request.session.get('_auth_user_id'), flush=True)

        return JsonResponse({
            'code': 0,
            'errmsg': '注册成功'
        })


# 1. 接收参数
# 2. 验证参数
# 3. 验证用户和密码是否正确
# 4. session
# 5. 判断是否记住登录
# 6. 返回响应


class LoginView(View):
    def post(self,request):
       data = json.loads(request.body.decode())
       username = data.get('username')
       password = data.get('password')
       remembered = data.get('remembered') # 记住登录（十天内免登录）

       if not all([username,password]):
           return JsonResponse({'code':400,'errmsg':'参数不全'})

       from django.contrib.auth import authenticate,login

    # 修改 USERNAME_FIELD 字段来修改authenticate查询
       if re.match("1[3-9]\d{9}",username):
           User.USERNAME_FIELD = "mobile"
       else:
           User.USERNAME_FIELD = "username"


       user = authenticate(username=username, password=password)
       if not user:
           return JsonResponse({'code':400,'errmsg':'账号或密码错误'})

       login(request, user)

       if remembered:
           # 记住登录（2周）默认
           request.session.set_expiry(timedelta(days=7))

       else:
           # 不记住登录
           request.session.set_expiry(0)  # 浏览器关闭过期

       response = JsonResponse({'code':0,'errmsg':'ok'})
       # 为了首页显示用户信息
       response.set_cookie('username',username,max_age=timedelta(days=7))


       return response

class LogOutView(View):
    def delete(self,request):
        # 删除sessionID信息
        logout(request)
        response = JsonResponse({'code':0,'errmsg':'ok'})
        # 删除Cookie中的username信息 前端展示
        response.delete_cookie('username')

        return response

from utils.views import LoginRequiredJSONMixin
class CenterView(LoginRequiredJSONMixin, View):
    def get(self,request):
        info_data = {
            "username": request.user.username, #request.user  来源于中间件 就是已经登陆的用户信息 不是登录用户 则是匿名用户
            "email": request.user.email,
            "mobile": request.user.mobile,
            "email_active": request.user.email_active,
        }
        return JsonResponse({'code':0,'errmsg':'ok',"info_data":info_data})


'''
1. 保存邮箱地址 2. 发送激活邮件 3.用户激活邮件
'''

class EmailView(LoginRequiredJSONMixin,View):
    def put(self,request):
        # 获取邮箱
        data = json.loads(request.body.decode())
        email = data.get('email')
        # 验证邮箱
        if not re.match("^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$",email):
            return JsonResponse({'code':400,'errmsg':'邮箱格式不正确'})
        # 保存邮箱
        user = request.user
        user.email = email
        user.save()
        # 发送激活邮件
        from django.core.mail import send_mail
        subject = "美多商城激活邮件"
        # 1. 准备纯文本正文（给不支持HTML的邮箱看）
        message = "尊敬的用户，请点击以下链接激活账号：http://www.itcast.cn"
        # 2. 准备 HTML 格式正文
        from apps.users.utils import generic_email_verify_token
        token = generic_email_verify_token(request.user.id)
        # 生成加密数据
        html_message = "点击按钮进行激活 <a href='http://www.itcast.cn/?token=%s'>激活</a>"%token
        from_email = "美多商城<mimwawilee@163.com>"
        recipient_list = ["mimwawilee@163.com"]

        send_mail(
            subject=subject,
            message=message,  # 必须有普通的 message
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message  # html_message 作为关键字参数传入
        )

        # 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})


"""
django 项目
1. django的基础 夯实
2. 需求分析
3. 学习新知识
4. 掌握分析问题，解决问题的能力（debug）
"""

"""

1. 设置邮件服务器

    我们设置 163邮箱服务器
    相当于 我们开启了 让163帮助我们发送邮件。同时设置了 一些信息（特别是授权码）

2.  设置邮件发送的配置信息
    #  让django的哪个类来发送邮件
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # 邮件服务器的主机和端口号
    EMAIL_HOST = 'smtp.163.com'
    EMAIL_PORT = 25

    # 使用我的 163服务器 和 授权码
    #发送邮件的邮箱
    EMAIL_HOST_USER = 'qi_rui_hua@163.com'
    #在邮箱中设置的客户端授权密码
    EMAIL_HOST_PASSWORD = '123456abc'

3. 调用  send_mail 方法
"""







