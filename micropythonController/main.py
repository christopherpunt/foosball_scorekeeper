from machine import Pin, ADC
from time import sleep_ms
import urequests as requests
import ujson as json
import neopixel
import sys
import gc
import network

# make sure the team variable is set in boot.py
# team = 'RED'  or  team = 'BLACK'
# so we can replace this program without having to worry about the team setting

analogIn = ADC(0)
# here we store the last vaerage value from the photo cell
averageValue = 0

# the delta when we consider it a goal
deltaMeassureValue = 50

ssid = 'foosball'
wifipassword = 'TGW66200'

baseUrl = ''

numLeds = 3
np = neopixel.NeoPixel(machine.Pin(4), numLeds)

network.hostname(team)
network.country('US')
network.phy_mode(network.MODE_11B)

backendIpAddress = '10.42.0.1'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# let's see if turning off the AP helps a bit
ap = network.WLAN(network.AP_IF)
ap.active(False) 

def connectToWifi():
    global wlan
    
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, wifipassword)
        while not wlan.isconnected():
            pass
    
    # connecting using a static IP seems to be faster than DHCP
    wlan.ifconfig((thisIpAddress, '255.255.255.0', backendIpAddress, backendIpAddress))
    
    # index 2 contains the ip address of the 'gateway', so this will be our raspi
    global baseUrl
    baseUrl = 'http://{}:5001'.format(backendIpAddress)
    print(baseUrl)
    
    data = {
        'team': team,
        'controllerIp': thisIpAddress
    }
    # as long as we can not connect to the backend we stay in here
    while not sendPostRequest(baseUrl + '/register_goal_counter', data):
        pass


def sendPostRequest(url, data):    
    if not wlan.isconnected():
        connectToWifi()
    
    for i in range(5):
        try:
            response = requests.post(url, data=json.dumps(data))
            print("Response status code:", response.status_code)
            print("Response content:", response.text)
            return True
        except Exception as e:
            gc.collect()
            print("POST Error:", e)
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
    sleep_ms(1)
    currentValue = analogIn.read()
    if isGoal(currentValue, averageValue):
        # strange enough: without that gc.collect we get random connection aborted 103 errors
        # when trying to send a post request; this seems to make it a bit better ?!?
        gc.collect()
        goal(currentValue)
        initGoalCountMode()
