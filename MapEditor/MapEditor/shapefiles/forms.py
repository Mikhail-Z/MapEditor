# coding: utf-8

from django import forms

class ImportShapefileForm(forms.Form):
    import_file = forms.FileField(label="Выберите файл фигур")