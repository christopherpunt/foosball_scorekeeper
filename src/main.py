from flask import Flask, render_template, request, jsonify, Response, url_for
from flask_socketio import SocketIO
from foosballGame import FoosballGameManager
from player import PlayerManager
from database import db
from threading import Thread, Event
import datetime
import json
import time
import cv2
import os


app = Flask(__name__)
socketio = SocketIO(app)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

# create tables in database if they don't exist
with app.app_context():
    db.create_all()

gameManager = FoosballGameManager(socketio)
playerManager = PlayerManager(socketio)

video_buffer = []
video_capture_active = False
stop_recording_event = Event()
video_thread = None

# Set the maximum number of frames to store in the circular buffer
MAX_BUFFER_SIZE = 100

@app.route('/')
def index():
    redTeamPlayers = playerManager.getAllPlayers()
    blackTeamPlayers = playerManager.getAllPlayers()
    return render_template('join_game.html', redTeamPlayers=redTeamPlayers, blackTeamPlayers=blackTeamPlayers)

@app.route('/new_game')
def newGame():
    stop_video_capture_thread()

    gameManager.newGame()
    return index()

@app.route('/start_game', methods=['POST'])
def start_game():
    if gameManager.isCurrentGameReady():
        start_video_capture_thread()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/add_user', methods=['POST'])
def addUser():
    return playerManager.addNewPlayer(request, gameManager.currentGame)

@app.route('/game_page')
def game_page():
    return render_template('game_page.html')

@app.route('/add_score', methods=['POST'])
def addScore():
    # Get the raw bytes from the request
    raw_data = request.data
    data_str = raw_data.decode('utf-8')
    data = json.loads(data_str)
    team_value = data.get('team')

    returnValue = gameManager.currentGame.addScore(team_value)
    gameManager.updateCurrentGameData()

    # Save the last 10 seconds of video to a file
    video_filename = save_last_10_seconds_video()
    video_path = url_for('static', filename=f'videos/{video_filename}')

    # Broadcast the video feed to clients with the video path
    socketio.emit('replay_video', {'new_score_added': True, 'video_path': video_path}, namespace='/')


    return returnValue


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

        # Save the last 10 seconds of video to a file
        video_filename = save_last_10_seconds_video()
        video_path = url_for('static', filename=f'videos/{video_filename}')

        # Broadcast the video feed to clients with the video path
        socketio.emit('replay_video', {'new_score_added': True, 'video_path': video_path})

@socketio.on('update_player')
def handle_update_player(data):
    playerManager.updatePlayers(data, gameManager.currentGame)

# Function to start video capture on a separate thread
def start_video_capture_thread():
    global video_thread
    video_thread = Thread(target=start_video_capture)
    video_thread.start()

def start_video_capture():
    global video_buffer, video_capture_active

    cap = cv2.VideoCapture(0)  # Adjust camera index as needed
    video_capture_active = True

    while video_capture_active:
        ret, frame = cap.read()
        timestamp = time.time()
        frame_with_timestamp = (frame, timestamp)

        # Append the frame to the circular buffer
        video_buffer.append(frame_with_timestamp)

        # Limit the buffer size to MAX_BUFFER_SIZE
        if len(video_buffer) > MAX_BUFFER_SIZE:
            video_buffer.pop(0)

        # Sleep to control the frame rate (adjust as needed)
        time.sleep(0.05)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def stop_video_capture_thread():
    global video_capture_active, stop_recording_event, video_thread

    # Set the event to signal the recording thread to stop
    stop_recording_event.set()
    video_capture_active = False  # Set the flag to stop the while loop

    # Wait for the recording thread to finish
    if video_thread is not None and video_thread.is_alive():
        video_thread.join()

def save_last_10_seconds_video():
    global video_buffer

    # Create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_filename = f'output_video{datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.mp4'
    output_path = os.path.join('src', 'static', 'videos', output_filename)
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))  # Adjust parameters as needed

    # Write the frames from the last 10 seconds to the video file
    for frame, _ in video_buffer:
        out.write(frame)

    out.release()
    video_buffer = []  # Clear the video buffer after saving

    # Print the full path to the saved video
    print(f"Video saved to: {os.path.abspath(output_path)}")

    return output_filename

def generate_video_frames():
    global video_buffer, stop_recording_event

    while not stop_recording_event.is_set():
        if len(video_buffer) > 0:
            # Get the latest frame from the circular buffer
            _, jpeg = cv2.imencode('.jpg', video_buffer[-1][0])
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        # Sleep to control the frame rate (adjust as needed)
        time.sleep(0.05)

    # Release the video stream when the event is set
    cv2.destroyAllWindows()

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)