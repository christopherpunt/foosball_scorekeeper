from configuration import Configuration
from flask import jsonify
from enum import Enum
from tinydb import TinyDB, Query
from datetime import datetime


class TeamEnum(Enum):
    RED = 'RED'
    BLACK = 'BLACK'

class FoosballGame:

    def __init__(self, redPlayer1, blackPlayer1, redPlayer2 = None, blackPlayer2 = None):
        self.redPlayer1 = redPlayer1
        self.redPlayer2 = redPlayer2
        self.blackPlayer1 = blackPlayer1
        self.blackPlayer2 = blackPlayer2
        self.blackTeamScore = 0
        self.redTeamScore = 0
        self.winningTeam = None
        self.isFinished = False

        self.db = TinyDB('instance/FoosballGames.json')

    def addScore(self, team):
        # if self.isFinished():
        #     print('game already finished, cannot change score')
        #     return jsonify({'success': False, 'message': 'game already finished, cannot change score'})

        scoreAdded = False
        if (team == TeamEnum.BLACK.name) and self.blackTeamScore < Configuration.gameWinningAmount:
            self.blackTeamScore += 1
            scoreAdded = True
            return jsonify({'success': True})
        elif (team == TeamEnum.RED.name) and self.redTeamScore < Configuration.gameWinningAmount:
            self.redTeamScore += 1
            return jsonify({'success': True})    
        
        if not scoreAdded:
            print(f'score for {team} could not be added')
            return jsonify({'success': False, 'message': f'could not add score for {team}'})
    
    def removeScore(self, team):
        if (team == TeamEnum.BLACK.name) and self.blackTeamScore > 0:
            self.blackTeamScore -= 1
        elif (team == TeamEnum.RED.name) and self.redTeamScore > 0:
            self.redTeamScore -= 1      
        else:
            print(f'could not remove score from {team}')

    def isGameFinished(self):
        if self.blackTeamScore >= Configuration.gameWinningAmount:
            self.winningTeam = TeamEnum.BLACK
            self.isFinished = True
        elif self.redTeamScore >= Configuration.gameWinningAmount:
            self.winningTeam = TeamEnum.RED
            self.isFinished = True

        if self.isFinished:
            saveData = self.getGameData()
            self.db.insert(saveData)
        
        return self.isFinished

    def getGameData_old(self):
        return vars(self)

    def getGameData(self):
        return {
            'redTeam': {
                'players': [
                    self.redPlayer1.username if self.redPlayer1 else None,
                    self.redPlayer2.username if self.redPlayer2 else None,
                ],
                'score': self.redTeamScore
            },
            'blackTeam': {
                'players': [
                    self.blackPlayer1.username if self.blackPlayer1 else None,
                    self.blackPlayer2.username if self.blackPlayer2 else None,
                ],
                'score': self.blackTeamScore
            },
            'finished': self.isFinished,
            'finishDate': datetime.now().strftime('%d/%m/%Y, %I:%M%p'),
            'winningTeam': self.winningTeam.name if self.winningTeam else None
        }


class FoosballGameManager:
    currentGame = None

    def __init__(self, socketio) -> None:
        self.socketio = socketio
    
    def startGame(self, redSelectedPlayers, blackSelectedPlayers):

        #player1 should never be None, need to check if player2 exists, otherwise set as None
        if len(redSelectedPlayers) == 2:
            redPlayer2 = redSelectedPlayers[1]
        else:
            redPlayer2 = None
        if len(blackSelectedPlayers) == 2:
            blackPlayer2 = blackSelectedPlayers[1]
        else:
            blackPlayer2 = None

        self.currentGame = FoosballGame(redPlayer1=redSelectedPlayers[0], blackPlayer1=blackSelectedPlayers[0], redPlayer2=redPlayer2, blackPlayer2=blackPlayer2)
    
    def updateCurrentGameData(self):
        if self.currentGame is not None:
            self.currentGame.isGameFinished()
            self.socketio.emit('update_game', self.currentGame.getGameData())