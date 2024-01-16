from player import Player, PlayerManager
from unittest.mock import Mock
from testConfiguration import TestConfiguration
import pytest
import os

@pytest.fixture
def mock_socketio():
    return Mock()

@pytest.fixture
def playerManager(mock_socketio):
    # Use the test configuration in your fixture
    with TestConfiguration():
        yield PlayerManager(mock_socketio)

@pytest.fixture(autouse=True)
def setup_teardown_test_database():
    try:
        # Use the test configuration for the database path
        os.remove(TestConfiguration.playersDatabase)
    except FileNotFoundError:
        pass  # Ignore the error if the file doesn't exist
    
def test_addNewPlayer(playerManager):
    result = playerManager.addNewPlayer("Player1")
    assert result == True