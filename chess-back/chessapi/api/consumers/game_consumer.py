from channels.generic.websocket import AsyncWebsocketConsumer
import json

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_group = self.scope['url_route']['kwargs']['game_group']
        await self.accept()

        await self.channel_layer.group_add(self.game_group, self.channel_name)
        print(f"Player connected to game group {self.game_group}: {self.channel_name}")

        board = await self.CreateBoard(8)

        await self.channel_layer.group_send(
            self.game_group,
            {
                "type":"send_ready_message",
                "action":"game_ready",
                "board":board,
            }
        )


    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.game_group, self.channel_name)
        print(f"Player disconnected from game group {self.game_group}: {self.channel_name}")

    async def send_ready_message(self,event):
        action = event["action"]
        board = event["board"]
        await self.send(text_data=json.dumps({
            "action":action,
            "board":board
        }))

    async def CreateBoard(self, num):
        board = [[["K"],["N"],["N"],["N"],["N"],["N"],["N"],["K"]],
                 [["N"],["N"],["N"],["N"],["N"],["N"],["N"],["N"]],
                 [["N"],["N"],["N"],["N"],["N"],["N"],["N"],["N"]],
                 [["N"],["N"],["N"],["N"],["N"],["N"],["N"],["N"]],
                 [["N"],["N"],["P1"],["N"],["N"],["P2"],["N"],["N"]],
                 [["N"],["N"],["N"],["N"],["N"],["N"],["N"],["N"]],
                 [["N"],["N"],["N"],["N"],["N"],["N"],["N"],["N"]],
                 [["K"],["N"],["N"],["N"],["N"],["N"],["N"],["K"]],]

        return board
