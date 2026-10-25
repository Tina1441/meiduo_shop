from django.urls import path
from apps.carts.views import CartsView,CartsAllSelect

urlpatterns = [
    path('carts/',CartsView.as_view()),
    path('carts/selection/',CartsAllSelect.as_view()),
]