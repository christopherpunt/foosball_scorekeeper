from flask import jsonify
from foosballGame import TeamEnum
from database import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class Player(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=True)

class PlayerManager:

    def __init__(self, socketio) -> None:
        self.socketio = socketio

    def getAllPlayers(self):
        return db.session.execute(db.select(Player).order_by(Player.username)).scalars().all()

    def updatePlayerData(self, currentGame):
        self.socketio.emit("update_players", self.getAllowedPlayerData(currentGame))

    def getAllowedPlayerData(self, currentGame):
        players = self.getAllPlayers()

        redTeamPlayers = []
        if currentGame.redTeam.player1 is not None:
            redTeamPlayers.append(currentGame.redTeam.player1.username)
        if currentGame.redTeam.player2 is not None:
            redTeamPlayers.append(currentGame.redTeam.player2.username)

        blackTeamPlayers = []
        if currentGame.blackTeam.player1 is not None:
            blackTeamPlayers.append(currentGame.blackTeam.player1.username)
        if currentGame.blackTeam.player2 is not None:
            blackTeamPlayers.append(currentGame.blackTeam.player2.username)
        
        allowedRedTeamPlayers = [ player.username for player in players if player.username not in redTeamPlayers and player.username not in blackTeamPlayers ]
        allowedBlackTeamPlayers = [ player.username for player in players if player.username not in redTeamPlayers and player.username not in blackTeamPlayers ]

        return {
            'redTeamPlayers': redTeamPlayers,
            'allowedRedTeamPlayers': allowedRedTeamPlayers,

            'blackTeamPlayers': blackTeamPlayers,
            'allowedBlackTeamPlayers': allowedBlackTeamPlayers
        }

    def updatePlayers(self, request, currentGame):
        data = request

        if 'team' in data and 'playerName' in data and 'isChecked' in data:
            team = data['team']
            playerName = data['playerName']
            checked = data['isChecked']
            if checked == True:
                if team == 'red':
                    self.addPlayerToTeam(self.findExistingPlayer(playerName), TeamEnum.RED, currentGame)
                elif team == 'black':
                    self.addPlayerToTeam(self.findExistingPlayer(playerName), TeamEnum.BLACK, currentGame)
            else:
                self.removePlayerFromGame(self.findExistingPlayer(playerName), currentGame)

        self.updatePlayerData(currentGame)
        return jsonify({'success': True})    

    def findExistingPlayer(self, plaerName):
        foundPlayer = db.session.execute(db.select(Player).where(Player.username == plaerName)).scalar()
        if foundPlayer is not None:
            return foundPlayer

    def addNewPlayer(self, request, currentGame):
        data = request.get_json()
        if 'newUser' not in data:
            print(f'newUser does not exist in data from request')
            return jsonify({'success': False, 'message': 'Something went wrong'})
        
        newUser = data['newUser']
        if newUser is None or newUser == '':
            print(f'cannot create user {newUser}')
            return jsonify({'success': False, 'message': 'Something went wrong'})
        
        foundPlayer = db.session.execute(db.select(Player).where(Player.username == newUser)).first()
        if foundPlayer is None:
            player = Player(username=newUser)
            db.session.add(player)
            db.session.commit()
            self.updatePlayerData(currentGame)
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Something went wrong'})

    def addPlayerToTeam(self, player, team, currentGame):
        if player is None:
            return False

        player_added = False
        if team == TeamEnum.BLACK:
            player_added = currentGame.blackTeam.addPlayer(player)
        elif team == TeamEnum.RED:
            player_added = currentGame.redTeam.addPlayer(player)
        else:
            print(f'Team: {team} not recognized')

        if player_added:
            print(f"User '{player.username}' joined the game on the '{team}' side.")
            currentGame.updateGameData()
            return True
        return False
    
    def removePlayerFromGame(self, playerName, currentGame):
        currentGame.removePlayer(playerName)