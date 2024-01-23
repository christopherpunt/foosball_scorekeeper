from tournament import Tournament
import pytest

def test_newTournamentNotEnoughPlayers():
    players = ["player1", "player2"]

    with pytest.raises(ValueError, match="There must be at least 4 players for a tournament"):
        tournament = Tournament(players)
        assert tournament is not None
        assert len(players) == 2  # Ensure the original list remains unchanged
        assert tournament.teams == []  # Ensure no teams are created

def test_newTournament2Teams():
    players = ["player1", "player2", "player3", "player4"]
    tournament = Tournament(players)

    assert len(tournament.teams) == 2

    playersToMatch = []
    for team in tournament.teams:
        assert len(team) == 2
        playersToMatch.append(team[0])
        playersToMatch.append(team[1])

    assert set(players) == set(playersToMatch)


def test_new_tournament_odd_players():
    players = ["player1", "player2", "player3", "player4", "player5"]
    tournament = None  # Initialize the variable outside the with statement

    with pytest.raises(ValueError, match="The number of players must be even to create teams."):
        tournament = Tournament(players)
        assert tournament is not None
        assert len(players) == 5  # Ensure the original list remains unchanged
        assert tournament.teams == []  # Ensure no teams are created