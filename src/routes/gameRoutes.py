from flask import Flask, render_template, Blueprint, jsonify, request
from socketioManager import socketio
from configuration import Configuration
from foosballGame import FoosballGameManager
from player import PlayerManager
from leaderboardStats import LeaderboardStats
from ledStripService import LedStripService
from datetime import datetime
from helpers import *

game_blueprint = Blueprint('game', __name__)

gameManager = FoosballGameManager(socketio)
playerManager = PlayerManager()
leaderboardStats = LeaderboardStats()
ledStripService = LedStripService(Configuration.ledStripControllerUrl)

gameStartedBy = None

@game_blueprint.route('/join_game')
def joinGame():
    return render_template('join_game.html', 
                           players=playerManager.getPlayersSortedByTotalGames(
                               leaderboardStats.getPlayersSortedByGamesPlayed()), 
                           defaultPlayersCount=Configuration.defaultJoinGamePlayersCount)

@game_blueprint.route('/game_page')
def game_page():
    if gameManager.currentGame is not None:
        remoteAddrStartedGame = request.remote_addr == gameStartedBy if gameStartedBy is not None else False
        return render_template('game_page.html', remoteAddrStartedGame=remoteAddrStartedGame)
    return joinGame()

@game_blueprint.route('/start_game', methods=['POST'])
def start_game():
    global gameStartedBy
    gameStartedBy = request.remote_addr
    json = requestToJson(request)
    ledStripService.gameStarted()
    result = gameManager.startGame(json.get('RED'), json.get('BLACK'))
    if result:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': f'Could not start game'})


@game_blueprint.route('/reset_game', methods=['POST'])
def reset_game():
    gameManager.currentGame = None
    return joinGame()

@game_blueprint.route('/add_score', methods=['POST'])
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
    socketio.emit('redirect_to_leaderboard')