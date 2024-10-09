from dialoguekit.platforms import FlaskSocketPlatform
from sample_agents.parrot_agent import ParrotAgent

from agent import MusicBotAgent

platform = FlaskSocketPlatform(MusicBotAgent)
platform.start()

""" from flask import Flask
from flask_socketio import SocketIO, emit
import re
from flask_sqlalchemy import SQLAlchemy
import playlist
from datetime import datetime, timedelta
from uuid import uuid4
from models import db, Song, Album, Artist 
from flask_cors import CORS 
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///playlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, resources={r"/*": {"origins": "*"}})
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")
 """
""" def populate_music_data(db):
    try:
        # Create Artist objects
        artist1 = Artist(id=uuid4(), name="The Beatles")
        artist2 = Artist(id=uuid4(), name="Taylor Swift")
        artist3 = Artist(id=uuid4(), name="Kendrick Lamar")
        artist4 = Artist(id=uuid4(), name="Adele")
        artist5 = Artist(id=uuid4(), name="Ed Sheeran")
        
        db.session.add_all([artist1, artist2, artist3, artist4, artist5])
        
        # Create Album objects and link them to artists
        album1 = Album(id=uuid4(), name="Abbey Road", artist_id=artist1.id, release_year="1969")
        album2 = Album(id=uuid4(), name="1989", artist_id=artist2.id, release_year="2014")
        album3 = Album(id=uuid4(), name="To Pimp a Butterfly", artist_id=artist3.id, release_year="2015")
        album4 = Album(id=uuid4(), name="25", artist_id=artist4.id, release_year="2015")
        album5 = Album(id=uuid4(), name="Divide", artist_id=artist5.id, release_year="2017")
        
        db.session.add_all([album1, album2, album3, album4, album5])

        # Create Song objects and link them to albums
        song1 = Song(id=uuid4(), name="Come Together", album_id=album1.id, artist=artist1.name, length=datetime.strptime('00:04:20', '%H:%M:%S'))
        song2 = Song(id=uuid4(), name="Style", album_id=album2.id, artist=artist2.name, length=datetime.strptime('00:03:51', '%H:%M:%S'))
        song3 = Song(id=uuid4(), name="Alright", album_id=album3.id, artist=artist3.name, length=datetime.strptime('00:03:39', '%H:%M:%S'))
        song4 = Song(id=uuid4(), name="Hello", album_id=album4.id, artist=artist4.name, length=datetime.strptime('00:04:55', '%H:%M:%S'))
        song5 = Song(id=uuid4(), name="Shape of You", album_id=album5.id, artist=artist5.name, length=datetime.strptime('00:03:53', '%H:%M:%S'))
        song6 = Song(id=uuid4(), name="Something", album_id=album1.id, artist=artist1.name, length=datetime.strptime('00:03:03', '%H:%M:%S'))
        song7 = Song(id=uuid4(), name="Blank Space", album_id=album2.id, artist=artist2.name, length=datetime.strptime('00:03:51', '%H:%M:%S'))
        
        db.session.add_all([song1, song2, song3, song4, song5, song6, song7])

        # Commit the changes to the database
        db.session.commit()
        print("Data successfully populated!")
    except IntegrityError:
        db.session.rollback()
        print("Error occurred: Database constraint violation!") """

""" with app.app_context():
    populate_music_data(db)
    current_playlist = playlist.Playlist(name='My Playlist', songs=[f"({song.name} - {song.album.name} - {song.artist} - {song.length.strftime('%H:%M:%S')})" for song in Song.query.limit(5).all()]) 

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
    message_field = msg.get("message", "")
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
        print("Got message: ", msg)
        playlist_contents = current_playlist.view_playlist()
        emit('message', {
                    'message': {
                        'text': f"Current playlist: {playlist_contents}"
                    }
                })
        
    elif 'when' in msg_lower:
        match = re.search(r"when was album (.+?) released\??$", msg_lower, re.IGNORECASE)
        if match:
            album_name = match.group(1).strip()
            album = Album.query.filter(func.lower(Album.name) == album_name.lower()).first()
            emit('message', {
                'message': {
                    'text': f"Album {album.name} was released in {album.release_year} by {album.artist}"
                }
            })
    
    elif 'how' in msg_lower:
        match = re.search(r"how many albums has artist (.+?) released\??$", msg_lower, re.IGNORECASE)
        if match:
            artist_name = match.group(1).strip()
            artist = Artist.query.filter(func.lower(Artist.name) == artist_name.lower()).first()
            emit('message', {
                'message': {
                    'text': f"Artist {artist.name} has released {len(artist.albums)} album(s) named {artist.albums}"
                }
            })
    
    elif 'which' in msg_lower:
        match = re.search(r"which album features song (.+?)\??$", msg_lower, re.IGNORECASE)
        if match:
            song_name = match.group(1).strip()
            song = Song.query.filter(func.lower(Song.name) == song_name.lower()).first()
            emit('message', {
                'message': {
                    'text': f"Song {song.name} is featured in album {song.album}"
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
            "- When was album [album name] released?\n"
            "- How many albums has artist [artist name] released?\n"
            "- Which album features song [song name]?\n"
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

 """