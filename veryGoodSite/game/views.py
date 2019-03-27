from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection, IntegrityError
from game.forms.GuildForm import GuildForm


def index(request):
    if request.user.is_authenticated:
        return render(request, 'game/index.html',
                      {"userInfo": getUserInfo(request.user.userID,
                                               request.user.username)})
    return render(request, 'game/index.html')


@login_required
def guild(request):
    context = {
        'guildName': None,
        'guilds': getGuildInvites(request.user.userID),
        'form': GuildForm()
    }
    return render(request, 'game/guild.html', context)


@login_required
def createGuild(request):
    context = None
    return render(request, 'game/guild.html', context)


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
    except Exception:
        pass
    finally:
        c.close()
    return userInfo


def getGuildInvites(userID):
    c = connection.cursor()
    guilds = []
    try:
        c.execute("SELECT temp.name, temp.num_members \
                    FROM (SELECT Guild.name, COUNT(*) as num_members \
                          FROM Member INNER JOIN Guild ON \
                            Member.guildID=Guild.guildID \
                          WHERE Member.pending=0 \
                          GROUP BY Member.guildID) as temp, Member \
                    WHERE Member.userID=%s;", [userID])
        for tup in c.fetchall():
            guilds.append({"name": tup[0], "num_members": tup[1]})
    except Exception:
        pass
    finally:
        c.close()
    return guilds


def createNewGuild(guildName, userID):
    c = connection.cursor()
    success = 1
    try:
        c.execute("INSERT INTO Guild(name, owner) \
                       VALUES(%s, %s);",
                  [guildName, userID])
    except IntegrityError:
        success = 0
    except Exception:
        success = -1
    finally:
        c.close()
    return success
