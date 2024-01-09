from tinydb import TinyDB, Query
from collections import defaultdict

class LeaderboardStats:
    def __init__(self) -> None:
        self._db = TinyDB("instance/FoosballGames.json")

    def getStats(self):
        self.updateStats()
        return {key: value for key, value in vars(self).items() if not key.startswith('_')}

    def updateStats(self):
        self.playerStats = self.getPlayerStats()
        self.teamStats = self.getTeamStats(False)
        self.teamStatsWithTeamInfo = self.getTeamStats(True)
        self.teamBeans = self.getTeamBeans()

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
            wins += sum(1 for game in data if player in [game['blackPlayer1'], game.get('blackPlayer2', "")] and game['winningTeam'] == 'BLACK')
            losses = sum(1 for game in data if player in [game['redPlayer1'], game.get('redPlayer2', "")] and game['winningTeam'] == 'BLACK')
            losses += sum(1 for game in data if player in [game['blackPlayer1'], game.get('blackPlayer2', "")] and game['winningTeam'] == 'RED')
            if player is not None:
                player_stats[player] = {'wins': wins, 'losses': losses}

        # Sort players based on wins and losses
        sortedTeams = sorted(player_stats.items(), key=lambda x: (x[1]['wins'] / (x[1]['wins'] + x[1]['losses']), x[1]['wins'], -x[1]['losses']), reverse=True)
        return sortedTeams[:10]

    def getTeamStats(self, includeTeam):
        # Initialize a defaultdict to store team statistics
        team_stats = defaultdict(lambda: {'wins': 0, 'losses': 0})

        # Iterate through each game
        for game_info in self._db.table('_default').all():
            red_team = [player for player in [game_info.get('redPlayer1', ""), game_info.get('redPlayer2', "")] if player is not None]
            black_team = [player for player in [game_info.get('blackPlayer1', ""), game_info.get('blackPlayer2', "")] if player is not None]

            # Check if the game is finished
            if game_info.get('isFinished', False) and len(red_team) == 2 and len(black_team) == 2:
                # Determine the winning team
                winning_team = game_info['winningTeam']

                # Create canonical team representation by sorting player names
                red_team.sort()
                black_team.sort()

                if includeTeam:
                    # Update team statistics for all player combinations and team assignments
                    team_stats[(black_team[0], black_team[1], 'RED')]['losses' if winning_team == 'RED' else 'wins'] += 1
                    team_stats[(red_team[0], red_team[1], 'BLACK')]['losses' if winning_team == 'BLACK' else 'wins'] += 1
                else:
                    team_stats[(red_team[0], red_team[1])]['wins' if winning_team == 'RED' else 'losses'] += 1
                    team_stats[(black_team[0], black_team[1])]['wins' if winning_team == 'BLACK' else 'losses'] += 1

        # Sort teams based on wins and losses
        sorted_teams = sorted(team_stats.items(), key=lambda x: (x[1]['wins'] / (x[1]['wins'] + x[1]['losses']), x[1]['wins'], -x[1]['losses']),  reverse=True)

        #only return the top ten
        return sorted_teams[:10]
    
    def getTeamBeans(self):
        # Initialize a defaultdict to store team statistics
        team_stats = defaultdict(lambda: {'beans': 0})

        # Iterate through each game
        for game_info in self._db.table('_default').all():
            red_team = [player for player in [game_info.get('redPlayer1', ""), game_info.get('redPlayer2', "")] if player is not None]
            black_team = [player for player in [game_info.get('blackPlayer1', ""), game_info.get('blackPlayer2', "")] if player is not None]

            # Check if the game is finished
            if game_info.get('isFinished', False) and len(red_team) == 2 and len(black_team) == 2 and (game_info.get('redTeamScore', 0) == 0 or game_info.get('blackTeamScore', 0) == 0):
                # Determine the winning team
                winning_team = game_info['winningTeam']

                # Create canonical team representation by sorting player names
                red_team.sort()
                black_team.sort()

                # Update team statistics for all player combinations and team assignments
                if winning_team == "RED":
                    team_stats[(black_team[0], black_team[1])]['beans'] += 1

                if winning_team == "BLACK":
                    team_stats[(red_team[0], red_team[1])]['beans'] += 1

        # Sort teams based on wins and losses
        sorted_teams = sorted(team_stats.items(), key=lambda x: (x[1]['beans']),  reverse=True)

        return sorted_teams