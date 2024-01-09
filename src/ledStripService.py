import requests


class LedStripService:
    def __init__(self, url) -> None:
        self.url = url

    def sendPostRequest(self, function, data):
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        try:
            response = requests.post(self.url + function, json=data, headers=headers)
        except Exception as e:
            print(f'Could not post to: {self.url + function} error: {e}')
        print(f"Status Code: {response.status_code}")
        print("Response Content:")
        print(response.text)
    
    def goalScored(self, team):
        data = {
            "team": team
        }
        self.sendPostRequest('/goal_scored', data)

    def gameStarted(self):
        pass
    
    def gameCompleted(self):
        pass
