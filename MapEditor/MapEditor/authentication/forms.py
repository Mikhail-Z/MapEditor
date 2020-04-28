# -*- coding: utf-8 -*-

from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя',
        min_length=3, max_length=255,
        error_messages={"required": "Логин должен быть длиной минимум 3 символа"},
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        ),
        min_length=8, max_length=255,
        error_messages={"required": "Пароль должен быть длиной минимум 8 символов"}
    )


class RegistrationForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя',
        min_length=3, max_length=255,
        error_messages={"required": "Логин должен быть длиной минимум 3 символа"},
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        ),
        min_length=8, max_length=255,
        error_messages={"required": "Пароль должен быть длиной минимум 8 символов"}
    )
    repeat_password = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        ),
        min_length=8, max_length=255,
        error_messages={"required": "Пароль должен быть длиной минимум 8 символов"}
    ),
    email = forms.EmailField(
        label='Эл. почта',
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )

    def clean(self):
        super(RegistrationForm, self).clean()
        errors = []
        password = self.cleaned_data["password"]
        repeat_password = self.cleaned_data["repeat_password"]
        if password != repeat_password:
            errors.append("Повторенный пароль не совпадает с первоначальным".decode("utf-8"))
            self._errors["repeat_password"] = ["Повторенный пароль не совпадает с первоначальным".decode("utf-8")]
        #if len(errors):
        #    raise forms.ValidationError([' & '.join(errors)])

        return self.cleaned_data