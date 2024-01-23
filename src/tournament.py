import random


class Tournament:
    def __init__(self, players) -> None:
        self.players = players
        self.teams = []
        self.setTeams()
    
    def setTeams(self):
        if len(self.players) < 4:
            raise ValueError("There must be at least 4 players for a tournament")

        if len(self.players) % 2 != 0:
            raise ValueError("The number of players must be even to create teams.")

        # Shuffle the list of players to randomize the order
        random.shuffle(self.players)

        # Iterate through the shuffled players and create teams
        for i in range(0, len(self.players), 2):
            team = (self.players[i], self.players[i + 1])
            self.teams.append(team)

class TournamentManager:
    def __init__(self) -> None:
        self.currentTournament = None

    def newTournament(self, players):
        try:
            self.currentTournament = Tournament(players)
            return True
        except Exception as e:
            print(f'could not start tournament: {e}')
            return False
    