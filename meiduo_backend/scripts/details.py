#######################################################################
"""
首页，详情页面

我们都是先查询数据库的数据
然后再进行HTML页面的渲染

不管是 数据库的数据缓存 还是 HTML页面的渲染（特别是分类渲染，比较慢） 多少都会影响用户的体验

最好的体验 是
用户  直接 就可以访问到  经过数据库查询，已经渲染的HTML页面 静态化


 经过数据库查询，已经渲染的HTML页面，写入到指定目录

"""
# 这个函数 能够帮助我们 数据库查询，渲染HTML页面，然后把渲染的HTML写入到指定文件

import os
import django
import sys



sys.path.insert(0,'../')

# 1. 设置 Django 的配置文件环境变量（请把 'meiduo_backend.settings' 换成你实际的 settings 模块路径）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_backend.settings')

# 2. 手动初始化 Django 环境
django.setup()

import time
from utils.goods import get_categories, get_breadcrumb, get_goods_specs
from meiduo_backend import settings
from apps.goods.models import SKU

def generic_meiduo_index(sku):
    print('--------------%s-------------'%time.ctime())
        # 1. 分类数据
    categories = get_categories()
    # 2. 面包屑
    breadcrumb = get_breadcrumb(sku.category)
    # 3. sku
    # 4. 规格数据
    goods_specs = get_goods_specs(sku)

    context = {

        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': goods_specs,

    }

    # 1. 加载渲染的模板
    from django.template import loader
    index_template=loader.get_template('detail.html')

    # 2. 把数据给模板
    index_html_data=index_template.render(context)
    # 3. 把渲染好的HTML，写入到指定文件

    # base_dir 的上一级
    file_path=os.path.join(os.path.dirname(settings.BASE_DIR),f'front_end_pc/front_end_pc/goods/{sku.id}.html')

    with open(file_path,'w',encoding='utf-8') as f:
        f.write(index_html_data)

if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        generic_meiduo_index(sku)