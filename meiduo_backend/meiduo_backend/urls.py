"""
URL configuration for meiduo_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from django.http import HttpResponse

from django.urls import register_converter,include
from utils.converters import UsernameConverter,MobileConverter

# 定义一个包含 (类, 别名) 的注册蓝图列表
CUSTOM_CONVERTERS = [
    (UsernameConverter, 'username'),
    (MobileConverter, 'mobile'),
]

# 循环批量注册
for converter_class, alias in CUSTOM_CONVERTERS:
    register_converter(converter_class, alias)

register_converter(UsernameConverter, 'username')

def log(request):
       # 1.导入
       import logging
       # 2. 创建日志器
       logger = logging.getLogger("django")
       # 3. 调试日志器的方法保存日志
       logger.info("用户登陆了")
       logger.warning("redis缓存不足")
       logger.error("该记录不存在")
       logger.debug("~~~~~~~")
       return HttpResponse("Hello world")

urlpatterns = [
       path("admin/", admin.site.urls),
       path("log/", log),
       path("", include("apps.users.urls")),
       path("", include("apps.verifications.urls")),
       path("",include("apps.OAuth.urls")),
       path("",include("apps.area.urls")),
       path("",include("apps.goods.urls")),

]
