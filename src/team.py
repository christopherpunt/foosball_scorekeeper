from configuration import Configuration
from enum import Enum


class Team:
    
    def __init__(self, side):
        self.side = side
        self.player1 = None
        self.player2 = None
        self.score = 0

    def getScore(self):
        return self.score

    def addPlayer(self, player):
        if self.player1 is None:
            self.player1 = player
            return True
        elif self.player1 is not None and self.player2 is None:
            self.player2 = player
            return True
        else:
            return False
        
    def removePlayer(self, player):
        if self.player1 is not None and self.player1.username == player.username:
            self.player1 = None
            return True
        elif self.player2 is not None and self.player2.username == player.username:
            self.player2 = None
            return True
        else:
            return False
        
    def isTeamReady(self):
        return self.player1 is not None

    def addScore(self):
        if self.score < Configuration.gameWinningAmount:
            self.score += 1

    def removeScore(self):
        if self.score > 0:
            self.score -= 1


class TeamEnum(Enum):
    RED = 1
    BLACK = 2
