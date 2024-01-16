

class Configuration:
    backendPort = 5001
    ledStripControllerPort = 5002
    ledStripControllerUrl = "http://localhost:" + str(ledStripControllerPort)
    gameWinningAmount = 5
    dateFormat = '%m/%d/%Y, %I:%M:%S %p'
    foosballGamesDatabase = 'instance/FoosballGames.json'
    playersDatabase = 'instance/players.json'