from configuration import Configuration
from flask import Flask, redirect, url_for
from socketioManager import socketio
from routes.playersRoutes import players_blueprint
from routes.settingsRoutes import settings_blueprint
from routes.leaderboardRoutes import leaderboard_blueprint
from routes.microControllerRoutes import microController_blueprint
from routes.gameRoutes import game_blueprint

# Load configuration on application startup
Configuration.load_configuration()

app = Flask(__name__)
socketio.init_app(app)

# serve the socket.io js file as static content
static_files = {
    '/static' : './static'
}

# register route blueprints
app.register_blueprint(players_blueprint, url_prefix='/players')
app.register_blueprint(settings_blueprint, url_prefix='/settings')
app.register_blueprint(leaderboard_blueprint, url_prefix='/leaderboard')
app.register_blueprint(microController_blueprint)
app.register_blueprint(game_blueprint)

@app.route('/')
def index():
    return redirect(url_for('leaderboard.getLeaderboardStats'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=Configuration.backendPort, debug=True, allow_unsafe_werkzeug=True)