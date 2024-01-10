from tinydb import TinyDB, Query
from collections import defaultdict
from datetime import datetime

class LeaderboardStats:
    def __init__(self) -> None:
        self._db = TinyDB("instance/FoosballGames.json")

    def getStats(self):
        self.updateStats()
        return {key: value for key, value in vars(self).items() if not key.startswith('_')}

    def updateStats(self):
        self.playerStats = self.getPlayerStats()
        self.teamStats = self.getTeamStats()
        self.teamBeans = self.getTeamBeans()
        self.redVsBlack = self.getRedVsBlack()
        self.shortestGame = self.getShortestGames()

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

    def getTeamStats(self):
        # Initialize a defaultdict to store team statistics
        team_stats = defaultdict(lambda: {'wins': 0, 'losses': 0})

        # Iterate through each game
        for game_info in self._db.table('_default').all():
            red_team = [player for player in [game_info.get('redPlayer1', None), game_info.get('redPlayer2', None)] if player is not None]
            black_team = [player for player in [game_info.get('blackPlayer1', None), game_info.get('blackPlayer2', None)] if player is not None]

            # Check if the game is finished
            if game_info.get('isFinished', False) and len(red_team) == 2 and len(black_team) == 2:
                # Determine the winning team
                winning_team = game_info['winningTeam']

                # Create canonical team representation by sorting player names
                red_team.sort()
                black_team.sort()

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
            red_team = [player for player in [game_info.get('redPlayer1', None), game_info.get('redPlayer2', None)] if player is not None]
            black_team = [player for player in [game_info.get('blackPlayer1', None), game_info.get('blackPlayer2', None)] if player is not None]

            # Check if the game is finished
            if game_info.get('isFinished', False) and (game_info.get('redTeamScore', 0) == 0 or game_info.get('blackTeamScore', 0) == 0):
                # Determine the winning team
                winning_team = game_info['winningTeam']

                # Create canonical team representation by sorting player names
                red_team.sort()
                black_team.sort()

                # Update team statistics for all player combinations and team assignments
                if winning_team == "RED":
                    losingTeamString = f"{black_team[0] + ' - ' + black_team[1] if len(black_team) == 2 else black_team[0]}"
                    team_stats[(losingTeamString)]['beans'] += 1

                if winning_team == "BLACK":
                    losingTeamString = f"{red_team[0] + ' - ' + red_team[1] if len(red_team) == 2 else red_team[0]}"
                    team_stats[(losingTeamString)]['beans'] += 1

        # Sort teams based on wins and losses
        sorted_teams = sorted(team_stats.items(), key=lambda x: (x[1]['beans']),  reverse=True)

        return sorted_teams
    
    def getRedVsBlack(self):
        teamData = {
            'RED':0,
            'BLACK':0
            }
        for game_info in self._db.table('_default').all():
            if game_info.get('isFinished', False):
                teamData[game_info['winningTeam']] += 1

        return sorted(teamData.items(), key=lambda x: (x[1]), reverse=True)

    def getShortestGames(self):
        team_stats = defaultdict(lambda: {'length': None, 'score': '0-0'})

        for game_info in self._db.table('_default').all():
            red_team = [player for player in [game_info.get('redPlayer1', None), game_info.get('redPlayer2', None)] if player is not None]
            black_team = [player for player in [game_info.get('blackPlayer1', None), game_info.get('blackPlayer2', None)] if player is not None]

            # Check if the game is finished
            if game_info.get('isFinished', False):
                # Determine the winning team
                winning_team = game_info['winningTeam']

                # Create canonical team representation by sorting player names
                red_team.sort()
                black_team.sort()

                # Update team statistics for all player combinations and team assignments
                if winning_team == "RED":
                    winningTeamString = f"{red_team[0] + ' - ' + red_team[1] if len(red_team) == 2 else red_team[0]}"
                    losingTeamString = f"{black_team[0] + ' - ' + black_team[1] if len(black_team) == 2 else black_team[0]}"
                    duration = datetime.strptime(game_info['finishTime'], '%m/%d/%Y, %I:%M:%S%p') - datetime.strptime(game_info['startTime'], '%m/%d/%Y, %I:%M:%S%p')
                    scoreString = f"{game_info.get('redTeamScore', 0)} -- {game_info.get('blackTeamScore', 0)}"

                    team_stats[(winningTeamString, losingTeamString)]['length'] = duration
                    team_stats[(winningTeamString, losingTeamString)]['score'] = scoreString

                if winning_team == "BLACK":
                    losingTeamString = f"{red_team[0] + ' - ' + red_team[1] if len(red_team) == 2 else red_team[0]}"
                    winningTeamString = f"{black_team[0] + ' - ' + black_team[1] if len(black_team) == 2 else black_team[0]}"
                    duration = datetime.strptime(game_info['finishTime'], '%m/%d/%Y, %I:%M:%S%p') - datetime.strptime(game_info['startTime'], '%m/%d/%Y, %I:%M:%S%p')
                    scoreString = f"{game_info.get('blackTeamScore', 0)} -- {game_info.get('redTeamScore', 0)}"

                    team_stats[(winningTeamString, losingTeamString)]['length'] = duration
                    team_stats[(winningTeamString, losingTeamString)]['score'] = scoreString

        return sorted(team_stats.items(), key=lambda x: (x[1]['length']))[:10]