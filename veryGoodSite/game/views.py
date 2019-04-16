from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from game.forms.GuildForm import GuildForm
from game.forms.InviteForm import InviteForm
from django.http import JsonResponse
from django.utils import safestring
import random as r
import math
from game.sql import (
    getUserInfo, leaveGuild, getGuildInvites, getGuildMembers, getGuildRank,
    getTop100, getUserRank, getUserGuild, getTop100Guilds, createNewGuild,
    sendGuildInvite, joinGuildMember, sendRaidInvite, getRaidInvites,
    createRaid, getRaid, getMonsters, generateMonsters, noMonsters,
    updateRaid, deleteRaid, deleteInvites, updateMonsters, updateUserInfo
)

# TODO leave
# TODO stageing when no raid error
NUM_LEVELS = 5


def updateStats(request):
    if request.user.is_authenticated:
        user = getUserInfo(request.user.userID)
        bID = request.GET.get('bID')
        if user['skillPoints'] > 0:
            if bID == "1":
                user['health'] += 1
                user['skillPoints'] -= 1
            elif bID == "2":
                user['attack'] += 1
                user['skillPoints'] -= 1
            elif bID == "3":
                user['defense'] += 1
                user['skillPoints'] -= 1
            elif bID == "4":
                user['speed'] += 1
                user['skillPoints'] -= 1
            updateUserInfo(user)
    return JsonResponse(user)


def index(request):
    if request.user.is_authenticated:
        user = getUserInfo(request.user.userID)
        while (user['exp'] >= user['level'] * 5 + user['level']**2):
            user['skillPoints'] += 2
            user['exp'] -= user['level']*5
            user['level'] += 1
        updateUserInfo(user)
        return render(request, 'game/index.html',
                      {"userInfo": user})
    return render(request, 'game/index.html')


@login_required
def raidGetInvites(request):
    return JsonResponse(getRaidInvites(request.user.userID))


@login_required
def guildPage(request, form=GuildForm()):
    leave = request.GET.get('leave')
    if leave:
        leaveGuild(request.user.userID)
    guild = getUserGuild(request.user.userID)
    context = {
        'guildName': None,
        'members': None,
        'guilds': getGuildInvites(request.user.userID),
        'form': form
    }
    if guild:
        context['guildName'] = guild[1]
        context['members'] = getGuildMembers(request.user.userID, guild[0])
        context['is_admin'] = guild[2]
        context['inviteForm'] = InviteForm()
    return render(request, 'game/guild.html', context)


@login_required
def statsPage(request):
    user = getUserInfo(request.user.userID)
    context = {}

    if user:
        context['characterName'] = user['characterName']
        context['level'] = user['level']
        context['gold'] = user['gold']
        context['top100'] = getTop100()
        context['rank'] = getUserRank(request.user.userID)
        context['guild'] = getUserGuild(request.user.userID)
        context['top100Guilds'] = getTop100Guilds()
        if context['guild']:
            context['guildRank'] = getGuildRank(context['guild'])

    return render(request, 'game/stats.html', context)


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
def guildInvite(request):
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            guild = getUserGuild(request.user.userID)
            sendGuildInvite(data['userName'], guild[0])
    return guildPage(request)


@login_required
def joinGuild(request):
    guild = getUserGuild(request.user.userID)
    if guild:
        messages.info(request, "You cannot join a guild \
                      when you belong to: %s", guild[1])
    else:
        joinGuildMember(request.user.userID, request.GET.get('gID'))
    return guildPage(request)


