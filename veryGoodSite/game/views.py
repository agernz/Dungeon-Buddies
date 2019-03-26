from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'game/index.html')

@login_required
def guild(request):
    guilds = ['abc', '123']
    context = {
        'guilds': guilds,
        'form': guildForm()
    }
    return render(request, 'game/guild.html', context)
