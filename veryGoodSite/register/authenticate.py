from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db import connection


class authBackend:

    def authenticate(self, request, username=None, password=None):
        user = self.getUserFromNamePwd(username, password)
        if user:
            return user
        return None

    def get_user(self, user_id):
        c = connection.cursor()
        try:
            c.execute("SELECT username FROM Account WHERE \
                                   userID=%s;", [user_id])
            user = c.fetchone()
            return User(user[0])
        except Exception:
            return None
        finally:
            c.close()

    def getUserFromNamePwd(self, uname, pwd):
        c = connection.cursor()
        try:
            c.execute("SELECT password FROM Account WHERE \
                                   username=%s;", [uname])
            user = c.fetchone()
            if not check_password(pwd, user[0]):
                return None
            return User(username=uname)
        except Exception:
            return None
        finally:
            c.close()
