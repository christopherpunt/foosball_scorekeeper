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
        self._db = TinyDB('instance/players.json')

    def getAllPlayers(self):
        players = []
        for player_data in self._db.all():
            players.append(Player(**player_data))
        return players

    def updatePlayerData(self):
        self.socketio.emit("update_players", self.getAllowedPlayerData())

    def getAllowedPlayerData(self):
        players = self.getAllPlayers()
        
        allowedRedTeamPlayers = [player.username for player in players if player.username not in [p.username for p in self.redSelectedPlayers] and player.username not in [p.username for p in self.blackSelectedPlayers]]
        allowedBlackTeamPlayers = [player.username for player in players if player.username not in [p.username for p in self.redSelectedPlayers] and player.username not in [p.username for p in self.blackSelectedPlayers]]

        return {
            'redTeamPlayers': [player.username for player in self.redSelectedPlayers],
            'allowedRedTeamPlayers': allowedRedTeamPlayers,

            'blackTeamPlayers': [player.username for player in self.blackSelectedPlayers],
            'allowedBlackTeamPlayers': allowedBlackTeamPlayers
        }

    def updatePlayers(self, request):
        data = request

        if 'team' in data and 'playerName' in data and 'isChecked' in data:
            team = data['team']
            playerName = data['playerName']
            checked = data['isChecked']
            if checked == True:
                if team == 'red':
                    self.addSelectedPlayer(self.findExistingPlayer(playerName), TeamEnum.RED)
                elif team == 'black':
                    self.addSelectedPlayer(self.findExistingPlayer(playerName), TeamEnum.BLACK)
            else:
                self.removeSelectedPlayer(self.findExistingPlayer(playerName))

        self.updatePlayerData()
        return jsonify({'success': True})    

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
            self.updatePlayerData()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': f'User: {newUser} already exists'})

    def addSelectedPlayer(self, player, team):
        if player is None:
            return False

        player_added = False
        if team == TeamEnum.BLACK and len(self.blackSelectedPlayers) <= 2:
            self.blackSelectedPlayers.append(player)
            player_added = True
        elif team == TeamEnum.RED and len(self.redSelectedPlayers) <= 2:
            self.redSelectedPlayers.append(player)
            player_added = True
        else:
            print(f'Team: {team} not recognized')

        if player_added:
            print(f"User '{player.username}' joined the game on the '{team}' side.")
            return True
        return False
    
    def clearSelectedPlayers(self):
        self.redSelectedPlayers = []
        self.blackSelectedPlayers = []
    
    def areSelectedPlayersReady(self):
        if len(self.redSelectedPlayers) > 0 and len(self.blackSelectedPlayers) > 0:
            return True
    
    def getRedTeamSelectedPlayers(self):
        return self.redSelectedPlayers
    
    def getBlackTeamSelectedPlayers(self):
        return self.blackSelectedPlayers
    
    def removeSelectedPlayer(self, player):
        if player in self.blackSelectedPlayers:
            self.blackSelectedPlayers.remove(player)
        if player in self.redSelectedPlayers:
            self.redSelectedPlayers.remove(player)