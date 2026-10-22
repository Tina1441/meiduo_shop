from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from datetime import timedelta

# Create your views here.
class ImageCodeView(View):
    def get(self,request,uuid):
        # 1. ????uuid
        # 2. ????????? ?? ????????
        text,image = captcha.generate_captcha()
        # 3?? ????redis
        redis_cli = get_redis_connection('code')
        redis_cli.set(uuid,text,timedelta(seconds=120),)
        # 4. ??????????????????
        return HttpResponse(image,content_type='image/jpeg')
