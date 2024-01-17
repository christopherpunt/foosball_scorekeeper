from configuration import Configuration

class TestConfiguration(Configuration):
    Configuration.foosballGamesDatabase = 'instance/FoosballGames_unitTest.json'
    Configuration.playersDatabase = 'instance/players_unitTest.json'

    #methods to allow using with statement in tests to use test configuration 
    #specific properties instead of main configuration
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass