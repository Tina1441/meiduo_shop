from apps.goods.models import SKU
from haystack import indexes
"""
0. 我们需要在模型所对应的子应用中创建search_indexes.py，以方便haystack来检索数据
1. 索引类必须得继承indexes.SearchIndex,indexes.Indexable
2. 我们必须定义一个字段 document=True 字段名起什么都可以 text只是惯例
    所有的索引类这个字段都一致就行
3.user_template=True 
    允许我们通过一些单独的文件 来指定对哪些字段字段进行检索
    这些单独的文件在哪里呢？
    模板文件夹下/search/indexes/子应用名目录/模型类名小写_text.txt
"""

class SKUIndex(indexes.SearchIndex,indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return SKU
    def index_queryset(self, using=None):
        return SKU.objects.all()

