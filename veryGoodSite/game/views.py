from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.contrib import messages
from django.conf import settings
from game.forms.GuildForm import GuildForm


def index(request):
    if request.user.is_authenticated:
        return render(request, 'game/index.html',
                      {"userInfo": getUserInfo(request.user.userID,
                                               request.user.username)})
    return render(request, 'game/index.html')


@login_required
def guildPage(request, form=GuildForm()):
    guild = getUserGuild(request.user.userID)
    context = {
        'guildName': None,
        'members': None,
        'guilds': getGuildInvites(request.user.userID),
        'form': form
    }
    if guild:
        context['guildName'] = guild[1]
        context['members'] = None
    return render(request, 'game/guild.html', context)


@login_required
def createGuild(request):
    if request.method == 'POST':
        form = GuildForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            guild = getUserGuild(request.user.userID)
            if guild:
                messages.info(request, "You cannot create a new guild \
                              when you belong to: %s", guild[1])
            else:
                createNewGuild(request.user.userID, data['guildName'])
    return guildPage(request, form)


@login_required
def joinGuild(request):
    guild = getUserGuild(request.user.userID)
    if guild:
        messages.info(request, "You cannot join a guild \
                      when you belong to: %s", guild[1])
    else:
        joinGuildMember(request.user.userID, request.GET.get('gID'))
    return guildPage(request)


def getUserInfo(userID, uname):
    c = connection.cursor()
    userInfo = {
        "username": uname,
        "charName": "",
        "exp": "",
        "gold": ""
    }
    try:
        c.execute("SELECT characterName, experience, gold \
                       FROM Account WHERE userID=%s;", [userID])
        uInfo = c.fetchone()
        userInfo["charName"] = uInfo[0]
        userInfo["exp"] = uInfo[1]
        userInfo["gold"] = uInfo[2]
    except Exception as e:
        if settings.DEBUG:
            print(e)
    finally:
        c.close()
    return userInfo


def getUserGuild(userID):
    c = connection.cursor()
    guild = None
    try:
        c.execute("SELECT Guild.guildID, Guild.name FROM Account, Guild \
                  WHERE Account.userID=%s \
                  AND Guild.guildID=Account.guildID;", [userID])
        guild = c.fetchone()
    except Exception as e:
        if settings.DEBUG:
            print(e)
    finally:
        c.close()
    return guild


def getGuildInvites(userID):
    c = connection.cursor()
    guilds = []
    try:
        c.execute("SELECT temp.guildID, temp.name, temp.num_members \
            FROM (SELECT Guild.guildID, Guild.name, \
            COUNT(*) as num_members \
                  FROM Member INNER JOIN Guild ON \
                    Member.guildID=Guild.guildID \
                  WHERE Member.pending=0 \
                  GROUP BY Member.guildID) as temp \
            WHERE temp.guildID IN (SELECT m.guildID \
            FROM Member as m WHERE m.userID=%s AND m.pending=1);", [userID])
        for tup in c.fetchall():
            guilds.append({"gID": tup[0],
                           "name": tup[1], "num_members": tup[2]})
    except Exception as e:
        if settings.DEBUG:
            print(e)
    finally:
        c.close()
    return guilds


def joinGuildMember(userID, guildID):
    c = connection.cursor()
    try:
        c.execute("DELETE FROM Member WHERE userID=%s", [userID])
        c.execute("INSERT INTO Member(userID, guildID, pending) \
                       VALUES(%s, %s, 0);",
                  [userID, guildID])
        c.execute("UPDATE Account SET guildID=%s WHERE Account.userID=%s;",
                  [guildID, userID])
    except Exception as e:
        if settings.DEBUG:
            print(e)
    finally:
        c.close()


def createNewGuild(userID, guildName):
    c = connection.cursor()
    try:
        c.execute("DELETE FROM Member WHERE userID=%s", [userID])
        c.execute("INSERT INTO Guild(name, owner) \
                       VALUES(%s, %s);",
                  [guildName, userID])
        c.execute("SELECT guildID FROM Guild WHERE owner=%s", [userID])
        guildID = c.fetchone()[0]
        c.execute("INSERT INTO Member(userID, guildID, pending, admin) \
                       VALUES(%s, %s, 0, 1);",
                  [userID, guildID])
        c.execute("UPDATE Account SET guildID=%s WHERE Account.userID=%s;",
                  [guildID, userID])
    except Exception as e:
        if settings.DEBUG:
            print(e)
    finally:
        c.close()
