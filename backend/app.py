from flask import Flask
from flask_socketio import SocketIO, emit
import re
import playlist

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

current_playlist = playlist.Playlist(name='My Playlist', songs=["song1", "song2", "song3"])

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
