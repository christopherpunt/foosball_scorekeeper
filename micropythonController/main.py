from machine import Pin, ADC, Timer
from time import sleep_ms
import urequests as requests
import ujson as json
import neopixel
import sys
import gc
import network

import webrepl

# make sure the 'team' and 'thisIpAddress' variables are set in boot.py
# team = 'RED'  or  team = 'BLACK'
# so we can replace this program without having to worry about the team setting

# ------------- some config stuff --------------

# here we store the last average value from the photo cell
averageValue = 0
# the delta when we consider it a goal
deltaMeassureValue = 50

backendIpAddress = '10.42.0.1'

ssid = 'foosball'
wifipassword = 'TGW66200'

numLeds = 3

# ------------- some config stuff --------------

baseUrl = ''

analogIn = ADC(0)
np = neopixel.NeoPixel(Pin(4), numLeds)

network.hostname(f'NodeMCU Team {team}')
network.country('US')

def send_ping(t):
    data = {
        'team': team,
        'averageValue': averageValue
    }
    sendPostRequest(baseUrl + '/ping', data)
    # strange enough: without that gc.collect we get random connection aborted 103 errors
    # when trying to send a post request; this seems to make it a bit better ?!?
    gc.collect()

def connectToWifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('connecting to network...')
        # connecting using a static IP seems to be faster than DHCP
        wlan.ifconfig((thisIpAddress, '255.255.255.0', backendIpAddress, backendIpAddress))
    
        wlan.connect(ssid, wifipassword)
        while not wlan.isconnected():
            pass
        
        print(f'Connected with IP config {wlan.ifconfig()}')
    
    webrepl.start()
    
    global baseUrl
    baseUrl = 'http://{}:5001'.format(backendIpAddress)
    
    # this should keep the wifi connection open
    tim = Timer(-1)
    tim.init(period=5000, mode=Timer.PERIODIC, callback=send_ping)
    
    # as long as we can not connect to the backend we stay in here
    while not sendPostRequest(baseUrl + '/register_goal_counter', { 'team': team, 'controllerIp': thisIpAddress }):
        pass


def sendPostRequest(url, data):    
    for i in range(5):
        try:
            response = requests.post(url, data=json.dumps(data, separators=(',', ':')))
            print(f'Response status code: {response.status_code}, content: {response.text}')
            return True
        except Exception as e:
            print("POST Error:", e)
            sleep_ms(100)
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
        sleep_ms(50)
    averageValue = sumAverageValue / 10
    print(f'average: {averageValue}')

def isGoal(currentValue, averageValue):
    return averageValue - currentValue > deltaMeassureValue

def cycleGoalLights():
    for i in range(20 * numLeds):
        lightsOff()
        np[i % numLeds] = (255, 255, 255)
        np.write()
        sleep_ms(50)
        
def goal(currentValue):
    print(f'Goal!!! Current {currentValue}, Avg {averageValue}')
    lightsGreen()
    
    sendPostRequest(baseUrl + '/add_score', { 'team': team, 'currentValue': currentValue, 'averageValue': averageValue })
    cycleGoalLights()

try:
    team
    thisIpAddress
except NameError:    
    print('Make sure you set the team and thisIpAddress variables in boot.py')
    sys.exit()

lightsRed()
connectToWifi()
initGoalCountMode()

while True:
    sleep_ms(1)
    currentValue = analogIn.read()
    if isGoal(currentValue, averageValue):
        goal(currentValue)
        initGoalCountMode()

