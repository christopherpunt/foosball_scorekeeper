from tinydb import TinyDB, Query


class LeaderboardStats:
    def __init__(self) -> None:
        self._db = TinyDB("instance/FoosballGames.json")

        self.playerStats = self.getPlayerStats()

    def getStats(self):
        self.updateStats()
        return {key: value for key, value in vars(self).items() if not key.startswith('_')}

    def updateStats(self):
        self.playerStats = self.getPlayerStats()

    def getPlayerStats(self):
        # Fetch data from the TinyDB
        data = self._db.table('_default').all()

        # Process data to extract relevant information
        # You can modify this part based on your specific requirements
        players_data = []
        for game_id, game_info in enumerate(data, start=1):
            red_team = [game_info['redPlayer1'], game_info.get('redPlayer2', "")]
            black_team = [game_info['blackPlayer1'], game_info.get('blackPlayer2', "")]

            players_data.extend(red_team + black_team)

        # Calculate wins and losses for each player
        player_stats = {}
        for player in set(players_data):
            wins = sum(1 for game in data if player in [game['redPlayer1'], game.get('redPlayer2', "")] and game['winningTeam'] == 'RED')
            losses = sum(1 for game in data if player in [game['blackPlayer1'], game.get('blackPlayer2', "")] and game['winningTeam'] == 'BLACK')
            if player is not None:
                player_stats[player] = {'wins': wins, 'losses': losses}

        # Sort players based on wins and losses
        return sorted(player_stats.items(), key=lambda x: (x[1]['wins'], -x[1]['losses']), reverse=True)
