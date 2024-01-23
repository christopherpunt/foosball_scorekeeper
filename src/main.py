from configuration import Configuration
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from foosballGame import FoosballGameManager
from player import PlayerManager
from leaderboardStats import LeaderboardStats
from ledStripService import LedStripService
from datetime import datetime
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

gameStartedBy = None

def requestToJson(request):
    raw_data = request.data
    data_str = raw_data.decode('utf-8')
    return json.loads(data_str)

@app.route('/')
def index():
    stats = leaderboardStats.getAllStats()
    return render_template('leaderboard.html', all_stats=stats)

@app.route('/leaderboard')
def getLeaderboardStats():
    stats = leaderboardStats.getAllStats()
    return render_template('leaderboard.html', all_stats=stats)

@app.route('/leaderboard/player_stats')
def playerStats():
    stats = leaderboardStats.getPlayerStats()
    return render_template('leaderboard/player_stats.html', stats=stats)

@app.route('/leaderboard/team_stats')
def teamStats():
    stats = leaderboardStats.getTeamStats()
    return render_template('leaderboard/team_stats.html', stats=stats)

@app.route('/leaderboard/shortestGame_stats')
def shortestGame():
    stats = leaderboardStats.getShortestGames()
    return render_template('leaderboard/shortestGame_stats.html', stats=stats)

@app.route('/leaderboard/gameHistory_stats')
def gameHistory():
    stats = leaderboardStats.getRecentGameHistory()
    return render_template('leaderboard/gameHistory_stats.html', stats=stats)

@app.route('/leaderboard/bean_stats')
def teamBeans():
    stats = leaderboardStats.getTeamBeans()
    return render_template('leaderboard/bean_stats.html', stats=stats)

@app.route('/hiddenStats')
def hiddenStats():
    stats = leaderboardStats.getHiddenStats()
    return render_template('hiddenStats.html', hiddenStats=stats)

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
        remoteAddrStartedGame = request.remote_addr == gameStartedBy if gameStartedBy is not None else False
        return render_template('game_page.html', remoteAddrStartedGame=remoteAddrStartedGame)
    return joinGame()

@app.route('/start_game', methods=['POST'])
def start_game():
    global gameStartedBy
    gameStartedBy = request.remote_addr
    json = requestToJson(request)
    ledStripService.gameStarted()
    result = gameManager.startGame(json.get('RED'), json.get('BLACK'))
    if result:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': f'Could not start game'})


@app.route('/reset_game', methods=['POST'])
def reset_game():
    gameManager.currentGame = None
    return joinGame()


@app.route('/add_user', methods=['POST'])
def addUser():
    json = requestToJson(request)
    result = playerManager.addNewPlayer(json.get('newUser', ''))
    if result:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': f'Could not add player'})

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
        if returnValue:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': f'could not add score.'})
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
    ledStripService.setDarkMode(True)
    return render_template('settings.html')

@app.route('/lights_off', methods=['POST'])
def turnLightsOff():
    ledStripService.setDarkMode(False)
    return render_template('settings.html')

@app.route('/ping', methods=['POST'])
def handlePing():
    json = requestToJson(request)
    if 'averageValue' in json and 'team' in json:
        print(f"team: {json.get('team')} has averageValue: {json.get('averageValue')}")
    return jsonify({'success': True})

@socketio.on('get_initial_data')
def handle_get_initial_data():
    # Get the current server time
    server_time = datetime.now().isoformat()

    # Emit the server time to the client
    socketio.emit('server_time', {'server_time': server_time})
    gameManager.updateCurrentGameData()

@socketio.on('change_score')
def handle_change_score(data):
    if 'team' in data and 'action' in data:
        team = data['team']
        action = data['action']

        if gameStartedBy == request.remote_addr:
            if action == 'minus':
                gameManager.currentGame.removeScore(team.upper())
            elif action == 'plus':
                gameManager.currentGame.addScore(team.upper())
            else:
                print('incorrect action')
            gameManager.updateCurrentGameData()
        else:
            print(f"{request.remote_addr} tried to change the score")

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