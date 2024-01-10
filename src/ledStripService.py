import requests


class LedStripService:
    def __init__(self, url) -> None:
        self.url = url

    def sendPostRequest(self, function, data = None):
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        try:
            response = requests.post(self.url + function, json=data, headers=headers)
            print(f"Status Code: {response.status_code}")
            print("Response Content:")
            print(response.text)
        except Exception as e:
            print(f'Could not post to: {self.url + function} with data:{data} error: {e}')
    
    def goalScored(self, team):
        data = {
            "team": team
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
        self.sendPostRequest('/game_started')
    
    def gameCompleted(self, winningTeam):
        data = {
            'winningTeam': winningTeam
        }
        self.sendPostRequest('/game_completed', data)
