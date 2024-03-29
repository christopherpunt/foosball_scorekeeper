import neopixel
import board
import time
import json
from flask import Flask, request, jsonify
from configuration import Configuration


app = Flask(__name__)

from LedStrip import ColorProvider, LedStrip, LedSwitch, AllLedsSameColor

q1 = list(range(1, 7))
q1r = list(reversed(q1))
q2 = list(range(7, 13))
q2r = list(reversed(q2))
q3 = list(range(13, 16))
q3r = list(reversed(q3))
q4 = list(range(16, 19))
q4r = list(reversed(q4))
q5 = list(range(19, 25))
q5r = list(reversed(q5))
q6 = list(range(25, 31))
q6r = list(reversed(q6))
q7 = list(range(31, 34))
q7r = list(reversed(q7))
q8 = list(range(34, 38))
q8r = list(reversed(q8))


numLeds = 37 # segments (there is 3 LEDs in one segment)
np = neopixel.NeoPixel(board.D18, numLeds)
allLeds = [*q1, *q2, *q3, *q4, *q5, *q6, *q7, *q8]

class NeopixelLedSwitch(LedSwitch):
    def on(self, leds: list, color: ColorProvider):
        for led in leds:
            np[led-1] = color.getColor(led)
        np.show()

    def off(self, leds: list):
        for led in leds:
            np[led-1] = (0,0,0)
        np.show()

ledStrip = LedStrip(allLeds, NeopixelLedSwitch())

@app.route('/goal_scored', methods=['POST'])
def handleGoalScored():
    data = request.get_json()
    if data:
        team = data.get('team')
        if team == 'RED':
            for i in range(3):
                ledStrip.race(q2 + q3, q5r + q4r, True, 20, AllLedsSameColor((0,255,0)))
        elif team == 'BLACK':
            for i in range(3):
                ledStrip.race(q1r + q8r, q6 + q7, True, 20, AllLedsSameColor((0,0,255)))
        else:
            print(f'Something went wrong! data:{data} team: {team}')

        if 'darkMode' in data:
            if data['darkMode']:
                ledStrip.allOn(AllLedsSameColor((255,255,255)))

    return jsonify({'success': True})


@app.route('/game_started', methods=['POST'])
def handleGameStarted():
    data = request.get_json()
    ledStrip.allOn(AllLedsSameColor((255,0,0)))
    time.sleep(3)

    if 'darkMode' in data:
        if data['darkMode']:
            ledStrip.allOn(AllLedsSameColor((255,255,255)))
            return jsonify({'success': True})
        
    ledStrip.allOff()

    return jsonify({'success': True})


@app.route('/game_completed', methods=['POST'])
def handleGameCompleted():
    data = request.get_json()
    success = False

    if data and 'winningTeam' in data:
        if data['winningTeam'] == 'RED':
            for i in range(5):
                ledStrip.race(allLeds, list(reversed(allLeds)), False, 35, AllLedsSameColor((0,255,0)))
            success = True
        elif data['winningTeam'] == 'BLACK':
            for i in range(5):
                ledStrip.race(allLeds, list(reversed(allLeds)), False, 35, AllLedsSameColor((0,0,255)))
            success = True
        
        if 'darkMode' in data:
            if data['darkMode']:
                ledStrip.allOn(AllLedsSameColor((255,255,255)))

    return jsonify({'success': success})


@app.route('/light_switch', methods=['POST'])
def handleLightsOn():
    data = request.get_json()
    if data and 'state' in data:
        state = data['state']
        color = tuple(data.get('color', (255, 255, 255)))
    if state:
        ledStrip.allOn(AllLedsSameColor(color))
    else:
        ledStrip.allOff()

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(port=Configuration.ledStripControllerPort, debug=True)