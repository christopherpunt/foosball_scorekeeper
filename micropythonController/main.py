from machine import Pin, ADC
from time import sleep_ms
import urequests as requests
import ujson as json
import neopixel
import sys
import gc

# make sure the team variable is set in boot.py
# team = 'RED'  or  team = 'BLACK'
# so we can replace this program without having to worry about the team setting

analogIn = ADC(0)
# here we store the last vaerage value from the photo cell
averageValue = 0

ssid = 'foosball'
wifipassword = 'TGW66200'

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
    
    # index 2 contains the ip address of the 'gateway', so this will be our raspi
    global baseUrl
    baseUrl = 'http://{}:5001'.format(sta_if.ifconfig()[2])
    print(baseUrl)
    
    data = {
        'team': team,
        'controllerIp': sta_if.ifconfig()[0]
    }
    # as long as we can not connect to the backend we stay in here
    while not sendPostRequest(baseUrl + '/register_goal_counter', data):
        sleep_ms(1000)

def sendPostRequest(url, data):    
    for i in range(2):
        try:
            response = requests.post(url, data=json.dumps(data))
            print("Response status code:", response.status_code)
            print("Response content:", response.text)
            return True
        except Exception as e:
            gc.collect()
            print("POST Error:", e)
            sleep_ms(1000)
    return False

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
    return averageValue - currentValue > 50

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



try:
    team
except NameError:    
    print('Make sure you set the team variable in boot.py, e. g. team = \'RED\'')
    sys.exit()


lightsRed()
connectToWifi()
initGoalCountMode()

while True:
    currentValue = analogIn.read()
    sleep_ms(1)
    if isGoal(currentValue, averageValue):
        # strange enough: without that gc.collect we get random connection aborted 103 errors
        # when trying to send a post request; this seems to fix it somehow
        gc.collect()
        goal(currentValue)
        initGoalCountMode()