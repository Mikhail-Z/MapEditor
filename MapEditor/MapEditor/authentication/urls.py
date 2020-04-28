from django.contrib import admin
from django.conf.urls import url, include
from . import views

from django.contrib.auth.views import LogoutView


urlpatterns = [
    url(r'^login/$', views.login, name="login"),
    url(r'^logout/$', LogoutView.as_view(), {'next_page': '/login/'}, name="logout"),
    url(r'^registration/$', views.registration, name="registration"),
]