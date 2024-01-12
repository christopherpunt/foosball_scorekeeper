from foosballGame import FoosballGame

def test_addScoreFrom0():
    game = FoosballGame("player1", "player2")

    assert game.redTeamScore == 0
    assert game.blackTeamScore == 0

    game.addScore('RED')
    assert game.redTeamScore == 1
    assert game.blackTeamScore == 0

