from machine import Pin, ADC
from time import sleep
 
analogIn = ADC(0)
averageValue = 0
 
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
    sleep(5)
    calculateAverage()

calculateAverage()
while True:
    currentValue = analogIn.read()
    sleep(.001)
    if isGoal(currentValue, averageValue):
        Goal()