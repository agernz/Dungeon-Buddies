from django.shortcuts import render


def index(request):
    return render(request, 'game/index.html',
                  {'is_auth': request.user.is_authenticated})


def guild(request):
    return render(request, 'game/index.html',
                  {'is_auth': request.user.is_authenticated})
