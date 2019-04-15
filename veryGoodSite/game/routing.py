from django.conf.urls import url
from game.raidManager import RaidManager, RaidStageManager

websocket_urlpatterns = [
    url(r'^ws/raid/(?P<rID>\d+)/$', RaidManager),
    url(r'^ws/raid-stage/(?P<rID>\d+)/$', RaidStageManager),
]
