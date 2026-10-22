from django.urls import path
from apps.verifications.views import ImageCodeView,SendMessageView
urlpatterns = [
    path("image_codes/<str:uuid>/",ImageCodeView.as_view()),
    path("sms_codes/<mobile:mobile>/", SendMessageView.as_view())
]