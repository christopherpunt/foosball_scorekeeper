from configuration import Configuration
from team import Team, TeamEnum
from flask import jsonify
from sqlalchemy import Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import db


class FoosballGame(db.Model):
    __tablename__ = 'foosball_games'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    startDate: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    finishDate: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    red_team_id: Mapped[int] = mapped_column(Integer, ForeignKey('teams.id'))
    black_team_id: Mapped[int] = mapped_column(Integer, ForeignKey('teams.id'))
    winning_team: Mapped[int] = mapped_column(Integer, ForeignKey('teams.id'))

    red_team = relationship('Team',foreign_keys=[red_team_id], back_populates='red_team_games')
    black_team = relationship('Team',foreign_keys=[black_team_id], back_populates='black_team_games')
    scores = relationship('Score', back_populates='foosball_game')

    def __init__(self):
        pass
        # self.blackTeam = Team(TeamEnum.BLACK)
        # self.redTeam = Team(TeamEnum.RED)
        # self.winningTeam = None

    def addScore(self, team):
        if self.isFinished():
            print('game already finished, cannot change score')
            return jsonify({'success': False, 'message': 'game already finished, cannot change score'})

        if (team == TeamEnum.BLACK.name):
            self.blackTeam.addScore()
            return jsonify({'success': True})    
        elif (team == TeamEnum.RED.name):
            self.redTeam.addScore()
            return jsonify({'success': True})    
        else:
            print(f'addScore(): team: {team} does not exist')
            return jsonify({'success': False, 'message': f'addScore(): team: {team} does not exist'})
    
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


class FoosballGameManager:
    currentGame = None

    def __init__(self, socketio) -> None:
        self.socketio = socketio
        self.currentGame = FoosballGame()

    def newGame(self):
        self.currentGame = FoosballGame()
    
    def isCurrentGameReady(self):
        return self.currentGame.isGameReady()
        
    def updateCurrentGameData(self):
        self.socketio.emit('update_game', self.currentGame.getGameData())