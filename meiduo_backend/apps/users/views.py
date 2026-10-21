from django.http import JsonResponse
from django.shortcuts import render
import json
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
        # 1.接收数据
        body = request.body
        body_str = body.decode('utf-8')
        body_dict = json.loads(body_str)

        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        sms_code = body_dict.get('sms_code')
        allow = body_dict.get('allow')
        # 2.验证数据
        if not all([username, password, password2, mobile, sms_code, allow]):
            return JsonResponse({'code':0,'errmsg':'注册信息不全'})
        user_count = User.objects.filter(mobile=mobile).count()
        mobile_count = User.objects.filter(mobile=mobile).count()

        if user_count:
            return JsonResponse({'code':0,'errmsg':'用户名已存在，请重新输入'})
        if mobile_count:
            return JsonResponse({'code':0,'errmsg':'该手机号已存在，请重新输入'})
        if password != password2:
            return JsonResponse({'code':0,'errmsg':'两次输入的密码不一致，请重新输入'})

        # 3.数据入库
        user = User.objects.create_user(username=username, password=password, mobile=mobile)


        # 4.返回响应
        return JsonResponse({'code': 0, 'errmsg': '注册成功'})

