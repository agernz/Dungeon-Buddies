from django import forms
from django.core.validators import RegexValidator


onlyCharNum = RegexValidator(r'^[a-zA-Z0-9]+$',
                             "Field can only contain letters and numbers.")


class GuildForm(forms.Form):
    guildName = forms.CharField(label="Guild Name",
                                max_length=120,
                                validators=[onlyCharNum])
