from foosballGame import FoosballGame, FoosballGameManager
from configuration import Configuration
from unittest.mock import Mock
from testConfiguration import TestConfiguration
from tinydb import TinyDB
import pytest
import os

@pytest.fixture(scope="class")
def test_database(request):
    # Create the file once for the entire test class
    db_path = TestConfiguration.foosballGamesDatabase
    with open(db_path, 'w') as file:
        pass  # Empty file

    # Provide the database path to the tests
    request.cls.db_path = db_path

    yield db_path  # This is the value returned by the fixture

    # Delete the file after all tests in the class have run
    os.remove(db_path)

@pytest.fixture
def mock_socketio():
    return Mock()

@pytest.fixture
def foosballGameManager(mock_socketio):
    with TestConfiguration():
        yield FoosballGameManager(mock_socketio)

@pytest.fixture(autouse=True)
def setup_teardown_test_database(request):
    # Truncate the file between individual tests
    db_path = TestConfiguration.foosballGamesDatabase
    with TinyDB(db_path, indent=2) as db:
        db.truncate()


@pytest.fixture
def game():
    return FoosballGame("player1", "player2")

def test_addScoreFrom0(game):
    assert game.redTeamScore == 0
    assert game.blackTeamScore == 0

    result = game.addScore('RED')
    assert game.redTeamScore == 1
    assert game.blackTeamScore == 0
    assert result == True

    result = game.addScore('BLACK')
    assert game.redTeamScore == 1
    assert game.blackTeamScore == 1
    assert result == True

def test_addScorefromNon0(game):
    game.redTeamScore = 4
    game.blackTeamScore = 3

    result = game.addScore('RED')
    assert game.redTeamScore == 5
    assert game.blackTeamScore == 3
    assert result == True

    result = game.addScore('BLACK')
    assert game.redTeamScore == 5
    assert game.blackTeamScore == 4
    assert result == True

def test_addScoreOverWinningAmount(game):
    game.redTeamScore = Configuration.gameWinningAmount
    game.blackTeamScore = Configuration.gameWinningAmount

    result = game.addScore('RED')
    assert game.redTeamScore == Configuration.gameWinningAmount
    assert game.blackTeamScore == Configuration.gameWinningAmount
    assert result == False

    result = game.addScore('BLACK')
    assert game.redTeamScore == Configuration.gameWinningAmount
    assert game.blackTeamScore == Configuration.gameWinningAmount
    assert result == False

def test_removeScoreAlready0(game):
    result = game.removeScore('RED')
    assert game.redTeamScore == 0
    assert result == False

    result = game.removeScore('BLACK')
    assert game.blackTeamScore == 0
    assert result == False

def test_removeScore(game):
    game.redTeamScore = 2
    game.blackTeamScore = 1

    result = game.removeScore('RED')
    assert game.redTeamScore == 1
    assert result == True

    result = game.removeScore('BLACK')
    assert game.blackTeamScore == 0
    assert result == True

def test_removeScoreOverGameWinning(game):
    game.redTeamScore = Configuration.gameWinningAmount + 1
    game.blackTeamScore = Configuration.gameWinningAmount + 1

    result = game.removeScore('RED')
    assert game.redTeamScore == Configuration.gameWinningAmount
    assert result == True

    result = game.removeScore('BLACK')
    assert game.blackTeamScore == Configuration.gameWinningAmount
    assert result == True

def test_isFinishedUnderWinningAmount(game):
    game.blackTeamScore = Configuration.gameWinningAmount - 1
    assert game.isGameFinished() == False
    assert game.isFinished == False

    game.redTeamScore = Configuration.gameWinningAmount - 1
    assert game.isGameFinished() == False
    assert game.isFinished == False

def test_isFinishedMatchingWinningAmount(game):
    game.blackTeamScore = Configuration.gameWinningAmount
    assert game.isGameFinished() == True
    assert game.isFinished == True

    game = FoosballGame("player1", "player2")
    assert game.isFinished == False
    game.redTeamScore = Configuration.gameWinningAmount
    assert game.isGameFinished() == True
    assert game.isFinished == True


def test_isFinishedOverWinningAmount(game):
    game.blackTeamScore = Configuration.gameWinningAmount + 1
    assert game.isGameFinished() == True
    assert game.isFinished == True

    game = FoosballGame("player1", "player2")
    assert game.isFinished == False
    game.redTeamScore = Configuration.gameWinningAmount + 1
    assert game.isGameFinished() == True
    assert game.isFinished == True

def test_startGameWith4UniquePlayers(foosballGameManager):
    redPlayers = ["Player1", "Player2"]
    blackPlayers = ["Player3", "Player4"]

    result = foosballGameManager.startGame(redPlayers, blackPlayers)
    assert result == True

def test_startGameWith2UniquePlayers(foosballGameManager):
    redPlayers = ["Player1"]
    blackPlayers = ["Player2"]

    result = foosballGameManager.startGame(redPlayers, blackPlayers)
    assert result == True

def test_startGameWith3UniquePlayers(foosballGameManager):
    redPlayers = ["Player1"]
    blackPlayers = ["Player2", "Player3"]

    result = foosballGameManager.startGame(redPlayers, blackPlayers)
    assert result == True

def test_startGameNotEnoughPlayers(foosballGameManager):
    redPlayers = []
    blackPlayers = ["Player2"]

    result = foosballGameManager.startGame(redPlayers, blackPlayers)
    assert result == False


def test_startGame2SamePlayersSameTeam(foosballGameManager):
    redPlayers = ["Player1", "Player1"]
    blackPlayers = ["Player2"]

    result = foosballGameManager.startGame(redPlayers, blackPlayers)
    assert result == False

def test_startGame2SamePlayersDifferentTeam(foosballGameManager):
    redPlayers = ["Player1", "Player2"]
    blackPlayers = ["Player2"]

    result = foosballGameManager.startGame(redPlayers, blackPlayers)
    assert result == False

def test_startGame3Players1Team(foosballGameManager):
    redPlayers = ["Player1", "Player2", "Player3"]
    blackPlayers = ["Player4"]

    result = foosballGameManager.startGame(redPlayers, blackPlayers)
    assert result == False