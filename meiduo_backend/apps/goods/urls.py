from django.urls import path
from apps.goods.views import indexView,ListView,hotView,SKUSearchView,DetailView

urlpatterns = [
    path("index/",indexView.as_view()),
    path('list/<category_id>/skus/', ListView.as_view()),
    path('hot/<category_id>/',hotView.as_view()),
    path('search/', SKUSearchView()),
    path('detail/<sku_id>/', DetailView.as_view()),
]