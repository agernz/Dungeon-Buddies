from django.conf.urls import url
from game.raidManager import RaidManager, RaidStageManager, RaidInviteManager

websocket_urlpatterns = [
    url(r'^ws/raid/(?P<rID>\d+)/$', RaidManager),
    url(r'^ws/raid-stage/(?P<rID>\d+)/$', RaidStageManager),
    url(r'^ws/raid-invite/(?P<gID>\d+)/$', RaidInviteManager),
]
