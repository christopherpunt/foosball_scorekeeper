from database import db
from sqlalchemy import Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Score(db.Model):
    __tablename__ = 'scores'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    score_time: Mapped[DateTime] = mapped_column(DateTime)
    foosball_game_id: Mapped[int] = mapped_column(Integer, ForeignKey('foosball_games.id'))
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey('players.id'))
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey('teams.id'))
    score: Mapped[int] = mapped_column(Integer, default=0)

    foosball_game = relationship('FoosballGame', back_populates='scores')
    team = relationship('Team', back_populates='scores')

    def __init__(self) -> None:
        super().__init__()