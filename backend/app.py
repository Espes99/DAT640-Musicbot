# app.py
from flask import Flask
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return "Backend is running."

@socketio.on('message')
def handle_message(data):
    print('Received message: ' + str(data))
    send('Message received: ' + data, broadcast=True)

@socketio.on('custom_event')
def handle_custom_event(json_data):
    print('Received json: ' + str(json_data))
    emit('response', {'data': 'Custom event received'}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
