from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid

lobby = []

class MatchmakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        print(self.channel_name)
        lobby.append(self.channel_name)
        print("Player joined lobby:", self.channel_name)
        await self.trymm()

    async def disconnect(self, code):
        if self.channel_name in lobby:
            lobby.remove(self.channel_name)
            print("Player left lobby:", self.channel_name)

    async def trymm(self):
        if len(lobby) >= 2:
            player1 = lobby.pop(0)
            player2 = lobby.pop(0)

            game_group = f"game_{uuid.uuid4().hex}"

            await self.channel_layer.group_add(game_group, player1)
            await self.channel_layer.group_add(game_group, player2)

            match_message = json.dumps({
                "action": "match_found",
                "game_group": game_group,
                "message": "Match Found!"
            })

            await self.channel_layer.group_send(
                game_group,
                {
                    "type":"send_match_message",
                    "text": match_message,
                }
            )
            
            print(f"Matchmaking was successful: player1={player1}, player2={player2}")
        else:
            print("Not enough players in lobby:", len(lobby))

    async def send_match_message(self, event):
        # Send the message to WebSocket client
        match_message = event["text"]
        await self.send(text_data=match_message)

