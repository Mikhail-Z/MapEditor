# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

# Create your views here.


def login(request):
    return render(request, "login.html")


def register(request):
    form = UserCreationForm()
    context = {"form": form}
    return render(request, "registration.html", context)