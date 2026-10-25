"""
登陆后将cookie数据传到redis

cookie :
{
    sku_id: {'count':xxx,'selected':xxx}
    ...
}

redis
{sku_is:count ...}
(sku_id ...)

1.cookies中有 redis没有 添加
2.redis有 cookie没有 不变
3.redis有 cookie有 以cookie为准


1. 获取cookie 解密
2. 初始化一个字典 已选择列表 未选择列表
3. 连接redis
4. 加入数据
5. 删除cookie
6. 返回response

"""
import base64
import pickle

from django.http import JsonResponse
from django_redis import get_redis_connection

def merge_cookie_to_redis(request,response):
    cookie_cart = request.COOKIES.get('carts')
    user = request.user

    if cookie_cart:
        carts = pickle.loads(base64.b64decode(cookie_cart))

        sku_id_count = {}
        selected_sku_id = []
        unselected_sku_id = []

        for sku_id,count_selected in carts.items():
            sku_id_count[sku_id] = count_selected['count']
            if count_selected['selected']:
                selected_sku_id.append(sku_id)
            else:
                unselected_sku_id.append(sku_id)

        redis_cli = get_redis_connection('carts')
        pipeline = redis_cli.pipeline()

        pipeline.hmset('carts_%s' % user.id, sku_id_count)
        if len(selected_sku_id) > 0:
            # *selected_ids  对列表数据进行解包
            pipeline.sadd('selected_%s' % user.id, *selected_sku_id)
        # unselected_id [4,5,6]
        if len(unselected_sku_id) > 0:
            pipeline.srem('selected_%s' % user.id, *unselected_sku_id)
        pipeline.execute()

        response = JsonResponse({'code':0,'errmsg':'ok'})

        response.delete_cookie('carts')

    return response





