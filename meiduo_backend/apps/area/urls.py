from django.urls import path
from apps.area.views import AreaView,SubAreaView
urlpatterns = [
    path('areas/',AreaView.as_view()),
    path('areas/<id>/',SubAreaView.as_view()),

]