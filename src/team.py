from configuration import Configuration
from enum import Enum
from sqlalchemy import Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db
from score import Score


class Team(db.Model):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    player1_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    player2_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=True)

    players = relationship('Player', foreign_keys=player1_id, back_populates='teams')
    red_team_games = relationship('Foosball_game', foreign_keys='foosball_games.red_team_id', back_populates='red_team')
    black_team_games = relationship('Foosball_game', foreign_keys='foosball_games.black_team_id', back_populates='black_team')
    scores = relationship('Score', back_populates='team')


    def __init__(self):
        pass
        # self.player1 = None
        # self.player2 = None
        # self.score = 0

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
