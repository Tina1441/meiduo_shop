import base64

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from eventlet.patcher import original

# Create your views here.

"""
添加：
user_id sku_id count selectd
未登录用户 保存在cookie
                cookie:
                    {
                        sku_id: {count:xxx,selected:xxxx},
                        sku_id: {count:xxx,selected:xxxx},
                        sku_id: {count:xxx,selected:xxxx},
                    }
登录用户 保存在redis  
        hset
        usr_id: {
            sku_id:count
        }
        list: selected
        
        优化
        usr_id: {
            sku_id:count/-count(未选择)
        }
        
"""
"""
查看
user_id sku_id count selectd
未登录用户 保存在cookie
                cookie:
                    {
                        sku_id: {count:xxx,selected:xxxx},
                        sku_id: {count:xxx,selected:xxxx},
                        sku_id: {count:xxx,selected:xxxx},
                    }
                1.. 查询cookie中的数据
                        base64.decode()
                        pickle.loads()
                2.. 返回响应
登录用户 保存在redis  
        hset
        usr_id: {
            sku_id:count
        }
        list: selected

        优化
        usr_id: {
            sku_id:count/-count(未选择)
        }
                
                1. 获取参数 user_id
                2. 根据user_id查询redis中的数据
                3. redis.decode
                4. 返回响应

"""
import json
from apps.goods.models import SKU
from django_redis import get_redis_connection
import pickle
class CartsView(View):
    def post(self, request):
        # 1. 接收数据
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected')
        # 2. 验证参数
        try:
            sku  = SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'code':400, 'errmsg':'查无此商品'})
        # 类型强制转换
        try:
            count = int(count)
        except Exception:
            count = 1
        # 3. 判断用户登陆状态
        user = request.user
        # 用户存在
        if user.is_authenticated:
            # 3.1 连接redis
            redis_cli = get_redis_connection('carts')
            # 3.2 操作hash
            # redis_cli.hset(key,field,value)
            # 直接让 Redis 帮你在原数量上做累加，连查询的步骤都省了！
            redis_cli.hincrby('carts_%s' % user.id, sku_id, count)
            # 3.3 操作set
            # 默认就是选中
            redis_cli.sadd('selected_%s' % user.id, sku_id)
            # 4. 返回响应
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 用户不存在
        else:
            # 3.1 查询 cookie 是否存在 carts
            cookie_carts = request.COOKIES.get('carts')
            # 3.1.1 存在则解密
            if cookie_carts:
                try:
                    carts = pickle.loads(base64.b64decode(cookie_carts))
                except Exception:
                    carts = {}
            else:
                carts = {}

            # --- 核心修复：先定义默认值 ---
            current_selected = True  # 默认新加入的商品是选中状态

            # 1. 如果 sku_id 已经在字典里
            if sku_id in carts:
                # 购物车中 已经有该商品id
                # 数量累加
                ## {16： {count:3,selected:True}}
                origin_count=carts[sku_id]['count']
                count+=origin_count

            #     carts[sku_id] = {
            #         'count':count,
            #         'selected':True
            #     }
            # else:
            # 购物车中 没有该商品id
            # {16： {count:3,selected:True}}
            carts[sku_id]={
                'count':count,
                'selected':True
            }


            # 加密
            carts_bytes = pickle.dumps(carts)
            base64encode = base64.b64encode(carts_bytes)

            # 设置cookie
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})

            # 返回响应
            response.set_cookie('carts', base64encode.decode(), max_age=3600 * 24 * 12)

            return response

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            sku_id_count = redis_cli.hgetall('carts_%s' % user.id)
            selected_ids = redis_cli.smembers('selected_%s' % user.id)

            carts = {}

            for sku_id,count in sku_id_count.items():
                sku_iddecode = int(sku_id.decode())
                carts[sku_iddecode] = {
                    'count': int(count),
                    'selected': sku_id in selected_ids
                }
        else:
            carts_cookie = request.COOKIES.get('carts')
            if carts_cookie:
                carts = pickle.loads(base64.b64decode(carts_cookie))
            else:
                carts = {}

        sku_ids = carts.keys()

        skus = SKU.objects.filter(id__in=sku_ids)

        sku_list = []

        for sku in skus:
            sku_list.append({
                'id': sku.id,
                'price': sku.price,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'selected': carts[sku.id]['selected'],  # 选中状态
                'count': int(carts[sku.id]['count']),  # 数量 强制转换一下
                'amount': sku.price * carts[sku.id]['count']  # 总价格
            })

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus': sku_list})

    def put(self, request):
        # 1. 获取参数
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected')
        if not all([sku_id, count]):
            return JsonResponse({'code':400, 'errmsg':'参数不全'})
        # 2. 验证参数
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400, 'errmsg':'商品不存在'})
        try:
            count = int(count)
        except Exception:
            count = 1
        # 3. 验证用户是否登录
        if request.user.is_authenticated:
            user_id = request.user.id
            redis_cli = get_redis_connection('carts')
            redis_cli.hset('carts_%s' % user_id, sku_id, count)
            if selected:
                redis_cli.sadd('selected_%s' % user_id, sku_id)
            else:
                redis_cli.srem('selected_%s' % user_id, sku_id)

            return JsonResponse({'code':0,'errmsg':'ok','cart_sku':{'count':count,'selected':selected}})

        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                carts = {}
            if sku_id in carts:
                carts[sku_id] = {
                    'count': count,
                    'selected': selected
                }

            new_carts = base64.b64encode(pickle.dumps(carts))

            response = JsonResponse({'code':0,'errmsg':'ok','cart_sku':{'count':count,'selected':selected}})

            response.set_cookie('carts', new_carts.decode(), max_age=3600 * 24 * 12)

            return response

    def delete(self, request):
        data = json.loads(request.body.decode())

        sku_id = data.get('sku_id')
        if not sku_id:
            return JsonResponse({'code':400, 'errmsg':'参数不全'})
        try:
            sku = SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'code':400, 'errmsg':'商品不存在'})
        if request.user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            redis_cli.hdel('carts_%s' % request.user.id, sku_id)
            redis_cli.srem('selected_%s' % request.user.id, sku_id)
            return JsonResponse({'code':0,'errmsg':'ok'})
        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                carts = pickle.loads(base64.b64decode(cookie_carts))
                del carts[sku_id]
            else:
                carts = {}
            # 删掉之后要重新修改cookie
            new_carts = base64.b64encode(pickle.dumps(carts))
            response = JsonResponse({'code':0,'errmsg':'ok'})
            response.set_cookie('carts', new_carts.decode(), max_age=3600 * 24 * 12)
            return response

class CartsAllSelect(View):
    def put(self, request):
        data = json.loads(request.body.decode())
        selected = data.get('selected')
        if request.user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            if selected is False:
                redis_cli.delete('selected_%s' % request.user.id)
            else:
                sku_id_count = redis_cli.hgetall('carts_%s' % request.user.id)
                sku_ids = sku_id_count.keys()
                for sku_id in sku_ids:
                    redis_cli.sadd('selected_%s' % request.user.id, sku_id.decode())
            return JsonResponse({'code': 0, 'errmsg': 'ok'})

        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                carts = pickle.loads(base64.b64decode(cookie_carts))
            else:
                carts = {}
            for sku,count in carts.items():
                carts[sku]['selected'] = selected
            new_carts = base64.b64encode(pickle.dumps(carts))
            response = JsonResponse({'code':0,'errmsg':'ok'})
            response.set_cookie('carts', new_carts.decode(), max_age=3600 * 24 * 12)
            return response




