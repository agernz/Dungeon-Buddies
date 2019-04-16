from django import forms
from django.core.validators import RegexValidator


onlyCharNum = RegexValidator(r'^[a-zA-Z0-9]+$',
                             "Field can only contain letters and numbers.")


class InviteForm(forms.Form):
    userName = forms.CharField(label="Enter Username",
                               max_length=30,
                               validators=[onlyCharNum])
