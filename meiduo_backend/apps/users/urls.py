from django.urls import path
from apps.users.views import UsernameCountView,MobileView
urlpatterns = [
       path("usernames/<username:username>/count/", UsernameCountView.as_view()),
       path("mobiles/<mobile:mobile>/count/", MobileView.as_view()),
]