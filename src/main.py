from configuration import Configuration
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from foosballGame import FoosballGameManager
from player import PlayerManager
from leaderboardStats import LeaderboardStats
from ledStripService import LedStripService
import json
app = Flask(__name__)
socketio = SocketIO(app)

# serve the socket.io js file as static content
static_files = {
    '/static' : './static'
}

ledStripControllerUrl = Configuration.ledStripControllerUrl
gameManager = FoosballGameManager(socketio)
playerManager = PlayerManager(socketio)
leaderboardStats = LeaderboardStats()
ledStripService = LedStripService(ledStripControllerUrl)

def requestToJson(request):
    raw_data = request.data
    data_str = raw_data.decode('utf-8')
    return json.loads(data_str)

@app.route('/')
def index():
    stats = leaderboardStats.getStats()
    return render_template('leaderboard.html', stats=stats)

@app.route('/players')
def getAllPlayers():
    return render_template('/players.html', players=playerManager.getAllPlayers())

@app.route('/join_game')
def joinGame():
    return render_template('join_game.html', players=playerManager.getAllPlayers())

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/game_page')
def game_page():
    if gameManager.currentGame is not None:
        return render_template('game_page.html')
    return joinGame()

@app.route('/start_game', methods=['POST'])
def start_game():
    json = requestToJson(request)
    ledStripService.gameStarted()
    return gameManager.startGame(json.get('RED'), json.get('BLACK'))

@app.route('/add_user', methods=['POST'])
def addUser():
    return playerManager.addNewPlayer(request)

@app.route('/add_score', methods=['POST'])
def addScore():
    team_value = requestToJson(request).get('team')
    if gameManager.currentGame:
        returnValue = gameManager.currentGame.addScore(team_value)
        gameManager.updateCurrentGameData()
        if gameManager.currentGame.isFinished:
            ledStripService.gameCompleted(gameManager.currentGame.winningTeam)
        else:
            ledStripService.goalScored(team_value)

        return returnValue
    return jsonify({'success': False, 'message': f'Game not started could not add score.'})

# the goal counters / controllers need to register first before we can start a game
@app.route('/register_goal_counter', methods=['POST'])
def registerGoalCounter():
    json = requestToJson(request)
    team = json.get('team')
    controllerIp = json.get('controllerIp')
    return jsonify({'success': True})

@app.route('/lights_on', methods=['POST'])
def turnLightsOn():
    ledStripService.turnLightsOn()
    return render_template('settings.html')

@app.route('/lights_off', methods=['POST'])
def turnLightsOff():
    ledStripService.turnLightsOff()
    return render_template('settings.html')

@socketio.on('get_initial_data')
def handle_get_initial_data():
    gameManager.updateCurrentGameData()

@socketio.on('change_score')
def handle_change_score(data):
    if 'team' in data and 'action' in data:
        team = data['team']
        action = data['action']

        if action == 'minus':
            gameManager.currentGame.removeScore(team.upper())
        elif action == 'plus':
            gameManager.currentGame.addScore(team.upper())
        else:
            print('incorrect action')
        gameManager.updateCurrentGameData()

@socketio.on('switch_sides')
def handle_switch_sides():
    redPlayers = gameManager.getRedPlayers()
    blackPlayers = gameManager.getBlackPlayers()
    gameManager.gameCompleted()
    gameManager.startGame(blackPlayers, redPlayers)
    gameManager.updateCurrentGameData()
    return render_template('game_page.html')

@socketio.on('game_completed')
def handleGameCompleted():
    gameManager.gameCompleted()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=Configuration.backendPort, debug=True, allow_unsafe_werkzeug=True)