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
        self.blackPlayer1 = blackPlayer1
        self.redPlayer2 = redPlayer2
        self.blackPlayer2 = blackPlayer2
        self.blackTeamScore = 0
        self.redTeamScore = 0
        self.winningTeam = None
        self.isFinished = False
        self.startTime = datetime.now().strftime(Configuration.dateFormat)

        self._db = TinyDB(Configuration.foosballGamesDatabase, indent=2)

    def addScore(self, team):
        if self.isFinished:
            print('game already finished, cannot change score')
            return jsonify({'success': False, 'message': 'game already finished, cannot change score'})

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
            if self.isFinished:
                self.isFinished = False
        elif (team == TeamEnum.RED.name) and self.redTeamScore > 0:
            self.redTeamScore -= 1      
            if self.isFinished:
                self.isFinished = False
        else:
            print(f'could not remove score from {team}')

    def isGameFinished(self):
        if self.blackTeamScore >= Configuration.gameWinningAmount:
            self.winningTeam = TeamEnum.BLACK.name
            self.isFinished = True
        elif self.redTeamScore >= Configuration.gameWinningAmount:
            self.winningTeam = TeamEnum.RED.name
            self.isFinished = True

        return self.isFinished

    def getGameData(self):
        gameData = vars(self)
        gameData['finishTime'] = datetime.now().strftime(Configuration.dateFormat) if self.isFinished else None
        return {key: value for key, value in gameData.items() if not key.startswith('_')}

class FoosballGameManager:
    currentGame = None

    def __init__(self, socketio) -> None:
        self.socketio = socketio
    
    def startGame(self, redSelectedPlayers, blackSelectedPlayers):
        # Check for uniqueness of players in both teams
        allPlayers = redSelectedPlayers + blackSelectedPlayers
        if len(set(allPlayers)) == len(allPlayers):
            # Check for the required number of players in each team
            if 1 <= len(redSelectedPlayers) <= 2 and 1 <= len(blackSelectedPlayers) <= 2:
                redPlayer1 = redSelectedPlayers[0]
                redPlayer2 = redSelectedPlayers[1] if len(redSelectedPlayers) == 2 else None

                blackPlayer1 = blackSelectedPlayers[0]
                blackPlayer2 = blackSelectedPlayers[1] if len(blackSelectedPlayers) == 2 else None

                self.currentGame = FoosballGame(redPlayer1=redPlayer1, blackPlayer1=blackPlayer1, redPlayer2=redPlayer2, blackPlayer2=blackPlayer2)
                return jsonify({'success': True, 'message': 'Game Started'})

        return jsonify({'success': False, 'message': 'Could not start game, teams not ready or players not unique'})

    def updateCurrentGameData(self):
        if self.currentGame is not None:
            self.currentGame.isGameFinished()
            self.socketio.emit('update_game', self.currentGame.getGameData())

    def gameCompleted(self):
        if self.currentGame.isFinished:
            saveData = self.currentGame.getGameData()
            self.currentGame._db.insert(saveData)
        self.currentGame = None

    def getRedPlayers(self):
        if self.currentGame is not None:
            return [player for player in [self.currentGame.redPlayer1, self.currentGame.redPlayer2] if player is not None]

    def getBlackPlayers(self):
        if self.currentGame is not None:
            return [player for player in [self.currentGame.blackPlayer1, self.currentGame.blackPlayer2] if player is not None]
