from player import Player, PlayerManager
from unittest.mock import Mock
from testConfiguration import TestConfiguration
from tinydb import TinyDB
import pytest

@pytest.fixture
def mock_socketio():
    return Mock()

@pytest.fixture
def playerManager(mock_socketio):
    # Use the test configuration in your fixture
    with TestConfiguration():
        yield PlayerManager(mock_socketio)

@pytest.fixture(autouse=True)
def setup_teardown_test_database(request):
    # Truncate the file between individual tests
    db_path = TestConfiguration.playersDatabase
    with TinyDB(db_path, indent=2, create_dirs=True) as db:
        db.truncate()


def test_player_equality_same_username():
    player1 = Player("Username")
    player2 = Player("Username")
    assert player1 == player2

def test_player_equality_different_usernames():
    player1 = Player("Username1")
    player2 = Player("Username2")
    assert player1 != player2

def test_player_equality_with_non_player_object():
    player = Player("Username")
    non_player_object = "NotAPlayer"
    assert player != non_player_object

def test_addNewPlayer_success(playerManager):
    result = playerManager.addNewPlayer("NewPlayer")
    assert result is True

def test_addNewPlayer_duplicate(playerManager):
    # Adding the same player twice should return False
    playerManager.addNewPlayer("Player2")
    result = playerManager.addNewPlayer("Player2")
    assert result is False

def test_findExistingPlayer_existing(playerManager):
    # Adding a player and then finding it should return the Player object
    playerManager.addNewPlayer("ExistingPlayer")
    found_player = playerManager.findExistingPlayer("ExistingPlayer")
    assert found_player is not None
    assert found_player.username == "ExistingPlayer"

def test_findExistingPlayer_nonexistent(playerManager):
    # Trying to find a player that doesn't exist should return None
    found_player = playerManager.findExistingPlayer("NonExistentPlayer")
    assert found_player is None

def test_getAllPlayers_sorted(playerManager):
    # Adding players in a random order, getAllPlayers should return them in sorted order
    playerManager.addNewPlayer("PlayerC")
    playerManager.addNewPlayer("PlayerA")
    playerManager.addNewPlayer("PlayerB")
    players = playerManager.getAllPlayers()
    assert [p.username for p in players] == ["PlayerA", "PlayerB", "PlayerC"]

def test_getAllPlayers_empty(playerManager):
    # When there are no players, getAllPlayers should return an empty list
    players = playerManager.getAllPlayers()
    assert players == []

def test_findExistingPlayer_existing_case_insensitive(playerManager):
    # Adding a player with a different case and then finding it should return the Player object
    playerManager.addNewPlayer("CaseSensitivePlayer")
    found_player = playerManager.findExistingPlayer("casesensitiveplayer")
    assert found_player is not None
    assert found_player.username == "CaseSensitivePlayer"

def test_findExistingPlayer_empty_database(playerManager):
    # When the database is empty, findExistingPlayer should return None
    found_player = playerManager.findExistingPlayer("NonExistentPlayer")
    assert found_player is None

def test_addNewPlayer_empty_username(playerManager):
    # Adding a player with an empty username should return False
    result = playerManager.addNewPlayer("")
    assert result is False

def test_addNewPlayer_none_username(playerManager):
    # Adding a player with None as the username should return False
    result = playerManager.addNewPlayer(None)
    assert result is False