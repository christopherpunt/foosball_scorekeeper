import requests
import threading

class LedStripService:
    def __init__(self, url) -> None:
        self.url = url
        self.darkMode = False

    def sendPostRequest(self, function, data = None):
        thread = threading.Thread(target=self.makePostRequest, args=(function, data,))
        thread.start()

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
    
    def setDarkMode(self, value: bool):
        self.darkMode = value
        if self.darkMode:
            self.turnLightsOn()
        else:
            self.turnLightsOff()

    def goalScored(self, team):
        data = {
            "team": team,
            "darkMode": self.darkMode
        }
        self.sendPostRequest('/goal_scored', data)

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
        data = {
            'darkMode': self.darkMode
        }

        self.sendPostRequest('/game_started', data)
    
    def gameCompleted(self, winningTeam):
        data = {
            'winningTeam': winningTeam,
            'darkMode': self.darkMode
        }
        self.sendPostRequest('/game_completed', data)
