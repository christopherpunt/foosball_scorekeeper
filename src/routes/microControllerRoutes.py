from flask import Flask, render_template, Blueprint, jsonify, request
from leaderboardStats import LeaderboardStats
from helpers import *

microController_blueprint = Blueprint('microController', __name__)

# the goal counters / controllers need to register first before we can start a game
@microController_blueprint.route('/register_goal_counter', methods=['POST'])
def registerGoalCounter():
    json = requestToJson(request)
    team = json.get('team')
    controllerIp = json.get('controllerIp')
    return jsonify({'success': True})

@microController_blueprint.route('/ping', methods=['POST'])
def handlePing():
    json = requestToJson(request)
    if 'averageValue' in json and 'team' in json:
        print(f"team: {json.get('team')} has averageValue: {json.get('averageValue')}")
    return jsonify({'success': True})