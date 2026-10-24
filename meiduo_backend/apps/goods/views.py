# from pathlib import Path
# from fdfs_client.client import Fdfs_client
#
# # views.py 位于 apps/goods/ 下
# BASE_DIR = Path(__file__).resolve().parents[2]
#
# conf_path = BASE_DIR / 'utils' / 'fastdfs' / 'client.conf'
#
# print('配置文件路径：', conf_path)
# print('配置文件存在：', conf_path.exists())
#
# client = Fdfs_client(str(conf_path))
#
# # 图片的绝对路径
# image_path = r'D:\Docker\images\a.jpg'
#
# print('图片是否存在：', Path(image_path).is_file())
#
# result = client.upload_by_filename(image_path)
# print('上传结果：', result)
#
# """
# {'Group name': 'group1', 'Remote file_id': 'group1\\M00/00/00/wKhBA2rcFb-ACgVuAAJXemwU4Js493.jpg', 'Status': 'Upload successed.', 'Local file name': 'D:\\Docker\\images\\a.jpg', 'Uploaded size': '149.00KB', 'Storage IP': '127.0.0.1'}
# """
# # 获取field_id upload上传成功后有字典返回
from tkinter.constants import PAGES

from django.shortcuts import render
from django.views import View
from utils.goods import get_categories,get_breadcrumb
from apps.contents.models import ContentCategory
from django.http import JsonResponse

class indexView(View):
    def get(self, request):
        """
        首页数据分两部分：商品分类数据 广告数据
        """
        # 1. 分类数据
        categories = get_categories()
        # 2. 广告数据
        contents = {}
        content_category = ContentCategory.objects.all()

        for content in content_category:
            contents[content.key] = content.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request,'index.html',context)
"""
需求：
        根据点击的分类，来获取分类数据（有排序，有分页）
前端：
        前端会发送一个axios请求， 分类id 在路由中， 
        分页的页码（第几页数据），每页多少条数据，排序也会传递过来
后端：
    请求          接收参数
    业务逻辑       根据需求查询数据，将对象数据转换为字典数据
    响应          JSON

    路由      GET     /list/category_id/skus/
    步骤
        1.接收参数
        2.获取分类id
        3.根据分类id进行分类数据的查询验证
        4.获取面包屑数据
        5.查询分类对应的sku数据，然后排序，然后分页
        6.返回响应
"""
from apps.goods.models import GoodsCategory,SKU
from django.core.paginator import Paginator
class ListView(View):
    def get(self, request, category_id):
        # 1.接收参数
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        ordering = request.GET.get('ordering')
        # 2.获取分类id
        # 3.根据分类id进行分类数据的查询验证
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except:
            return JsonResponse({'code':400,'errmsg':'参数缺失'})
        # 4.获取面包屑数据
        breadcrumb = get_breadcrumb(category)
        # 5.查询分类对应的sku数据，然后排序，然后分页
        goods = SKU.objects.filter(category=category,is_launched=True).order_by(ordering)
        # 分页
        pages_goods = Paginator(goods, page_size)

        per_goods = pages_goods.page(page)
        goods_dict = []
        for good in per_goods.object_list:
            goods_dict.append({
                'id': good.id,
                'name': good.name,
                'price': good.price,
                'default_image_url': good.default_image.url
            })

        count = pages_goods.count

        # 6.返回响应

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'list': goods_dict, 'count': count, 'breadcrumb': breadcrumb})

# 1. 获取请求参数
# 2. 根据category_id查询category
# 3. 根据category查询sku，按照销量排序
# 4. 格式化响应skus列表
# 5. 返回响应
class hotView(View):
    def get(self, request, category_id):
        skus = SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url,
                'sales': sku.sales
            })

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'hot_skus': hot_skus})

########################################################################
"""
搜索 

1. 我们不使用like

2. 我们使用 全文检索
    全文检索即在指定的任意字段中进行检索查询
    
3. 全文检索方案需要配合搜索引擎来实现

4. 搜索引擎
    
    原理：  关键词与词条的对应关系，并记录词条的位置
                                            
    
        1  --- 我爱北京天安门                      我爱， 北京，天安门
        
        2 --- 王红，我爱你，我想你想的睡不着觉        王红，我爱，我爱你，睡不着觉，想你，
        
        3 ---  我睡不着觉                          我，睡不着觉 
        
        
        我爱


5. Elasticsearch
    进行分词操作 
    分词是指将一句话拆解成多个单字或词，这些字或词便是这句话的关键词
    
    下雨天 留客天 天留我不 留
    
    
6. 
    数据         <----------Haystack--------->             elasticsearch 
                        
                        ORM(面向对象操作模型)                 mysql,oracle,sqlite,sql server
"""

"""
 我们/数据         <----------Haystack--------->             elasticsearch 

 我们是借助于 haystack 来对接 elasticsearch
 所以 haystack 可以帮助我们 查询数据
"""





