import random

class Team:
    def __init__(self, player1, player2) -> None:
        self.players = (player1, player2)

class Match:
    def __init__(self, teams) -> None:
        self.teams = []
        self.setTeams(teams)
        self.winner = None
    def setTeams(self, teams):
        self.teams = teams
        #only one team means there is a by for this team in the round
        if len(teams) == 1:
            self.winner = teams[0]
    def assignRandomWinner(self):
        random.shuffle(self.teams)
        self.winner = self.teams[0]

class Tournament:
    def __init__(self, players) -> None:
        self.round_number = 1
        self.teams = []
        self.setTeams(players)
        self.matches = {}
        self.setNextRoundMatches(self.teams)

    def setTeams(self, players):
        if len(players) < 4:
            raise ValueError('Need more than 4 people to play a tournament')
        if len(players) % 2 != 0:
            raise ValueError('Need even amount of players to start tournament')
        
        random.shuffle(players)
        for i in range(0, len(players), 2):
            self.teams.append(Team(players[i], players[i+1]))

    def setNextRoundMatches(self, teams):
        matches = []
        if self.round_number == 1:
            matches = self.createMatches(teams)
        elif self.round_number > 1:
            teams = self.getRoundWinners(self.round_number - 1)
            matches = self.createMatches(teams)

        self.matches[self.round_number] = matches
        self.round_number += 1
        return matches
    
    def createMatches(self, teams) -> [Match]:
        matches = []
        random.shuffle(teams)
        # Create matches for the current round
        for i in range(0, len(teams), 2):
            if len(teams) >= i + 2:
                currentMatchTeams = [teams[i], teams[i+1]]
            else:
                currentMatchTeams = [teams[i]]
            matches.append(Match(currentMatchTeams))
        return matches
    
    def getRoundWinners(self, round_number) -> [Team]:
        winningTeams = []
        for match in self.matches[round_number]:
            if match.winner:
                winningTeams.add(match.winner)
            
    def isRoundCompleted(self, round_number):
        for match in self.matches[round_number]:
            if match.winner is None:
                return False
        return True
            

class TournamentManager:
    def __init__(self) -> None:
        self.currentTournament = None

    def newTournament(self, players):
        try:
            self.currentTournament = Tournament(players)
            return True
        except Exception as e:
            print(f'Could not start tournament: {e}')
            return False