@login_required
def raidPage(request):
    if request.GET.get('cancel') == '1':
        deleteInvites(request.user.userID)
        deleteRaid(request.user.userID)

    raid = getRaid(request.user.userID)
    if raid and raid['stageing'] == 1:
        return redirect("game-raid-stage", rID=raid['user1'])
    elif raid and raid['stageing'] == 0:
        return redirect("game-raid-render", rID=raid['user1'])

    levels = []
    for level in range(1, NUM_LEVELS + 1):
        levels.append({"description": "Reward: {0} gold and {1} exp. \
                       Lose {2} gold on failure."
                       .format(5**(level-1), 3*(2**(level-1)),
                               2*(5**(level-1)))})

    guild = getUserGuild(request.user.userID)
    context = {
        'members': '',
        'levels': levels,
        'guildID': ''
    }

    if guild:
        guildID = guild[0]
        guildMembers = getGuildMembers(request.user.userID, guildID, False)
        context['members'] = guildMembers
        context['guildID'] = guildID

    return render(request, 'game/raid.html', context)


@login_required
def raidStageRender(request, rID):
    level = request.POST.get("level", None)
    pid1 = request.POST.get("partner1", None)
    pid2 = request.POST.get("partner2", None)

    partner1 = partner2 = None
    if pid1 != "undefined":
        partner1 = getUserInfo(pid1)
    if pid2 != "undefined":
        partner2 = getUserInfo(pid2)

    p_name1 = p_name2 = None
    if partner1:
        p_name1 = partner1['username']
    if partner2:
        p_name2 = partner2['username']

    uInfo = getUserInfo(request.user.userID)
    context = {
        "level": level,
        "partners": [p_name1, p_name2],
        "partnerUserIDs": [pid1, pid2],
        "raidOwner": uInfo["username"],
        "is_owner": True,
        "pk": request.user.userID,
    }
    return render(request, 'game/raid-staging.html', context)


@login_required
def raidStage(request, rID):
    # TODO allow members to join raid
    if request.method == "POST":
        level = request.POST.get("level", None)
        pid1 = request.POST.get("partner1", None)
        pid2 = request.POST.get("partner2", None)

        partner1 = partner2 = None
        if pid1 != "undefined":
            partner1 = getUserInfo(pid1)
        if pid2 != "undefined":
            partner2 = getUserInfo(pid2)

        p_name1 = p_name2 = None
        if partner1:
            sendRaidInvite(request.user.userID, pid1)
            p_name1 = partner1['username']
        if partner2:
            sendRaidInvite(request.user.userID, pid2)
            p_name2 = partner2['username']

        uInfo = getUserInfo(request.user.userID)
        context = {
            "level": level,
            "partners": [p_name1, p_name2],
            "partnerUserIDs": [pid1, pid2],
            "raidOwner": uInfo["username"],
            "is_owner": True,
            "pk": request.user.userID,
        }

        if createRaid(request.user.userID, level, uInfo["health"]):
            # context['success'] = 1;
            return JsonResponse({"success": 1})
            # return render(request, 'game/raid-staging.html', context)
        else:
            messages.warning(request, "Could not create Raid")
            return redirect('game-raid')
            # return JsonResponse(context)
    else:
        raid = getRaid(rID)
        if not raid:
            return redirect('game-raid')
        # TODO get other players, show status and update
        # status when user accepts
        ownerInfo = getUserInfo(raid["user1"])

        pid1 = pid2 = p1username = p2username = None
        if raid["user2"] and raid["user2"] != request.user.userID:
            p1 = getUserInfo(raid["user2"])
            p1username = p1["username"]
            pid1 = p1["userID"]
        if raid["user3"] and raid["user3"] != request.user.userID:
            p2 = getUserInfo(raid["user3"])
            p2username = p2["username"]
            pid2 = p2["userID"]

        context = {
            "level": raid['raidLevel'],
            "partners": [p1username, p2username],
            "partnerUserIDs": [pid1, pid2],
            "raidOwner": ownerInfo["username"],
            "is_owner": request.user.userID == raid['user1'],
            "pk": raid['user1']
        }

        return render(request, 'game/raid-staging.html', context)


@login_required
def joinRaid(request):
    id = request.user.userID
    raid_owner = request.GET.get('id')
    raid = getRaid(raid_owner)
    if raid:
        userInfo = getUserInfo(id)
        if raid['user2'] == id or raid['user3'] == id:
            messages.info(request, "You have already joined")
        elif not raid['user2']:
            raid['user2'] = id
        else:
            raid['user3'] = id
        updateRaid(raid)
        return redirect("game-raid-stage", rID=raid_owner)
    messages.warning(request, "Raid Expired.")
    return redirect("game-raid")

