from foosballGame import TeamEnum
from tinydb import TinyDB, Query
from configuration import Configuration
import re


class Player:
    def __init__(self, username) -> None:
        self.username = username

    def __eq__(self, other) -> bool:
        return self.username == other.username 

class PlayerManager:
    def __init__(self, socketio) -> None:
        self.socketio = socketio
        self._db = TinyDB(Configuration.playersDatabase, indent=2)

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

    def addNewPlayer(self, newUser):
        if newUser is None or newUser == '':
            print(f'cannot create user {newUser}')
            return False
                
        foundPlayer = self.findExistingPlayer(newUser)

        if foundPlayer is None:
            player = Player(username=newUser)
            self._db.insert(vars(player))
            return True
        
        print(f'User: {newUser} already exists')
        return False
