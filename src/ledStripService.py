import requests
import threading

class LedStripService:
    def __init__(self, url) -> None:
        self.url = url
        self.darkMode = False

    def sendPostRequest(self, function, data = None):
        thread = threading.Thread(target=self.makePostRequest, args=(function, data,))
        thread.start()

    def setDarkMode(self, value: bool):
        self.darkMode = value
        if self.darkMode:
            self.turnLightsOn()
        else:
            self.turnLightsOff()

    def makePostRequest(self, function, data = None):
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        try:
            response = requests.post(self.url + function, json=data, headers=headers)
            print(f"Status Code: {response.status_code} with data {response.text}")
        except Exception as e:
            print(f'Could not post to: {self.url + function} with data:{data} error: {e}')
    
    def goalScored(self, team):
        data = {
            "team": team
        }
        self.sendPostRequest('/goal_scored', data)
        if self.darkMode:
            self.turnLightsOn()

    def turnLightsOn(self):
        data = {
            'state': True,
            'color': (255,255,255)
        }
        self.sendPostRequest('/light_switch', data)

    def turnLightsOff(self):
        data = {
            'state': False
        }
        self.sendPostRequest('/light_switch', data)

    def gameStarted(self):
        self.sendPostRequest('/game_started')
        if self.darkMode:
            self.turnLightsOn()
    
    def gameCompleted(self, winningTeam):
        data = {
            'winningTeam': winningTeam
        }
        self.sendPostRequest('/game_completed', data)
        if self.darkMode:
            self.turnLightsOn()
