import json
from decimal import Decimal
from time import strftime

from celery.worker.state import total_count
from django.shortcuts import render
from django.views import View

from apps.goods.models import SKU
from utils.views import LoginRequiredJSONMixin
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

        # 货币类型 decimal
        from decimal import Decimal
        freight=Decimal('10')

        context = {
            'skus': skus,
            'addresses': addresses,
            'freight': freight
        }

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': context})
###########提交订单##########
"""
1. 接收参数
 address_id pay_method
2. 验证参数
user_id,address_id,sku_id_count,selected_sku
3. 数据入库
订单基本信息表 订单商品表
4. 返回响应
"""
from apps.users.models import Address
from apps.orders.models import OrderInfo,OrderGoods
from django.db import transaction,connections,connection
from django.utils import timezone


"""
在 MySQL 中，TRUNCATE 和其他 DDL 操作无法回滚，因为它们会触发隐式提交，结束当前事务。
DML 与 DDL 的本质区别
DML（数据操作语言）：如 INSERT、UPDATE、DELETE，操作的是表中的数据。DML 操作会记录 undo log，因此在事务未提交前可以通过 ROLLBACK 回滚数据。
DDL（数据定义语言）：如 CREATE、ALTER、DROP、TRUNCATE，操作的是表结构、索引或数据库对象。DDL 执行时会隐式提交当前事务，即在执行前自动提交未完成的事务，
并在执行后开启新事务，因此无法回滚 
。

"""
class OrderCommitView(LoginRequiredJSONMixin,View):

    def post(self,request):
        user=request.user
        # 一。接收请求     user,address_id,pay_method
        data=json.loads(request.body.decode())
        address_id=data.get('address_id')
        pay_method=data.get('pay_method')

        # 二。验证数据
        if not all([address_id,pay_method]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})

        try:
            address=Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'参数不正确'})

        # if pay_method not in [1,2]:   这么写是没有问题的。
        # 从代码的可读性来说很差。 我都不知道 1 什么意思 2 什么意思

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code': 400, 'errmsg': '参数不正确'})
        # order_id 主键（自己生成）   年月日时分秒 + 用户id（9位数字）
        from django.utils import timezone
        from datetime import datetime
        # datetime.strftime()
        # Year
        # month
        # day
        # Hour
        # Minute
        # Second
        # %f 微秒
        # timezone.localtime() 2020-10-19 10:03:10
        order_id=timezone.localtime().strftime('%Y%m%d%H%M%S%f') + '%09d'%user.id

        # 支付状态由支付方式决定
        # 代码是对的。可读性差
        # if pay_method == 1: # 货到付款
        #     pay_status=2
        # else:
        #     pay_status=1

        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status=OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        # 总数量，总金额， = 0
        total_count=0
        from decimal import Decimal
        total_amount=Decimal('0')        #总金额
        # 运费
        freight=Decimal('10.00')

        with transaction.atomic():

            # 事务开始点
            point = transaction.savepoint()

            # 三。数据入库     生成订单（订单基本信息表和订单商品信息表）
            #     1.先保存订单基本信息
            orderinfo=OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=total_count,
                total_amount=total_amount,
                freight=freight,
                pay_method=pay_method,
                status=status
            )
            #     2 再保存订单商品信息
            #       2.1 连接redis
            redis_cli=get_redis_connection('carts')
            #       2.2 获取hash
            sku_id_counts=redis_cli.hgetall('carts_%s'%user.id)
            #       2.3 获取set
            selected_ids=redis_cli.smembers('selected_%s'%user.id)
            #       2.4 遍历选中商品的id，
            carts={}
            #         最好重写组织一个数据，这个数据是选中的商品信息
            #         {sku_id:count,sku_id:count}
            for sku_id in selected_ids:
                carts[int(sku_id)]=int(sku_id_counts[sku_id])

            ##         {sku_id:count,sku_id:count}
            #       2.5 遍历
            for sku_id,count in carts.items():

                # for i in range(10):
                while True:
                    # 根据选中商品的id进行查询
                    sku=SKU.objects.get(id=sku_id)
                    #       2.6 判断库存是否充足
                    if sku.stock<count:

                        #回滚点
                        transaction.savepoint_rollback(point)

                        #       2.7 如果不充足，下单失败
                        return JsonResponse({'code':400,'errmsg':'库存不足'})

                    from time import sleep
                    sleep(3)
                    #       2.8 如果充足，则库存减少，销量增加
                    # sku.stock -= count
                    # sku.sales += count
                    # sku.save()  #记得保存

                    # 1. 先记录某一个数据    记录哪个数据都可以
                    #旧库存  我们参照这个记录
                    old_stock=sku.stock

                    # 2. 我更新的时候，再比对一下这个记录对不对
                    new_stock=sku.stock-count
                    new_sales=sku.sales+count

                    result=SKU.objects.filter(id=sku_id,stock=old_stock).update(stock=new_stock,sales=new_sales)
                    # result = 1 表示 有1条记录修改成功
                    # result = 0 表示 没有更新

                    if result == 0:
                        # sleep(0.005)
                        continue
                        # 暂时回滚和返回下单失败
                        # transaction.savepoint_rollback(point)
                        # return JsonResponse({'code':400,'errmsg':'下单失败~~~~~~~'})

                    #       2.9 累加总数量和总金额
                    orderinfo.total_count+=count
                    orderinfo.total_amount+=(count*sku.price)

                    #       2.10 保存订单商品信息
                    OrderGoods.objects.create(
                        order=orderinfo,
                        sku=sku,
                        count=count,
                        price=sku.price
                    )
                    break
            #   3.更新订单的总金额和总数量
            orderinfo.save()
            # 提交点
            transaction.savepoint_commit(point)

        #   4.将redis中选中的商品信息移除出去 （暂缓）
        # 四。返回响应
        return JsonResponse({'code':0,'errmsg':'ok','order_id':order_id})


"""
解决并发的超卖问题：
① 队列
② 锁
    悲观锁： 当查询某条记录时，即让数据库为该记录加锁，锁住记录后别人无法操作

            悲观锁类似于我们在多线程资源竞争时添加的互斥锁，容易出现死锁现象

    举例：

    甲   1,3,5,7

    乙   2,4,7,5


    乐观锁:    乐观锁并不是真的锁。
            在更新的时候判断此时的库存是否是之前查询出的库存，
            如果相同，表示没人修改，可以更新库存，否则表示别人抢过资源，不再执行库存更新。



    举例：
                桌子上有10个肉包子。  9    8 

                现在有5个人。 这5个人，每跑1km。只有第一名才有资格吃一个肉包子。 

                5

                4

                3 

    步骤：
            1. 先记录某一个数据  
            2. 我更新的时候，再比对一下这个记录对不对  


MySQL数据库事务隔离级别主要有四种：

    Serializable：串行化，一个事务一个事务的执行。  用的并不多

    Repeatable read：可重复读，无论其他事务是否修改并提交了数据，在这个事务中看到的数据值始终不受其他事务影响。

v    Read committed：读取已提交，其他事务提交了对数据的修改后，本事务就能读取到修改后的数据值。

    Read uncommitted：读取未提交，其他事务只要修改了数据，即使未提交，本事务也能看到修改后的数据值。


    举例：     5,7 库存 都是  8

    甲   5,   7        5

    乙  7,    5         5


MySQL数据库默认使用可重复读（ Repeatable read）


"""





