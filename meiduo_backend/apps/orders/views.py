from django.shortcuts import render
from django.views import View

from apps.goods.models import SKU
from utils.views import LoginRequiredJSONMixin
from apps.users.models import Address
from django_redis import get_redis_connection
from django.http import JsonResponse
# Create your views here.


class OrderSettlementView(LoginRequiredJSONMixin,View):
    def get(self, request):
        user = request.user

        # 地址信息
        address = Address.objects.filter(user=user, is_deleted=False)
        addresses = []
        for item in address:
            addresses.append({
                'id': item.id,
                'province': item.province.name,
                'city': item.city.name,
                'district': item.district.name,
                'place': item.place,
                'receiver': item.receiver,
                'mobile': item.mobile
            })
        # 商品信息
        redis = get_redis_connection("carts")
        pipeline = redis.pipeline()

        pipeline.hgetall("carts_%s" % user.id)
        pipeline.smembers("selected_%s"%user.id)
        result = pipeline.execute()

        sku_id_count = result[0]
        selected_sku = result[1]

        selected_carts={}
        for sku_id in selected_sku:
            selected_carts[int(sku_id)]=int(sku_id_count[sku_id])

        skus = []
        for sku_id,count in selected_carts.items():
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': count,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })

        from decimal import Decimal
        freight=Decimal('10')

        context = {
            'skus': skus,
            'addresses': addresses,
            'freight': freight
        }

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': context})




