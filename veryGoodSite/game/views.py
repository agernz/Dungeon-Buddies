from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from game.forms.GuildForm import GuildForm
from game.forms.InviteForm import InviteForm
from django.http import JsonResponse
from django.utils import safestring
import math
import random as r
from game.sql import (
    getUserInfo, leaveGuild, getGuildInvites, getGuildMembers, getGuildRank,
    getTop100, getUserRank, getUserGuild, getTop100Guilds, createNewGuild,
    sendGuildInvite, joinGuildMember, sendRaidInvite, getRaidInvites,
    createRaid, getRaidStatus, getRaid, getMonsters, getPartyNames,
    generateMonsters, noMonsters, updateRaid, deleteRaid, deleteInvites,
    updateMonsters, updateUserInfo
)


NUM_LEVELS = 5


def index(request):
    if request.user.is_authenticated:
        return render(request, 'game/index.html',
                      {"userInfo": getUserInfo(request.user.userID)})
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

    raidStatus = getRaidStatus(request.user.userID)
    if raidStatus == 1:
        return redirect("game-raid-stage")
    elif raidStatus == 0:
        return redirect("game-raid-play")

    levels = []
    for l in range(1, NUM_LEVELS + 1):
        levels.append({"description": "You may recieve {0} gold and {1} exp \
                       or lose {2} gold"
                       .format(math.floor(l * 1.5), l, math.ceil(l * 1.5))})

    context = {
        'members': '',
        'levels': levels
    }
    guildID = getUserGuild(request.user.userID)
    if guildID:
        guildMembers = getGuildMembers(request.user.userID, guildID[0], False)
        context['members'] = guildMembers

    return render(request, 'game/raid.html', context)


@login_required
def raidStage(request):
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

        context = {
            "level": level,
            "partners": [p_name1, p_name2],
            "is_owner": True
        }

        uInfo = getUserInfo(request.user.userID)
        if createRaid(request.user.userID, level, uInfo["health"]):
            return render(request, 'game/raid-staging.html', context)
        else:
            messages.warning(request, "Could not create Raid")
            return redirect('game-raid')

    else:
        raid = getRaid(request.user.userID)
        # TODO get other players, show status and update
        # status when user accepts
        context = {
            "level": raid['raidLevel'],
            "partners": [None, None],
            "is_owner": request.user.userID == raid['user1']
        }
        return render(request, 'game/raid-staging.html', context)

@login_required
def joinRaid(request):
    id = request.GET.get('id')
    
    print(id)
    return redirect('game-raid-play')


# 1 == won, 0 == lost, -1 othewise
def hasWonOrLost(raid, monsters):
    if raid['health1'] == 0 and raid['health2'] == 0 and raid['health3'] == 0:
        return 0
    for m in monsters:
        if m['health'] != 0:
            return -1
    return 1


def endRaid(actors, raid, has_won):
    for user in actors:
        keys = user.keys()
        if 'userID' in keys:
            if 'move' in keys:
                del user['move']
            if 'raid_health' in keys:
                del user['raid_health']
            if has_won:
                user['exp'] += raid['raidLevel']
                user['gold'] += math.floor(raid['raidLevel'] * 1.5)
            else:
                user['exp'] += 1
                user['gold'] = max(0, user['gold'] - raid['raidLevel'])
            updateUserInfo(user)


def playerAttack(player, monsters):
    if r.randint(0, 100) < 5:
        return ()
    for m in monsters:
        if m['monsterID'] == player['move']:
            var_attack = max(1, int(player['attack'] * .5))
            var_attack *= r.randint(-1, 1)
            player_attack_value = max(1, player['attack'] - m['defense']
                                      + var_attack)
            m['health'] = max(0, m['health'] - player_attack_value)
            return (m['name'], player_attack_value)


def monsterAttack(monster, players, raid):
    if r.randint(0, 100) < 10:
        return ()
    p_len = len(players) - 1
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


@login_required
def raidPlay(request):
    # TODO error handling
    # TODO allow player to leave raid, they lose gold

    raid = getRaid(request.user.userID)
    if not raid:
        return redirect('game-raid')
    pk = raid['user1']

    # first time check for starting raid
    if raid['stageing'] == 1:
        deleteInvites(request.user.userID)
        raid['stageing'] = 0
        updateRaid(raid)

    # create monsters at start
    if noMonsters(pk):
        generateMonsters(pk, raid['raidLevel'])
    monsters = getMonsters(pk)

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
                    event_log.append(safestring.mark_safe("<li class='list-group-item list-group-item-success'>{0} attacked {1} for {2} damage!</li>"
                                     .format(actor['characterName'],
                                             event[0], event[1])))
                else:
                    event_log.append(safestring.mark_safe("<li class='list-group-item list-group-item-secondary'>{0} missed!</li>"
                                     .format(actor['characterName'])))
            elif not is_player and actor['health']:
                event = monsterAttack(actor, players, raid)
                if event:
                    event_log.append(safestring.mark_safe("<li class='list-group-item list-group-item-danger'>{0} attacked {1} for {2} damage!</li>"
                                     .format(actor['name'],
                                             event[0], event[1])))
                else:
                    event_log.append(safestring.mark_safe("<li class='list-group-item list-group-item-secondary'>{} missed!</li>"
                                     .format(actor['name'])))
        updateMonsters(monsters)
        raid['move1'] = None
        raid['move2'] = None
        raid['move3'] = None
        updateRaid(raid)

    # build UI components
    this_user = request.user.userID
    party = []
    userHealth = [raid['health1'], raid['health2'], raid['health3']]
    userMoves = [raid['move1'], raid['move2'], raid['move3']]
    no_move = False
    this_health = 0
    for i, name, health, move in zip(userIDs, getPartyNames(userIDs),
                                     userHealth, userMoves):
        if this_user == i and move is None:
            no_move = True
        if this_user == i:
            this_health = health
        party.append({
            "name": name,
            "health": health,
            "no_move": move is None,
        })

    # check for win/loss
    wl = hasWonOrLost(raid, monsters)
    has_won = 1 == wl
    has_lost = 0 == wl

    if has_won or has_lost and this_user == pk:
        endRaid(actors, raid, has_won)
        deleteRaid(pk)

    context = {
        "monsters": monsters,
        "party": party,
        "no_move": no_move,
        "health": this_health,
        "pk": pk,
        "events": event_log,
        "has_won": has_won,
        "has_lost": has_lost
    }
    return render(request, 'game/raid-play.html', context)


def raidAttack(request):
    pk = request.GET.get('pk')
    raid = getRaid(pk)
    if not raid:
        return redirect('game-raid')
    uid = request.user.userID
    mID = request.GET.get('mID')
    if uid == raid['user1'] and raid['health1'] != 0:
        raid['move1'] = mID
    elif uid == raid['user2'] and raid['health2'] != 0:
        raid['move2'] = mID
    elif uid == raid['user3'] and raid['health3'] != 0:
        raid['move3'] = mID
    updateRaid(raid)
    return redirect('game-raid-play')
