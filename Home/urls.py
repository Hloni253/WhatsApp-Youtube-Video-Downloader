from django.urls import path
from .views import Webhook, Choose_Format, Download

urlpatterns = [
    path("", Webhook),
    path("D", Choose_Format),
    path("D/<file_type>", Download),
    ]
