from django import forms
from django.core.validators import RegexValidator


onlyCharNum = RegexValidator(r'^[a-zA-Z0-9]+$',
                             "Field can only contain letters and numbers.")


class RegisterForm(forms.Form):
    username = forms.CharField(label="Username",
                               max_length=30,
                               validators=[onlyCharNum])
    characterName = forms.CharField(label="Character Name",
                                    max_length=30,
                                    validators=[onlyCharNum])
    password = forms.CharField(min_length=8, max_length=120)
