from machine import Pin, ADC
from time import sleep
import urequests as requests
import ujson as json
 
analogIn = ADC(0)
averageValue = 0

team = 'RED'
baseUrl = 'http://localhost:5001'

def send_post_request(url, data):
    try:
        response = requests.post(url, data=json.dumps(data))
        print("Response status code:", response.status_code)
        print("Response content:", response.text)
    except Exception as e:
        print("Error:", e)
 
def calculateAverage():
    sumAverageValue = 0
    global averageValue
    for x in range(20):
        sumAverageValue = sumAverageValue + analogIn.read()
        sleep(0.001)
    averageValue = sumAverageValue / 20
    print(f'average: {averageValue}')

def isGoal(currentValue, averageValue):
    return averageValue - currentValue > 10
 
def Goal(currentValue):
    print(currentValue)
    print('Goal!!!')

    data = {
        'team': team,
        'currentValue': currentValue,
        'averageValue': averageValue
    }
    send_post_request(baseUrl + '/add_score', data)
    sleep(5)
    calculateAverage()

calculateAverage()
while True:
    currentValue = analogIn.read()
    sleep(0.001)
    if isGoal(currentValue, averageValue):
        Goal(currentValue)