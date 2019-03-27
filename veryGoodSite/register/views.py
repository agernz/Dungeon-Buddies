from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.db import connection, IntegrityError
from register.forms.RegisterForm import RegisterForm
from register.forms.SignInForm import SignInForm


BACKEND = 'register.authenticate.authBackend'


def index(request):
    if request.user.is_authenticated:
        messages.info(request, "You are logged in")
        return redirect('game-index')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            password = data['password']
            characterName = data['characterName']
            result = createNewAccount(username,
                                      make_password(password), characterName)
            if result == 1:
                user = authenticate(request,
                                    username=username, password=password)
                login(request, user, backend=BACKEND)
                messages.success(request,
                                 "Successfully created account for {0}."
                                 .format(username))
                return redirect('game-index')
            elif result == 0:
                messages.warning(request, "Username: {0} is already taken."
                                 .format(username))
            else:
                messages.warning(request, "Something went wrong :(")
    return render(request, 'register/index.html', {'form': form})


def loginUser(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('game-index')
    form = SignInForm()
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            password = data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('game-index')
            else:
                messages.warning(request, "Incorrect username or password!")
    return render(request, 'register/login.html', {'form': form})


def logoutUser(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect('game-index')


def createNewAccount(username, password, characterName):
    c = connection.cursor()
    success = 1
    try:
        c.execute("INSERT INTO Account(username, password, characterName) \
                       VALUES(%s, %s, %s);",
                  [username, password, characterName])
        c.execute("SELECT userID FROM Account WHERE username=%s;", [username])
        userID = c.fetchone()[0]
        c.execute("INSERT INTO register_gooduser(username, userID, password) \
                       VALUES(%s, %s, %s);", [username, userID, password])
    except IntegrityError:
        success = 0
    except Exception:
        success = -1
    finally:
        c.close()
    return success
