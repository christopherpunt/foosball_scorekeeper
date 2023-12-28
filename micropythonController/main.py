from machine import Pin, ADC
from time import sleep_ms
import urequests as requests
import ujson as json
import neopixel

analogIn = ADC(0)
# here we store the last vaerage value from the photo cell
averageValue = 0

ssid = 'foosball'
wifipassword = 'TGW66200'

# states which team gets a goal; so RED controller needs to be mounted in the black goal
# possible values RED and BLACK
team = 'RED'
baseUrl = ''

numLeds = 3
np = neopixel.NeoPixel(machine.Pin(4), numLeds)

def connectToWifi():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, wifipassword)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    
    # index 2 contains the ip address of the gateway
    global baseUrl
    baseUrl = 'http://{}:5001'.format(sta_if.ifconfig()[2])
    print(baseUrl)
    
    data = {
        'team': team,
        'controllerIp': sta_if.ifconfig()[0]
    }
    sendPostRequest(baseUrl + '/register_goal_counter', data)

def sendPostRequest(url, data):
    try:
        response = requests.post(url, data=json.dumps(data))
        print("Response status code:", response.status_code)
        print("Response content:", response.text)
    except Exception as e:
        print("POST Error:", e)

def lights(r, g, b):
    for j in range(numLeds):
        np[j] = (r, g, b)
    np.write()

def lightsOff():
    lights(0, 0, 0)

def lightsOn():
    lights(255, 255, 255)

def lightsRed():
    lights(255, 0, 0)

def lightsGreen():
    lights(0, 255, 0)

def initGoalCountMode():
    lightsOn()
    # sleep a bit to get the final brightness
    sleep_ms(500)
    sumAverageValue = 0
    global averageValue
    for x in range(10):
        sumAverageValue = sumAverageValue + analogIn.read()
        sleep_ms(100)
    averageValue = sumAverageValue / 10
    print(f'average: {averageValue}')

def isGoal(currentValue, averageValue):
    return averageValue - currentValue > 10

def cycleGoalLights():
    for i in range(20 * numLeds):
        lightsOff()
        np[i % numLeds] = (255, 255, 255)
        np.write()
        sleep_ms(50)
        
def goal(currentValue):
    print(f'Goal!!! Current {currentValue}, Avg {averageValue}')
    lightsGreen()
    
    data = {
        'team': team,
        'currentValue': currentValue,
        'averageValue': averageValue
    }
    sendPostRequest(baseUrl + '/add_score', data)
    cycleGoalLights()

lightsRed()
connectToWifi()
initGoalCountMode()

while True:
    currentValue = analogIn.read()
    sleep_ms(1)
    if isGoal(currentValue, averageValue):
        goal(currentValue)
        initGoalCountMode()