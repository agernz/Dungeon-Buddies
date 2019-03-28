from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.conf import settings
from django.db import connection


class authBackend:

    def authenticate(self, request, username=None, password=None):
        user = self.getUserFromNamePwd(username, password)
        if user:
            return user
        return None

    def get_user(self, user_id):
        c = connection.cursor()
        user = None
        try:
            c.execute("SELECT username FROM Account WHERE \
                                   userID=%s;", [user_id])
            username = c.fetchone()[0]
            user = User(username=username, userID=user_id)
        except Exception as e:
            if settings.DEBUG:
                print(e)
        finally:
            c.close()
        return user

    def getUserFromNamePwd(self, uname, pwd):
        c = connection.cursor()
        user = None
        try:
            c.execute("SELECT userID, password FROM Account WHERE \
                                   username=%s;", [uname])
            user_details = c.fetchone()
            if not check_password(pwd, user_details[1]):
                return None
            user = User(username=uname, userID=user_details[0])
        except Exception as e:
            if settings.DEBUG:
                print(e)
        finally:
            c.close()
        return user
