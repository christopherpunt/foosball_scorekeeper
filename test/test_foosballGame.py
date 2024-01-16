from foosballGame import FoosballGame

def test_addScoreFrom0():
    game = FoosballGame("player1", "player2")

    assert game.redTeamScore == 0
    assert game.blackTeamScore == 0

    game.addScore('RED')
    assert game.redTeamScore == 1
    assert game.blackTeamScore == 0

    game.addScore('BLACK')
    assert game.redTeamScore == 1
    assert game.blackTeamScore == 1

def test_addScorefromNon0():
    game = FoosballGame("player1", "player2")

    game.redTeamScore = 4
    game.blackTeamScore = 3

    game.addScore('RED')
    assert game.redTeamScore == 5
    assert game.blackTeamScore == 3

    game.addScore('BLACK')
    assert game.redTeamScore == 5
    assert game.blackTeamScore == 4


