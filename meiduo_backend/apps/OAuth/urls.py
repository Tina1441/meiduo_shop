from django.urls import path
from apps.OAuth.views import QQLoginURLView
urlpatterns = [
    path("qq/authorization/",QQLoginURLView.as_view())
]