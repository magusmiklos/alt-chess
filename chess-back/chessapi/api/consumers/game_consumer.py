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

        await self.create_board()
        order = GameConsumer.players_by_group[self.game_group][self.channel_name]
        print(f"sending order player: {self.channel_name} , order: {order}")
        await self.send(json.dumps(
            {
                "type": "send_ready_message",
                "action": "game_ready",
                "board": GameConsumer.players_by_group[self.game_group]["board"],
                "order": order,
            })
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.game_group, self.channel_name)
        
        if (self.game_group in GameConsumer.players_by_group and
                self.channel_name in GameConsumer.players_by_group[self.game_group]):
            del GameConsumer.players_by_group[self.game_group][self.channel_name]
        
        print(f"Player disconnected from game group {self.game_group}: {self.channel_name}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get("action")

        if action == "move":
            move_from = text_data_json.get("move")[0]
            move_to = text_data_json.get("move")[1]

            if not (0 <= move_from[0] < 8 and 0 <= move_from[1] < 8 and 0 <= move_to[0] < 8 and 0 <= move_to[1] < 8):
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Invalid move coordinates."
                }))
                return

            await self.make_move_on_board(move_from, move_to)

            # Broadcast updated board state to all connected clients in the game group
            await self.channel_layer.group_send(
                self.game_group,
                {
                    "type": "send_game_state",
                    "board": GameConsumer.players_by_group[self.game_group]["board"],
                }
            )
            print("a move was made")

    async def create_board(self):
        # Initialize the board
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
        
        if "board" not in GameConsumer.players_by_group[self.game_group]:
            GameConsumer.players_by_group[self.game_group]["board"] = board
        
        GameConsumer.players_by_group[self.game_group]["turn"] = True

    async def assign_player_order(self):
        group_players = GameConsumer.players_by_group[self.game_group]
    
        if not group_players:
            group_players[self.channel_name] = random.choice([True, False])
            print("assigning the first player")
        else:
            first_value = next(iter(group_players.values()))
            group_players[self.channel_name] = not first_value
            print("assigning the second player", group_players)

    async def make_move_on_board(self, move_from, move_to):
        board = GameConsumer.players_by_group[self.game_group]["board"]

        # Make the move on the board
        board[move_from[0]][move_from[1]], board[move_to[0]][move_to[1]] = \
            board[move_to[0]][move_to[1]], board[move_from[0]][move_from[1]]

        # Toggle the turn after the move
        GameConsumer.players_by_group[self.game_group]["turn"] = not GameConsumer.players_by_group[self.game_group]["turn"]

    async def send_game_state(self, event):
        board = GameConsumer.players_by_group[self.game_group]["board"]
        
        # Broadcast the new board state to all connected clients in the game group
        await self.send(text_data=json.dumps({
            "type": "game_state_update",
            "action":"board_update",
            "board": board,
        }))

