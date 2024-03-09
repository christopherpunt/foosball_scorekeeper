from flask import render_template, Blueprint, jsonify, request
from player import PlayerManager
from helpers import *

players_blueprint = Blueprint('players', __name__)

playerManager = PlayerManager()

@players_blueprint.route('/')
def getAllPlayers():
    return render_template('/players.html', players=playerManager.getAllPlayers())

@players_blueprint.route('/add_user', methods=['POST'])
def addUser():
    json = requestToJson(request)
    result = playerManager.addNewPlayer(json.get('newUser', ''))
    if result:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': f'Could not add player'})