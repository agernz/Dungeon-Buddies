from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


class RaidManager(WebsocketConsumer):
    def connect(self):
        self.raid_name = self.scope['url_route']['kwargs']['rID']
        self.raid_name = 'raid_%s' % self.raid_name
        async_to_sync(self.channel_layer.group_add)
        (self.raid_name, self.channel_name)
        self.accept()

    def disconnect(self, info):
        async_to_sync(self.channel_layer.group_discard)
        (self.raid_name, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        events = data['events']
        print('recieve')
        async_to_sync(self.channel_layer.group_send)(
            self.raid_name,
            {
                'type': 'raidData',
                'events': events
            }
        )

    def raidData(self, data):
        print('raidData')
        events = data['events']
        self.send(text_data=json.dumps({
            'events': events
        }))


class RaidStageManager(WebsocketConsumer):
    def connect(self):
        self.raid_name = self.scope['url_route']['kwargs']['rID']
        self.raid_name = 'raid-stage-%s' % self.raid_name
        async_to_sync(self.channel_layer.group_add)(
            self.raid_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, info):
        async_to_sync(self.channel_layer.group_discard)(
            self.raid_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        playerID = data['playerID']
        async_to_sync(self.channel_layer.group_send)(
            self.raid_name,
            {
                'type': 'player_is_ready',
                'playerID': playerID,
            }
        )

    def player_is_ready(self, data):
        playerID = data['playerID']
        self.send(text_data=json.dumps({
            'playerID': playerID
        }))
