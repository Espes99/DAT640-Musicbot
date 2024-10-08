from flask import Flask
from flask_socketio import SocketIO, emit
import re
from flask_sqlalchemy import SQLAlchemy
import playlist
from datetime import datetime, timedelta
from uuid import uuid4
from models import db, Song, Album, Artist 
from flask_cors import CORS 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///playlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, resources={r"/*": {"origins": "*"}})
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

with app.app_context():
    current_playlist = playlist.Playlist(name='My Playlist', songs=[song.name for song in Song.query.limit(5).all()]) 

@app.route('/')
def index():
    return "Chatbot backend is running."
        
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('message', {
        'message': {
            'text': "Welcome to the chat! What can I do for you?"
        }
    })


@socketio.on('message')
def handle_message(msg):
    print("Got message: ", msg)
    message_field = msg.get("message", "")  # Extract the "message" field with a default empty string
    msg_lower = message_field.lower()

    if 'add' in msg_lower:
        match = re.search(r"add ['\"]?(.+?)['\"]?(?: to the playlist)?$", msg_lower)
        if match:
            song_name = match.group(1)
            if current_playlist.add_song(song_name):
                emit('message', {
                    'message':{
                        'text': f"Added '{song_name}' to the playlist."}
                    })
            else:
                emit('message', {
                    'message':{
                        'text': f"'{song_name}' already in the playlist."}
                    })
        else:
            emit('message', {
                'message':{ 
                'text': "Please specify the song to add."}
                })

    elif 'remove' in msg_lower:
        match = re.search(r"remove ['\"]?(.+?)['\"]?(?: from the playlist)?$", msg_lower)
        if match:
            song_name = match.group(1)
            if current_playlist.remove_song(song_name):
                emit('message', {
                    'message':{
                        'text': f"Removed '{song_name}' from the playlist."}
                    })
            else:
                emit('message', {
                    'message': {
                        'text': f"'{song_name}' is not in the playlist."}
                    })
        else:
            emit('message', {
                'message': {
                    'text': "Please specify the song to remove."}
                })

    elif 'view playlist' in msg_lower or 'get' in msg_lower:
        playlist_contents = current_playlist.view_playlist()
        emit('message', {
                    'message': {
                        'text': f"Current playlist: {playlist_contents}"
                    }
                })


    elif 'clear playlist' in msg_lower:
        current_playlist.clear_playlist()
        emit('message', {
                    'message': {
                        'text': "Playlist has been cleared."
                    }
                })

    elif 'list' in msg_lower:
        commands_list = (
            "Available commands:\n"
            "- Add [song name] to the playlist\n"
            "- Remove [song name] from the playlist\n"
            "- View playlist\n"
            "- Clear playlist\n"
            "- List commands"
        )
        emit('message', {
            'message':{
                'text': commands_list}
            })

    else:
        emit('message', {
            'message': {
                'text': "Sorry, I did not understand that command."}
                         })

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True)

