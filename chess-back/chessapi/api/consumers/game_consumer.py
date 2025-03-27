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
            board = GameConsumer.players_by_group[self.game_group]["board"]

            is_move_valid = await self.is_move_valid(text_data_json, board)
            if not is_move_valid:
                await self.send_error_move_message()
                return

            is_move_legal = await self.is_move_legal(text_data_json, board)
            if not is_move_legal:
                await self.send_error_move_message()
                return

            await self.make_move_on_board(text_data_json, board)

            game_state = await self.get_game_state(board)

            # Broadcast updated board state to all connected clients in the game group
            await self.channel_layer.group_send(
                self.game_group,
                {
                    "type": "send_game_state",
                }
            )
            print("a move was made, turn: ", GameConsumer.players_by_group[self.game_group]["turn"])

            if game_state != 0:
                await self.channel_layer.group_send(self.game_group,{"type": "send_game_over","won":game_state})
 

    async def create_board(self):
        if "board" in GameConsumer.players_by_group[self.game_group] and GameConsumer.players_by_group[self.game_group]["board"]:
            return

        # Initialize the board
        board = [
            [["K"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["K"]],
            [["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"]],
            [["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"]],
            [["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"]],
            [["N"], ["P1",1], ["P1",1], ["N"], ["N"], ["P2",1], ["P2",1], ["N"]],
            [["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"]],
            [["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"]],
            [["K"], ["N"], ["N"], ["N"], ["N"], ["N"], ["N"], ["K"]],
        ]
        
        GameConsumer.players_by_group[self.game_group]["board"] = board
        GameConsumer.players_by_group[self.game_group]["kings"] = []
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

    async def make_move_on_board(self, data, board):
        move_from = data.get("move")[0]
        move_to = data.get("move")[1]

        if board[move_from[0]][move_from[1]][0] == "P1" and board[move_to[0]][move_to[1]][0] == "K":
            GameConsumer.players_by_group[self.game_group]["kings"].append(True)
            print("P1 capcured a king")
        if board[move_from[0]][move_from[1]][0] == "P2" and board[move_to[0]][move_to[1]][0] == "K":
            GameConsumer.players_by_group[self.game_group]["kings"].append(False)
            print("P2 capcured a king")

        # Make the move on the board
        board[move_from[0]][move_from[1]], board[move_to[0]][move_to[1]] = \
            ["N"], board[move_from[0]][move_from[1]]

        board[move_to[0]][move_to[1]][1] -= data.get("piece")

        # Toggle the turn after the move
        GameConsumer.players_by_group[self.game_group]["turn"] = not GameConsumer.players_by_group[self.game_group]["turn"]

    async def send_game_state(self, event):
        board = GameConsumer.players_by_group[self.game_group]["board"]
        
        # Broadcast the new board state to all connected clients in the game group
        await self.send(text_data=json.dumps({
            "type": "game_state_update",
            "action":"board_update",
            "board": board,
            "kings": GameConsumer.players_by_group[self.game_group]["kings"],
            "turn": GameConsumer.players_by_group[self.game_group]["turn"],
        }))

    async def send_game_over(self,event):
        await self.send(text_data=json.dumps({
            "action":"game_over",
            "won":event.get("won")
            }))

    async def send_error_move_message(self):
        await self.send(text_data=json.dumps({
            "type": "error",
            "message": "Invalid move."
        }))
        print("invalid move")


    async def is_move_valid(self, data, board):
        turn = GameConsumer.players_by_group[self.game_group]["turn"]

        # It's the other player's turn
        if GameConsumer.players_by_group[self.game_group][self.channel_name] != turn:
            print("it s the other players turn")
            return False

        move = data.get("move")

        if len(move) != 2:
            print("move arr must have len 2")
            return False
        
        from_pos = move[0]  
        to_pos = move[1] 

        if board[from_pos[0]][from_pos[1]][0] == "P1" and not turn:
            print("selected piece P1 and turn is on P2")
            return False

        if board[from_pos[0]][from_pos[1]][0] == "P2" and turn:
            print("selected piece P2 and turn is on P1")
            return False

        if board[from_pos[0]][from_pos[1]][0] not in ["P1", "P2"]:
            print("on the selected square there is no piece")
            return False

        if board[from_pos[0]][from_pos[1]][0] == board[to_pos[0]][to_pos[1]][0]:
            print("from and to is the same pos")
            return False
        
        # if you don't have enough money => invalid move
        if board[from_pos[0]][from_pos[1]][1] < data.get("piece"):
           return False

        # NOTE: Returns true and not checking of move in in the boands of the board
        return True
    async def is_move_legal(self, data, board):
        piece = data.get("piece")
        move = data.get("move")
        from_pos = move[0]
        to_pos = move[1]
    
        #[1] => x [0] => y
        #pawn
        if piece == 0:
            if from_pos[1] == to_pos[1] and from_pos[0]-1 == to_pos[0] and board[to_pos[0]][to_pos[1]][0] == "N":
                return True
            elif abs(from_pos[1] - to_pos[1]) == 1 and from_pos[0]-1 == to_pos[0] and board[to_pos[0]][to_pos[1]][0] != "N":
                return True
        #horse
        elif piece == 1:
            if abs(from_pos[1] - to_pos[1]) == 1 and abs(from_pos[0] - to_pos[0]) == 2:
                return True
            elif abs(from_pos[1] - to_pos[1]) == 2 and abs(from_pos[0] - to_pos[0]) == 1:
                return True
        #bishop
        elif piece == 2:
            if abs(from_pos[0] - to_pos[0]) == abs(from_pos[1] - to_pos[1]):
                dy = 1 if to_pos[0] > from_pos[0] else -1
                dx = 1 if to_pos[1] > from_pos[1] else -1
                
                x,y = from_pos[1]+dx,from_pos[0]+dy

                while [y,x] != to_pos:
                    if board[y][x][0] != "N":
                        print("you can t jump with bishop")
                        return False
                    x += dx
                    y += dy
 
                return True
        #rook
        elif piece == 3:
            if from_pos[0] == to_pos[0]:
                dx = 1 if to_pos[1] > from_pos[1] else -1

                x = from_pos[1] + dx

                while x != to_pos[1]:
                    if board[from_pos[0]][x][0] != "N":
                        print("rook tryed jump 0")
                        return False
                    x += dx
                return True
            elif from_pos[1] == to_pos[1]:
                dy = 1 if to_pos[0] > from_pos[0] else -1

                y = from_pos[0] + dy

                while y != to_pos[0]:
                    if board[y][from_pos[1]][0] != "N":
                        print("rook tryed jump 1")
                        return False
                    y += dy
                return True
 

        return False


    async def get_game_state(self,board):
        if GameConsumer.players_by_group[self.game_group]["kings"].count(True) >= 3:
            return 1
        if GameConsumer.players_by_group[self.game_group]["kings"].count(False) >= 3:
            return 2

        P1_count = 0
        P2_count = 0


        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j][0] == "P1":
                    board[i][j][1] += 1
                    P1_count += 1

                elif board[i][j][0] == "P2":
                    board[i][j][1] += 1
                    P2_count += 1

        if P2_count == 0:
            return 1 
        elif P1_count == 0:
            return 2
        return 0



