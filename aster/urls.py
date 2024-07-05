
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("recording_info/", views.recording_info, name="recording_info"),
    path("admin/", admin.site.urls),
]
