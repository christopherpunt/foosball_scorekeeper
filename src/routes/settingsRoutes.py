from flask import Flask, render_template, Blueprint, jsonify, request
from ledStripService import LedStripService
from configuration import Configuration
from helpers import *

settings_blueprint = Blueprint('settings', __name__)

ledStripService = LedStripService(Configuration.ledStripControllerUrl)

@settings_blueprint.route('/')
def settings():
    return render_template('settings.html')

@settings_blueprint.route('/lights_on', methods=['POST'])
def turnLightsOn():
    ledStripService.setDarkMode(True)
    return render_template('settings.html')

@settings_blueprint.route('/lights_off', methods=['POST'])
def turnLightsOff():
    ledStripService.setDarkMode(False)
    return render_template('settings.html')