from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='game-index'),
    path('guild/', views.guildPage, name='game-guild'),
    path('guild-create/', views.createGuild, name='game-guild-create'),
    path('guild-invite/', views.guildInvite, name='game-guild-invite'),
    path('guild-join/', views.joinGuild, name='game-guild-join'),
    path('raid/', views.raidPage, name='game-raid'),
    path('raid-stage/', views.raidStage, name='game-raid-stage'),
    path('raid-get-invites/', views.raidGetInvites,
         name='game-raid-get-invites'),
    re_path(r'^raid-dungeon/(?P<rID>\d+)/$', views.raidRender,
            name='game-raid-render'),
    path('raid-dungeon-update/', views.raidUpdate, name='game-raid-update'),
    path('stats/', views.statsPage, name='game-stats'),
    path('raid-join/', views.joinRaid,
         name='game-raid-join'),
]
