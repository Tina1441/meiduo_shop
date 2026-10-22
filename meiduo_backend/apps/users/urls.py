from django.urls import path
from apps.users.views import UsernameCountView,MobileView,RegisterView,LoginView
urlpatterns = [
       path("usernames/<username:username>/count/", UsernameCountView.as_view()),
       path("mobiles/<mobile:mobile>/count/", MobileView.as_view()),
       path("register/", RegisterView.as_view()),
       path("login/", LoginView.as_view()),

]