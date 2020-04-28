# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.shortcuts import render, redirect
from .forms import LoginForm, RegistrationForm
from django.views.decorators.http import require_GET, require_POST, require_http_methods
import django.contrib.auth as auth
from django.urls import reverse
from django.db import IntegrityError


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")


@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                if "next" in request.POST:
                    return redirect(request.POST.get("next"))
                return redirect("shapefiles")
            form.add_error("username", "Пользователь не найден")
    else:
        initial = {"next": reverse("shapefiles")}
        form = LoginForm(initial=initial)
    context = {"form": form}
    return render(request, os.path.join(TEMPLATE_DIR, "login.html"), context=context)


@require_http_methods(["GET", "POST"])
def registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            user = auth.get_user_model()
            try:
                user.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                )
                return redirect("shapefiles")
            except IntegrityError as e:
                form.add_error("username", "Пользователь с таким именем уже зарегистрирован")

    else:
        form = RegistrationForm()
    context = {"form": form}
    return render(request, os.path.join(TEMPLATE_DIR, "registration.html"), context=context)


