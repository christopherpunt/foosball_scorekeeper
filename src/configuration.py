from tinydb import TinyDB, Query


class Configuration:
    backendPort = 5001
    ledStripControllerPort = 5002
    ledStripControllerUrl = "http://localhost:" + str(ledStripControllerPort)
    gameWinningAmount = 5
    dateFormat = '%m/%d/%Y, %I:%M:%S %p'
    foosballGamesDatabase = 'instance/FoosballGames.json'
    playersDatabase = 'instance/players.json'
    leaderboardStatsCount = 10
    defaultJoinGamePlayersCount = 14
    leaderboardHistory = 100

    db = TinyDB('instance/configuration.json', indent=2, create_dirs=True)

    @classmethod
    def load_configuration(cls):
        """Load configuration from TinyDB into class variables."""
        config_data = cls.db.all()  # Get all records from TinyDB
        if config_data:
            config = config_data[0]  # Assuming a single record for configuration
            cls.backendPort = config.get('backendPort', cls.backendPort)
            cls.ledStripControllerPort = config.get('ledStripControllerPort', cls.ledStripControllerPort)
            cls.ledStripControllerUrl = "http://localhost:" + str(cls.ledStripControllerPort)
            cls.gameWinningAmount = config.get('gameWinningAmount', cls.gameWinningAmount)
            cls.dateFormat = config.get('dateFormat', cls.dateFormat)
            cls.foosballGamesDatabase = config.get('foosballGamesDatabase', cls.foosballGamesDatabase)
            cls.playersDatabase = config.get('playersDatabase', cls.playersDatabase)
            cls.leaderboardStatsCount = config.get('leaderboardStatsCount', cls.leaderboardStatsCount)
            cls.defaultJoinGamePlayersCount = config.get('defaultJoinGamePlayersCount', cls.defaultJoinGamePlayersCount)
            cls.leaderboardHistory = config.get('leaderboardHistory', cls.leaderboardHistory)

    @classmethod
    def save_configuration(cls):
        """Save current class variables back to TinyDB."""
        cls.db.truncate()  # Clear existing records
        cls.db.insert({
            'backendPort': cls.backendPort,
            'ledStripControllerPort': cls.ledStripControllerPort,
            'gameWinningAmount': cls.gameWinningAmount,
            'dateFormat': cls.dateFormat,
            'foosballGamesDatabase': cls.foosballGamesDatabase,
            'playersDatabase': cls.playersDatabase,
            'leaderboardStatsCount': cls.leaderboardStatsCount,
            'defaultJoinGamePlayersCount': cls.defaultJoinGamePlayersCount,
            'leaderboardHistory': cls.leaderboardHistory,
        })
