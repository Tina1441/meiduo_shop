from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.area.models import Area
import json

# Create your views here.
class AreaView(View):
    def get(self,request):
        provinces = Area.objects.filter(parent__isnull=True)
        province_list = []
        for province in provinces:
            province_list.append({
                'id': province.id,
                'name': province.name
            })
        return JsonResponse({"code":0,"errmsg":"ok","province_list":province_list})

class SubAreaView(View):
    def get(self,request,id):
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
        return JsonResponse({"code": 0, "errmsg": "ok", "sub_data": {"subs": data_list}})