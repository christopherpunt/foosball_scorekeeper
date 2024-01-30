from tournament import *
import pytest

def test_valid_tournament_creation():
    players = ["Player1", "Player2", "Player3", "Player4"]
    manager = TournamentManager()
    assert manager.newTournament(players) is True
    assert manager.currentTournament is not None
    round1Matches = manager.currentTournament.matches.get(1, None)
    assert round1Matches is not None
    assert len(round1Matches) == 1
    round1Matches[0].assignRandomWinner()

def test_invalid_tournament_creation():
    players = ["Player1", "Player2"]
    manager = TournamentManager()
    assert manager.newTournament(players) is False
    assert manager.currentTournament is None

def test_tournament_3Teams():
    players = ["Player1", "Player2", "Player3", "Player4", "Player5", "Player6"]
    tournament = Tournament(players)

    # Assert that the number of matches is correct for each round
    assert len(tournament.matches.get(1)) == 2

def test_tournament_4Teams():
    players = ["Player1", "Player2", "Player3", "Player4", "Player5", "Player6", "Player7", "Player8"]
    tournament = Tournament(players)

    # Assert that the number of matches is correct for each round
    assert len(tournament.matches.get(1)) == 2

def test_team_creation():
    player1 = "Player1"
    player2 = "Player2"
    team = Team(player1, player2)
    assert team.players == (player1, player2)
