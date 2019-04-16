# Generated by Django 2.1.7 on 2019-03-22 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='goodUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('identifier', models.PositiveIntegerField(unique=True)),
                ('email', models.CharField(max_length=1)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