@login_required
def raidReady(request, rID):
    id = request.user.userID
    raid = getRaid(rID)
    if raid:
        userInfo = getUserInfo(id)
        if raid['user2'] == id:
            raid['health2'] = userInfo['health']
        elif raid['user3'] == id:
            raid['health3'] = userInfo['health']
        updateRaid(raid)
        return JsonResponse({"success":1})
    messages.warning(request, "Raid Expired.")
    return redirect("game-raid")


@login_required
def raidRender(request, rID):
    raid = getRaid(rID)
    if not raid:
        return redirect('game-raid')
    pk = raid['user1']

    # first time check for starting raid
    if raid['stageing'] == 1 and request.user.userID == pk:
        deleteInvites(request.user.userID)
        raid['stageing'] = 0
        updateRaid(raid)
    elif raid['stageing'] == 1:
        redirect('game-raid-stage', rID=pk)

    # create monsters at start
    if noMonsters(pk):
        generateMonsters(pk, raid['raidLevel'])

    context = {
        "pk": pk,
        "won": False,
        "lose": False,
    }
    return render(request, 'game/raid-play.html', context)


# 1 == won, 0 == lost, -1 othewise
def hasWonOrLost(raid, monsters):
    if raid['health1'] == 0 and raid['health2'] == 0 and raid['health3'] == 0:
        return 0
    for m in monsters:
        if m['health'] != 0:
            return -1
    return 1


def endRaid(userInfos, raid, has_won):
    for user in userInfos:
        if user['userID'] != -1:
            if has_won:
                user['exp'] += (2**(raid['raidLevel'] - 1)) * 3
                user['gold'] += 5**(raid['raidLevel'] - 1)
            else:
                user['exp'] += 1
                user['gold'] = max(0, user['gold'] -
                                   2*(5**(raid['raidLevel'] - 1)))
            updateUserInfo(user)


def playerAttack(player, monsters):
    if r.randint(0, 100) < 5:
        return ()
    for m in monsters:
        if m['monsterID'] == int(player['move']):
            var_attack = r.randint(0, int(player['attack'] * .25))
            var_attack *= r.randint(-1, 1)
            player_attack_value = max(1, player['attack'] - m['defense']
                                      + var_attack)
            m['health'] = max(0, m['health'] - player_attack_value)
            return (m['name'], player_attack_value)


def monsterAttack(monster, players, raid):
    p_len = len(players) - 1
    if p_len < 0 or r.randint(0, 100) < 10:
        return ()
    if p_len != 0:
        pid = r.randint(0, p_len)
    else:
        pid = 0
    player_heatlth = players[pid]['raid_health']
    var_attack = max(1, int(monster['attack'] * .5))
    var_attack *= r.randint(-1, 1)
    monster_attack_value = max(1, monster['attack'] - players[pid]['defense']
                               + var_attack)
    player_heatlth = max(0, player_heatlth - monster_attack_value)
    players[pid]['raid_health'] = player_heatlth

    player_id = players[pid]['userID']
    if player_id == raid['user1']:
        raid['health1'] = player_heatlth
    if player_id == raid['user2']:
        raid['health2'] = player_heatlth
    if player_id == raid['user3']:
        raid['health3'] = player_heatlth

    charName = players[pid]['characterName']
    if player_heatlth == 0:
        players.pop(pid)
    return (charName, monster_attack_value)


