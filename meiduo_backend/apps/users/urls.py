from django.urls import path
from apps.users.views import UsernameCountView,MobileView,RegisterView
urlpatterns = [
       path("usernames/<username:username>/count/", UsernameCountView.as_view()),
       path("mobiles/<mobile:mobile>/count/", MobileView.as_view()),
       path("register/", RegisterView.as_view()),

]