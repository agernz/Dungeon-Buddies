from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import connection, IntegrityError
from register.forms.RegisterForm import RegisterForm


def index(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            password = make_password(data['password'])
            characterName = data['characterName']
            if createNewAccount(username, password, characterName):
                messages.success(request,
                                 "Successfully created account for {0}"
                                 .format(username))
                return redirect('game-index')
            else:
                messages.warning(request, "Username: {0} is already taken"
                                 .format(username))
    return render(request, 'register/index.html', {'form': form})


def createNewAccount(username, password, characterName):
    c = connection.cursor()
    success = True
    try:
        c.execute("INSERT INTO Account(username, password, characterName) \
                       VALUES(%s, %s, %s);",
                  [username, password, characterName])
    except IntegrityError:
        success = False
    finally:
        c.close()
    return success
