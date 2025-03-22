from channels.generic.websocket import AsyncWebsocketConsumer
import json

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_group = self.scope['url_route']['kwargs']['game_group']
        await self.accept()

        await self.channel_layer.group_add(self.game_group, self.channel_name)
        print(f"Player connected to game group {self.game_group}: {self.channel_name}")

        game_ready_message = json.dumps({
            "action": "game_ready",
            "message": "Game is Ready!"
        })

        await self.channel_layer.group_send(
            self.game_group,
            {
                "type":"send_ready_message",
                "text": game_ready_message,
            }
        )


    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.game_group, self.channel_name)
        print(f"Player disconnected from game group {self.game_group}: {self.channel_name}")

    async def send_ready_message(self,event):
        ready_message = event["text"]
        await self.send(text_data=ready_message)

