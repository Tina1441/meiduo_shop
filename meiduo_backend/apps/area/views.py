from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.area.models import Area
from django.core.cache import cache
import json

# Create your views here.
class AreaView(View):
    def get(self,request):
        # 查询缓存数据
        province_list = cache.get('provinces')
        if not province_list:
            provinces = Area.objects.filter(parent__isnull=True)
            province_list = []
            for province in provinces:
                province_list.append({
                    'id': province.id,
                    'name': province.name
                })
            # 保存缓存数据
            cache.set('provinces', province_list, 24*3600)

        return JsonResponse({"code":0,"errmsg":"ok","province_list":province_list})

class SubAreaView(View):
    def get(self,request,id):
        data_list = cache.get(f'up_level:{id}')
        if not data_list:
            try:
                up_level = Area.objects.get(id=id)
            except Exception as e:
                return JsonResponse({"code":400,"errmsg":"输入错误"})
            down_level = up_level.subs.all()
            data_list = []
            for item in down_level:
                data_list.append({
                    'id': item.id,
                    'name': item.name
                })

            # 保存缓存数据
            cache.set(f'up_level:{id}', data_list, 24*3600)
        return JsonResponse({"code": 0, "errmsg": "ok", "sub_data": {"subs": data_list}})