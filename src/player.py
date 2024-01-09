from flask import jsonify
from foosballGame import TeamEnum
from tinydb import TinyDB, Query
import re


class Player:
    def __init__(self, username) -> None:
        self.username = username

    def __eq__(self, other) -> bool:
        return self.username == other.username 

class PlayerManager:
    def __init__(self, socketio) -> None:
        self.socketio = socketio
        self.redSelectedPlayers = []
        self.blackSelectedPlayers = []
        self._db = TinyDB('instance/players.json', indent=2)

    def getAllPlayers(self):
        players = []
        for player_data in self._db.all():
            players.append(Player(**player_data))
        return sorted(players, key=lambda x: (x.username.lower()))

    def findExistingPlayer(self, playerName):
        User = Query()
        results = self._db.search(User.username.matches(playerName, flags=re.IGNORECASE))

        if len(results) == 1:
            return Player(**results[0])
        return None

    def addNewPlayer(self, request):
        data = request.get_json()
        if 'newUser' not in data:
            print(f'newUser does not exist in data from request')
            return jsonify({'success': False, 'message': 'newUser does not exist in data from request'})
        
        newUser = data['newUser']
        if newUser is None or newUser == '':
            print(f'cannot create user {newUser}')
            return jsonify({'success': False, 'message': f'cannot create user {newUser}'})
        
        foundPlayer = self.findExistingPlayer(newUser)

        if foundPlayer is None:
            player = Player(username=newUser)
            self._db.insert(vars(player))
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': f'User: {newUser} already exists'})
