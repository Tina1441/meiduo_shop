from django.urls import path
from apps.users.views import UsernameCountView, MobileView, RegisterView, LoginView, LogOutView, CenterView, EmailView,EmailVerifyView,AddressCreateView

urlpatterns = [
       path("usernames/<username:username>/count/", UsernameCountView.as_view()),
       path("mobiles/<mobile:mobile>/count/", MobileView.as_view()),
       path("register/", RegisterView.as_view()),
       path("login/", LoginView.as_view()),
       path("logout/", LogOutView.as_view()),
       path("info/", CenterView.as_view()),
       path("emails/", EmailView.as_view()),
       path('emails/verification/',EmailVerifyView.as_view()),
       path('addresses/create/',AddressCreateView.as_view()),



]