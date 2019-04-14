from django.conf.urls import url
from game.raidManager import RaidManager

websocket_urlpatterns = [
    url('ws/raid/', RaidManager),
]
