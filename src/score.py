from database import db
from sqlalchemy import Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Score(db.Model):
    __tablename__ = 'scores'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    foosball_game_id: Mapped[int] = mapped_column(Integer, ForeignKey('foosball_games.id'))
    scorer_id: Mapped[int] = mapped_column(Integer, ForeignKey('players.id'))
    score_time: Mapped[DateTime] = mapped_column(DateTime)

    foosball_game = relationship('FoosballGame', back_populates='scores')
