# Generated by Django 2.1.7 on 2019-03-22 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0005_auto_20190322_2004'),
    ]

    operations = [
        migrations.AddField(
            model_name='gooduser',
            name='username',
            field=models.CharField(default=0, max_length=30, unique=True),
        ),
    ]
