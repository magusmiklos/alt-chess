from channels.generic.websocket import AsyncWebsocketConsumer
import json
import random

class GameConsumer(AsyncWebsocketConsumer):
    # Shared across instances for a given game group.
    players_by_group = {}

    async def connect(self):
        self.game_group = self.scope['url_route']['kwargs']['game_group']
        if self.game_group not in GameConsumer.players_by_group:
            GameConsumer.players_by_group[self.game_group] = {}

        await self.accept()
        await self.channel_layer.group_add(self.game_group, self.channel_name)
        print(f"Player connected to game group {self.game_group}: {self.channel_name}")

        await self.assign_player_order()

        board = await self.create_board(8)
        order = GameConsumer.players_by_group[self.game_group][self.channel_name]
        print(f"sending order player: {self.channel_name} , order: {order}")
        await self.send(json.dumps(
            {
                "type": "send_ready_message",
                "action": "game_ready",
                "board": board,
                "order": order,
            })
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.game_group, self.channel_name)
        if (self.game_group in GameConsumer.players_by_group and
                self.channel_name in GameConsumer.players_by_group[self.game_group]):
            del GameConsumer.players_by_group[self.game_group][self.channel_name]
        print(f"Player disconnected from game group {self.game_group}: {self.channel_name}")

    async def create_board(self, num):
        board = [
            [["K"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["K"]],
            [["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"]],
            [["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"]],
            [["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"]],
            [["N"], ["N"], ["P1", 2], ["N"], ["N"], ["P2", 2], ["N"], ["N"]],
            [["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"]],
            [["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"]],
            [["K"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["K"]],
        ]
        return board

    async def assign_player_order(self):
        group_players = GameConsumer.players_by_group[self.game_group]
        if not group_players:
            group_players[self.channel_name] = random.choice([True, False])
            print("assigning the first player")
        else:
            first_value = next(iter(group_players.values()))
            group_players[self.channel_name] = not first_value
            print("assigning the second player",group_players)

