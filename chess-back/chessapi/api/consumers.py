from channels.generic.websocket import AsyncWebsocketConsumer
import json

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Perform any cleanup here if necessary
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        # Echo the message back to the client
        await self.send(text_data=json.dumps({'message': message}))
