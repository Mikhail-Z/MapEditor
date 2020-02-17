from django.contrib import admin
from django.conf.urls import url, include
from . import views

from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    url(r'^login/$', LoginView.as_view()),
    url(r'^logout/$', LogoutView.as_view(), {'next_page': '/login/'}),
]