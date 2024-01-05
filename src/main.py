from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from foosballGame import FoosballGameManager
from player import PlayerManager
from leaderboardStats import LeaderboardStats
import json

app = Flask(__name__)
socketio = SocketIO(app)

# serve the socket.io js file as static content
static_files = {
    '/static' : './static'
}

gameManager = FoosballGameManager(socketio)
playerManager = PlayerManager(socketio)
leaderboardStats = LeaderboardStats()

def requestToJson(request):
    raw_data = request.data
    data_str = raw_data.decode('utf-8')
    return json.loads(data_str)

@app.route('/')
def index():
    stats = leaderboardStats.getStats()
    print(stats)
    return render_template('leaderboard.html', stats=stats)

@app.route('/players')
def getAllPlayers():
    return render_template('/players.html', players=playerManager.getAllPlayers())

@app.route('/join_game')
def joinGame():
    return render_template('join_game.html', players=playerManager.getAllPlayers())

@app.route('/start_game', methods=['POST'])
def start_game():
    json = requestToJson(request)
    return gameManager.startGame(json.get('RED'), json.get('BLACK'))

@app.route('/add_user', methods=['POST'])
def addUser():
    return playerManager.addNewPlayer(request)

@app.route('/game_page')
def game_page():
    if gameManager.currentGame is not None:
        return render_template('game_page.html')
    return joinGame()

@app.route('/add_score', methods=['POST'])
def addScore():
    team_value = requestToJson(request).get('team')
    print(f'Team {team_value} scored a goal!')
    returnValue = gameManager.currentGame.addScore(team_value)
    gameManager.updateCurrentGameData()
    return returnValue

# the goal counters / controllers need to register first before we can start a game
@app.route('/register_goal_counter', methods=['POST'])
def registerGoalCounter():
    json = requestToJson(request)
    team = json.get('team')
    controllerIp = json.get('controllerIp')
    return jsonify({'success': True})

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
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)