from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class goodManager(BaseUserManager):

    def create_user(self, username, userID, password):
        user = self.model(username=username, userID=userID)
        return user

    def create_superuser(self, email, password):
        pass


class goodUser(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True)
    userID = models.SmallIntegerField(unique=True, default=0)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['userID']

    object = goodManager()

    def __str__(self):
        return "{0}, {1}".format(self.userID, self.username)