# TODO allow player to leave raid, they lose gold
@login_required
def raidUpdate(request):
    this_user = request.user.userID
    raid = getRaid(this_user)
    if not raid:
        return JsonResponse({})
    pk = raid['user1']
    mID = request.GET.get('mID')
    if mID:
        if this_user == raid['user1'] and raid['health1'] != 0:
            raid['move1'] = mID
        elif this_user == raid['user2'] and raid['health2'] != 0:
            raid['move2'] = mID
        elif this_user == raid['user3'] and raid['health3'] != 0:
            raid['move3'] = mID
        updateRaid(raid)

    monsters = getMonsters(pk)

    """
    # check for win/loss
    wl = hasWonOrLost(raid, monsters)
    has_won = 1 == wl
    has_lost = 0 == wl

    userIDs = [raid['user1'], raid['user2'], raid['user3']]
    if has_won or has_lost:
        if request.user.userID == pk:
            players = []
            for uid in userIDs:
                uInfo = getUserInfo(uid)
                players.append(uInfo)
            endRaid(players, raid, has_won)
            deleteRaid(pk)
        return redirect('game-raid')
    """

    # carry out attacks if everyone is ready
    all_ready = True
    userIDs = [raid['user1'], raid['user2'], raid['user3']]
    userMoves = [raid['move1'], raid['move2'], raid['move3']]
    userHealth = [raid['health1'], raid['health2'], raid['health3']]
    for uid, um, health in zip(userIDs, userMoves, userHealth):
        if uid and health != 0 and um is None:
            all_ready = False

    event_log = []
    if all_ready:
        actors = []
        players = []
        for uid, move, health in zip(userIDs, userMoves, userHealth):
            if uid and health != 0:
                uInfo = getUserInfo(uid)
                uInfo['move'] = move
                uInfo['raid_health'] = health
                actors.append(uInfo)
                players.append(uInfo)

        # sort monsters and players by speed
        actors.extend(monsters)
        actors = sorted(actors, key=lambda k: k['speed'], reverse=True)

        for actor in actors:
            is_player = 'userID' in actor.keys()
            if is_player and actor['raid_health']:
                event = playerAttack(actor, monsters)
                if event:
                    event_log.append(
                        safestring.mark_safe("<li class='list-group-item \
                                             list-group-item-success'>{0} \
                                             attacked {1} for {2} damage!</li>"
                                             .format(actor['characterName'],
                                                     event[0], event[1])))
                else:
                    event_log.append(
                        safestring.mark_safe("<li class='list-group-item \
                                             list-group-item-secondary'>{0} \
                                             missed!</li>".format(
                                                 actor['characterName'])))
            elif not is_player and actor['health']:
                event = monsterAttack(actor, players, raid)
                if event:
                    event_log.append(
                        safestring.mark_safe("<li class='list-group-item \
                                             list-group-item-danger'>{0} \
                                             attacked {1} for {2} damage!</li>"
                                             .format(actor['name'],
                                                     event[0], event[1])))
                else:
                    event_log.append(
                        safestring.mark_safe("<li class='list-group-item \
                                             list-group-item-secondary'>{} \
                                             missed!</li>"
                                             .format(actor['name'])))
        updateMonsters(monsters)
        raid['move1'] = None
        raid['move2'] = None
        raid['move3'] = None
        updateRaid(raid)

    # build UI components
    userInfos = []
    for uid in userIDs:
        if uid:
            userInfos.append(getUserInfo(uid))
        else:
            userInfos.append({"userID": -1, "characterName": None})

    party = []
    userHealth = [raid['health1'], raid['health2'], raid['health3']]
    userMoves = [raid['move1'], raid['move2'], raid['move3']]
    no_move = False
    this_health = 0
    for user, health, move in zip(userInfos, userHealth, userMoves):
        if user['userID'] != -1:
            if this_user == user['userID'] and move is None:
                no_move = True
            if this_user == user['userID']:
                this_health = health
            party.append({
                "name": user['characterName'],
                "health": health,
                "no_move": move is None,
            })

    # check for win/loss
    wl = hasWonOrLost(raid, monsters)
    has_won = 1 == wl
    has_lost = 0 == wl

    if has_won or has_lost and this_user == pk:
        endRaid(userInfos, raid, has_won)
        deleteRaid(pk)

    context = {
        "monsters": monsters,
        "party": party,
        "no_move": no_move,
        "health": this_health,
        "events": event_log,
        "won": has_won,
        "lose": has_lost
    }
    return JsonResponse(context)
