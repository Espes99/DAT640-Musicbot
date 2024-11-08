from flask import Flask
from flask_socketio import SocketIO, emit
from ollama import *
from langchain_ollama import ChatOllama
import playlist
import database
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from typing import Annotated

db_connection = database.get_db_connection()
instance = playlist.Playlist(name='My Playlist', db_connection=db_connection)

@tool
def view_playlist() -> Annotated[str, "Contents of the playlist"]:
    """View playlist"""
    spillelisten = instance.view_playlist()
    print("view_playlist was called", spillelisten) 
    return spillelisten

@tool
def add_to_playlist(songname: Annotated[str, "SongName"], artistname: Annotated[str, "ArtistName"]) -> Annotated[str, "Result"]:
    """add to playlist."""
    instance.add_song(songname, artistname)
    return f'added {songname} by {artistname} to playlist'

@tool
def remove_from_playlist(songname: Annotated[str, "SongName"], artistname: Annotated[str, "ArtistName"]) -> Annotated[str, "Result"]:
    """remove from playlist."""
    instance.remove_song(songname, artistname)
    return f'removed {songname} by {artistname} from playlist'

@tool
def clear_the_playlist(tool_input: Annotated[None, "Clearing the playlist"]) -> Annotated[str, "Result"]:
    """clear the playlist."""
    instance.clear_playlist()
    print("view_playlist was called", tool_input) 
    return f'cleared the playlist'

@tool
def when_album_released(album_name: Annotated[str, "AlbumName"]) -> Annotated[str, "Result"]:
    """When was album released"""
    album = database.get_album_by_name(album_name)
    return f'Album {album[1]} wa released in {album[3]} by {album[5]}'

@tool
def how_albums_released_artist(artist_name: Annotated[str, "ArtistName"]) -> Annotated[str, "Result"]:
    """How many albums has artist released"""
    albums = database.get_albums_by_artist(artist_name)
    album_names = "', '".join([album[0] for album in albums])
    return f"Artist {artist_name} has released {len(albums)} albums named {album_names}"

@tool
def which_album_has_song(song_name: Annotated[str, "songName"]) -> Annotated[str, "Result"]:
    """Which album features this song"""
    albumName = database.get_albums_by_song(song_name)
    print(albumName)
    return f"Song {song_name} is featured in album {albumName[0]}"

@tool
def which_artist_released_song(song_name: Annotated[str, "songName"]) -> Annotated[str, "Result"]:
    """Which artist released this song"""
    artist = database.get_artist_by_song_name(song_name)
    return f"Artist for {song_name} is {artist[0]}"

@tool
def list_songs_album(album_name: Annotated[str, "albumName"]) -> Annotated[str, "Result"]:
    """List all songs in album [albumName]"""
    songs = database.get_songs_from_album_name(album_name)
    song_names = "', '".join([song[0] for song in songs])
    return f"Songs in album {album_name}: {song_names}"

@tool
def get_album_genre(album_name: Annotated[str, "albumName"]) -> Annotated[str, "Result"]:
    """Get album genre"""
    genre = database.get_genre_by_album_name(album_name)
    return f"The genre of album {album_name} is {genre[0]}"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

playlist_instance = playlist.Playlist(name='My Playlist', db_connection=db_connection)
tools = [view_playlist,
        add_to_playlist, 
        remove_from_playlist, 
        clear_the_playlist, 
        when_album_released, 
        how_albums_released_artist, 
        which_album_has_song, 
        which_artist_released_song, 
        list_songs_album,
        get_album_genre]

system_prompt = """
You are a music chatbot.
Rules:
    IMPORTANT: NEVER EVER DISPLAY ANY PYTHON, JAVASCRIPT, OR ANY CODE SNIPPETS OF THAT MATTER!
    IMPORTANT: If you do not completely understand the user input, respond with "I did not quite get that!"
    IMPORTANT: If the user input requests to display the playlist, view the playlist, show the playlist, list songs in the playlist, or any similar request, use the `view_playlist` tool ONLY and DO NOT generate any code snippets.
    IMPORTANT: You should execute the tool calls automatically, instead of suggesting how to call them in code.
    IMPORTANT: Always respond in natural language, giving a descriptive answer followed by a note about available tools, but avoid suggesting any form of code implementation.
"""

mistral_model = ChatOllama(
    model='mistral',
    temperature=0.8,
    system=system_prompt
).bind_tools(tools)

@app.route('/')
def index():
    return "Chatbot backend is running."

@socketio.on('connect')
def handle_connect():
    emit('message', {'message': {'text': "Welcome to the chat! What can I do for you?"}})

@socketio.on('message')
def handle_message(msg):
    message_field = msg.get("message", "")
    msg_lower = message_field.lower()
    print(msg_lower)
    try:
        response = mistral_model.invoke([HumanMessage(content=msg_lower)])
        print("Model response:", response)
        tool_calls = response.response_metadata.get("message", {}).get("tool_calls", [])
        if tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call['function'].get("name")
                tool_input = tool_call['function']['arguments']
                for tool in tools:
                    print("HEISAAAA: ", tool.name)
                    print("BLUSHI: ", tool_name)
                    print("BLUSHI: ", tool_input)
                    if tool.name == tool_name: 
                        result = tool.invoke( tool_input)
                        emit('message', {'message': {'text': result}})
                        return
        print()
        emit('message', {'message': {'text': response.content or "Ask me about a playlist."}})
    except Exception as e:
        print("Error invoking model or tool:", e)
        emit('message', {'message': {'text': "Something went wrong."}})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True)