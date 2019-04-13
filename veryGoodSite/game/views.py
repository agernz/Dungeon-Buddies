from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from game.forms.GuildForm import GuildForm
from game.forms.InviteForm import InviteForm
from django.http import JsonResponse
import math
from game.sql import (
    getUserInfo, leaveGuild, getGuildInvites, getGuildMembers, getGuildRank,
    getTop100, getUserRank, getUserGuild, getTop100Guilds, createNewGuild,
    sendGuildInvite, joinGuildMember, sendRaidInvite, getRaidInvites,
    createRaid, getRaidStatus, getRaid, getMonsters, getPartyNames,
    generateMonsters, noMonsters
)


# TODO delete old invites, maybe remove time?
NUM_LEVELS = 5


def index(request):
    if request.user.is_authenticated:
        return render(request, 'game/index.html',
                      {"userInfo": getUserInfo(request.user.userID,
                                               request.user.username)})
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
    user = getUserInfo(request.user.userID, request.user.username)
    context = {}

    if user:
        context['characterName'] = user['charName']
        context['experience'] = user['exp']
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
    # TODO allow user to delete raid on this page
    if request.method == "POST":
        level = request.POST.get("level", None)
        partner1 = request.POST.get("partner1", None)
        partner2 = request.POST.get("partner2", None)
        context = {
                "level": level,
                "partners": [partner1, partner2],
                "is_owner": True
            }
        if partner1 != "undefined":
            sendRaidInvite(request.user.userID, partner1)
        if partner2 != "undefined":
            sendRaidInvite(request.user.userID, partner2)

        uInfo = getUserInfo(request.user.userID, request.user.username)
        if createRaid(request.user.userID, level, uInfo["health"]):
            return render(request, 'game/raid-staging.html', context)
        else:
            messages.warning(request, "Could not create Raid")
            return redirect('game-raid')

    else:
        raid = getRaid(request.user.userID)
        # TODO get other players, show status
        context = {
            "level": raid['raidLevel'],
            "partners": [None, None],
            "is_owner": request.user.userID == raid['user1']
        }
        return render(request, 'game/raid-staging.html', context)


@login_required
def raidPlay(request):
    # TODO error handling
    raid = getRaid(request.user.userID)
    pk = raid['user1']
    if noMonsters(pk):
        generateMonsters(pk, raid['raidLevel'])
    this_user = request.user.userID
    party = []
    userIDs = [raid['user1'], raid['user2'], raid['user3']]
    userHealth = [raid['health1'], raid['health2'], raid['health3']]
    userMoves = [raid['move1'], raid['move2'], raid['move3']]
    no_move = False
    for i, name, health, move in zip(userIDs, getPartyNames(userIDs),
                                     userHealth, userMoves):
        if this_user == i and move is None:
            no_move = True
        party.append({
            "name": name,
            "health": health,
            "no_move": move is None,
        })
    context = {
        "monsters": getMonsters(pk),
        "party": party,
        "no_move": no_move
    }

    return render(request, 'game/raid-play.html', context)


def raidAttack(request):
    # TODO insert move into raid table
    return None
