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

        async_to_sync(self.channel_layer.group_send)(
            self.raid_name,
            {
                'type': 'raid_upates',
                'events': events
            }
        )

    def raidData(self, event):
        events = event['events']

        self.send(text_data=json.dumps({
            'events': events
        }))
