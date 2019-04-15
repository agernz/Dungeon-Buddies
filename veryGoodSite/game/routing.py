from django.conf.urls import url
from game.raidManager import RaidManager

websocket_urlpatterns = [
    url(r'^ws/raid/(?P<rID>\d+)/$', RaidManager),
]
