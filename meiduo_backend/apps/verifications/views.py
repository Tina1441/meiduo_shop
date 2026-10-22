from django.http import HttpResponse, JsonResponse
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
        redis_cli.setex(uuid,timedelta(seconds=120),text)
        # 4. ??????????????????
        return HttpResponse(image,content_type='image/jpeg')


# 1. 接受请求 获取请求参数： 手机号 图片验证码 uuid
# 2. 验证图片验证码
# 3. 生成短信验证码
# 4. 保存短信验证码
# 5. 发送短信验证码
# 6. 返回响应
class SendMessageView(View):
    def get(self,request,mobile):
        uuid = request.GET.get("image_code_id")
        image_code = request.GET.get("image_code")

        if not all([uuid,image_code]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})

        redis_cli = get_redis_connection('code')
        redis_image_code = redis_cli.get(uuid)
        if not redis_image_code:
            return JsonResponse({'code':400,'errmsg':'图片验证码已过期'})
        if redis_image_code.decode() != image_code:
            return JsonResponse({'code':400,'errmsg':'图片验证码错误'})

        redis_send_flag = redis_cli.get('send_flag_%s'%mobile)
        if redis_send_flag:
            return JsonResponse({'code':400,'errmsg':'不要频繁发送短信'})

        from random import randint
        sms_code = '%04d'%randint(0,9999)

        pipeline = redis_cli.pipeline()

        pipeline.setex(mobile,timedelta(seconds=300),sms_code)

        pipeline.setex('send_flag_%s'%mobile,timedelta(seconds=480),1)

        pipeline.execute()

        # from libs.yuntongxun.sms import CCP
        # CCP().send_template_sms(mobile,[sms_code,'5'],1)

        from celery_tasks.sms.tasks import celery_send_sms
        celery_send_sms.delay(mobile,sms_code)

        return JsonResponse({'code':0,'errmsg':'ok'})


