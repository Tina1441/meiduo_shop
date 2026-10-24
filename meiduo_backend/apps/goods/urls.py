from django.urls import path
from apps.goods.views import indexView,ListView

urlpatterns = [
    path("index/",indexView.as_view()),
    path('list/<category_id>/skus/', ListView.as_view()),
]