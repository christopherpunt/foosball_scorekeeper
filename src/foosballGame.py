from configuration import Configuration
from team import Team, TeamEnum


class FoosballGame:

    def __init__(self, socketio):
        self.socketio = socketio
        self.blackTeam = Team(TeamEnum.BLACK)
        self.redTeam = Team(TeamEnum.RED)
        self.winningTeam = None

    def addScore(self, team):
        if self.isFinished():
            print('game already finished, cannot change score')
            return

        if (team == TeamEnum.BLACK.name):
            self.blackTeam.addScore()
        elif (team == TeamEnum.RED.name):
            self.redTeam.addScore()
        else:
            print(f'addScore(): team: {team} does not exist')
        self.updateGameData()
    
    def removeScore(self, team):
        if self.isFinished():
            print('game already finished, cannot change score')
            return
        if (team == TeamEnum.BLACK.name):
            self.blackTeam.removeScore()
        elif (team == TeamEnum.RED.name):
            self.redTeam.removeScore()        
        else:
            print(f'removeScore(): team: {team} does not exist')
        self.updateGameData()

    def removePlayer(self, player):
        if self.blackTeam.removePlayer(player):
            return True
        if self.redTeam.removePlayer(player):
            return True
        return False

    def isGameReady(self):
        if self.blackTeam.isTeamReady() and self.redTeam.isTeamReady():
            return True
        else:
            return False

    def isFinished(self):
        if self.blackTeam and self.blackTeam.getScore() >= Configuration.gameWinningAmount:
            self.winningTeam = self.blackTeam
            return True
        elif self.redTeam and self.redTeam.getScore() >= Configuration.gameWinningAmount:
            self.winningTeam = self.redTeam
            return True
        else:
            return False
        
    def updateGameData(self):
        self.socketio.emit('update_game', self.getGameData())

    def getGameData(self):
        return {
            'redTeam': {
                'players': [
                    self.redTeam.player1.username if self.redTeam.player1 else None,
                    self.redTeam.player2.username if self.redTeam.player2 else None,
                ],
                'score': self.redTeam.score
            },
            'blackTeam': {
                'players': [
                    self.blackTeam.player1.username if self.blackTeam.player1 else None,
                    self.blackTeam.player2.username if self.blackTeam.player2 else None,
                ],
                'score': self.blackTeam.score
            },
            'finished': self.isFinished(),
            'winningTeam': self.winningTeam.side.name if self.winningTeam else None
        }
    
    def reset(self):
        self.blackTeam.reset()
        self.redTeam.reset()
        self.winningTeam = None
