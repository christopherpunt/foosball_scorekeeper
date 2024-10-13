from flask import render_template, Blueprint, request, redirect, url_for
from ledStripService import LedStripService
from configuration import Configuration
from helpers import *

settings_blueprint = Blueprint('settings', __name__)

ledStripService = LedStripService(Configuration.ledStripControllerUrl)

@settings_blueprint.route('/')
def settings():
    return render_template('settings.html', leaderboard_history=Configuration.leaderboardHistory)

@settings_blueprint.route('/lights_on', methods=['POST'])
def turnLightsOn():
    ledStripService.setDarkMode(True)
    return render_template('settings.html')

@settings_blueprint.route('/lights_off', methods=['POST'])
def turnLightsOff():
    ledStripService.setDarkMode(False)
    return render_template('settings.html')

@settings_blueprint.route('/save_leaderboard_history', methods=['POST'])
def save_leaderboard_history():
    new_history_count = int(request.form.get('historyCount'))
    Configuration.leaderboardHistory = new_history_count
    return redirect(url_for('settings.settings'))
