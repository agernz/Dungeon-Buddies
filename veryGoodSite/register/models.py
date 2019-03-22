from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class goodManager(BaseUserManager):

    def create_user(self, username, password):
        pass

    def create_superuser(self, email, password):
        pass


class goodUser(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    object = goodManager()
