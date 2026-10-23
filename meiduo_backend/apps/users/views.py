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
            "username": request.user.username, #request.user 就是已经登陆的用户信息
            "email": request.user.email,
            "mobile": request.user.mobile,
            "email_active": request.user.email_active,
        }
        return JsonResponse({'code':0,'errmsg':'ok',"info_data":info_data})



