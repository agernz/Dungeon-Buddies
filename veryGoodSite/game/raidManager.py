from channels.generic.websocket import WebsocketConsumer
import json


class RaidManager(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        pk = data['pk']
        message = data['events']

        self.send(text_data=json.dumps({
            'pk': pk,
            'message': message
        }))
