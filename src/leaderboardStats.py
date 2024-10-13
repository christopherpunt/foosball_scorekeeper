from tinydb import TinyDB, Query
from collections import defaultdict
from datetime import datetime, timedelta
from configuration import Configuration

class LeaderboardStats:
    def __init__(self) -> None:
        self._db = TinyDB(Configuration.foosballGamesDatabase)
        
    def getAllStats(self):
        return {
            'playerStats': self.getPlayerStats()[:Configuration.leaderboardStatsCount],
            'teamStats': self.getTeamStats()[:Configuration.leaderboardStatsCount],
            'teamBeans': self.getTeamBeans()[:Configuration.leaderboardStatsCount],
            'redVsBlack': self.getRedVsBlack(),
            'shortestGames': self.getShortestGames()[:Configuration.leaderboardStatsCount],
            'recentGameHistory': self.getRecentGameHistory()[:Configuration.leaderboardStatsCount]
        }
    
    def getHiddenStats(self):
        return {
            'playerWastedTime': self.getPlayerWastedTime(),
            'totalGames': self.getTotalGameTime()
        }

    def getPlayerStats(self):
        # Fetch data from the TinyDB
        data = self.getGameData()

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

            beans = sum(1 for game in data if player in [game['redPlayer1'], game.get('redPlayer2', "")] and game['winningTeam'] == 'BLACK' and game['redTeamScore'] == 0)
            beans += sum(1 for game in data if player in [game['blackPlayer1'], game.get('blackPlayer2', "")] and game['winningTeam'] == 'RED' and game['blackTeamScore'] == 0)

            if player is not None:
                player_stats[player] = {'wins': wins, 'losses': losses, 'beans': beans}

        # Sort players first by win ratio wins/losses but if losses is 0 then ratio is 0, then by win rate (wins/ (wins + losses)), there should always be at least 1 win or loss, so no need to check divide by 0
        sortedTeams = sorted(player_stats.items(), key=lambda x: ((x[1]['wins'] /  x[1]['losses']) if x[1]['losses'] != 0 else x[1]['wins'], x[1]['wins'] / (x[1]['wins'] + x[1]['losses'])), reverse=True)
        return sortedTeams

    def getTeamStats(self):
        # Initialize a defaultdict to store team statistics
        team_stats = defaultdict(lambda: {'wins': 0, 'losses': 0})

        # Iterate through each game
        for game_info in self.getGameData():
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

        # Sort team first by win ratio wins/losses but if losses is 0 then ratio is 0, then by win rate (wins/ (wins + losses)), there should always be at least 1 win or loss, so no need to check divide by 0
        sorted_teams = sorted(team_stats.items(), key=lambda x: ((x[1]['wins'] /  x[1]['losses']) if x[1]['losses'] != 0 else x[1]['wins'], x[1]['wins'] / (x[1]['wins'] + x[1]['losses'])), reverse=True)

        #only return the top ten
        return sorted_teams
    
    def getTeamBeans(self):
        # Initialize a defaultdict to store team statistics
        team_stats = defaultdict(lambda: {'beans': 0})

        # Iterate through each game
        for game_info in self.getGameData():
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
        for game_info in self.getGameData():
            if game_info.get('isFinished', False):
                teamData[game_info['winningTeam']] += 1

        return sorted(teamData.items(), key=lambda x: (x[1]), reverse=True)

    def getShortestGames(self):
        game_stats = []

        for game_info in self.getGameData():
            red_team = [player for player in [game_info.get('redPlayer1', None), game_info.get('redPlayer2', None)] if player is not None]
            black_team = [player for player in [game_info.get('blackPlayer1', None), game_info.get('blackPlayer2', None)] if player is not None]

            # Check if the game is finished
            if game_info.get('isFinished', False):
                # Create canonical team representation by sorting player names
                red_team.sort()
                black_team.sort()

                redTeamString = f"{red_team[0] + ' - ' + red_team[1] if len(red_team) == 2 else red_team[0]}"
                blackTeamString = f"{black_team[0] + ' - ' + black_team[1] if len(black_team) == 2 else black_team[0]}"
                duration = datetime.strptime(game_info['finishTime'], Configuration.dateFormat) - datetime.strptime(game_info['startTime'], Configuration.dateFormat)
                scoreString = f"{game_info.get('redTeamScore', 0)} -- {game_info.get('blackTeamScore', 0)}"

                game_stats.append((redTeamString, blackTeamString, scoreString, duration))

        return sorted(game_stats, key=lambda x: (x[3]))
    
    def getRecentGameHistory(self):
        game_stats = []

        for game_info in self.getGameData():
            red_team = [player for player in [game_info.get('redPlayer1', None), game_info.get('redPlayer2', None)] if player is not None]
            black_team = [player for player in [game_info.get('blackPlayer1', None), game_info.get('blackPlayer2', None)] if player is not None]

            # Check if the game is finished
            if game_info.get('isFinished', False):
                # Determine the winning team
                winning_team = game_info['winningTeam']

                # Create canonical team representation by sorting player names
                red_team.sort()
                black_team.sort()

                # Update game statistics for all player combinations and team assignments
                redTeamString = f"{red_team[0] + ' - ' + red_team[1] if len(red_team) == 2 else red_team[0]}"
                blackTeamString = f"{black_team[0] + ' - ' + black_team[1] if len(black_team) == 2 else black_team[0]}"
                duration = datetime.strptime(game_info['finishTime'], Configuration.dateFormat) - datetime.strptime(game_info['startTime'], Configuration.dateFormat)
                score_string = f"{game_info.get('redTeamScore', 0)} -- {game_info.get('blackTeamScore', 0)}"
                finish_date = game_info['finishTime']

                game_stats.append((redTeamString, blackTeamString, duration, score_string, finish_date))

        return sorted(game_stats, key=lambda x: datetime.strptime(x[4], Configuration.dateFormat), reverse=True)

    def getPlayerWastedTime(self):
        # Fetch data from the TinyDB
        data = self.getGameData()

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
            numGames = 0
            duration = timedelta(seconds=0)
            for game in data:
                if player in [game['redPlayer1'], game.get('redPlayer2', ""), game['blackPlayer1'], game.get('blackPlayer2', "")]:
                    numGames += 1
                    duration += datetime.strptime(game['finishTime'], Configuration.dateFormat) - datetime.strptime(game['startTime'], Configuration.dateFormat)

            if player is not None and player is not "":
                player_stats[player] = {'numGames': numGames, 'totalTime': duration}

        # Sort players first by win ratio wins/losses but if losses is 0 then ratio is 0, then by win rate (wins/ (wins + losses)), there should always be at least 1 win or loss, so no need to check divide by 0
        sortedTeams = sorted(player_stats.items(), key=lambda x: (x[1]['numGames']), reverse=True)
        return sortedTeams
    
    def getPlayersSortedByGamesPlayed(self):
        # Fetch data from the TinyDB
        data = self.getGameData()

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
            numGames = 0
            for game in data:
                if player in [game['redPlayer1'], game.get('redPlayer2', ""), game['blackPlayer1'], game.get('blackPlayer2', "")]:
                    numGames += 1

            if player is not None and player is not "":
                player_stats[player] = numGames

        return player_stats
    
    def getTotalGameTime(self):
        data = self.getGameData()
        duration = timedelta(seconds=0)
        numGames = 0

        for game in data:
            duration += datetime.strptime(game['finishTime'], Configuration.dateFormat) - datetime.strptime(game['startTime'], Configuration.dateFormat)
            numGames += 1
        return (numGames, duration)
    
    def getGameData(self):
        data = self._db.table('_default').all()
        if (Configuration.leaderboardHistory <= 0):
            return data
        return sorted(data, key=lambda x: int(x.doc_id), reverse=True)[:Configuration.leaderboardHistory]