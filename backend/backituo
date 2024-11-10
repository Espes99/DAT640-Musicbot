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
    success, song = instance.add_song(songname, artistname)
    if success:
        return f'Success! I have added {song.name} by {song.artist} to playlist'
    else:
        return f'Hmm... I was unable to add {songname} by {artistname} to playlist. It may already be in the playlist, or does not exist in the database. Try again.'

@tool
def remove_from_playlist(songname: Annotated[str, "SongName"], artistname: Annotated[str, "ArtistName"]) -> Annotated[str, "Result"]:
    """remove from playlist."""
    success, song = instance.remove_song(songname, artistname)
    if success:
        return f'Removed {song.name} by {song.artist} from playlist'
    else:
        return f'I was unable to remove {songname} by {artistname} from playlist'

@tool
def clear_the_playlist() -> Annotated[str, "Result"]:
    """clear the playlist."""
    success = instance.clear_playlist()
    print("view_playlist was called") 
    if success:
        return f'Cleared your playlist'
    else:
        return 'I was unable to clear you playlist, maybe there are no songs in your playlist to clear?'

@tool
def when_album_released(album_name: Annotated[str, "AlbumName"]) -> Annotated[str, "Result"]:
    """When was album released"""
    album = database.get_album_by_name(album_name)
    if album:
        if album[3] == "Unknown Release Date":
            return f'Album {album[1]}  by {album[5]} has an uknown release date, due to our source of music api.'
        else:
            return f'Album {album[1]} was released in {album[3]} by {album[5]}'
    else:
        return f'I was unable to find {album_name} in the database.'

@tool
def how_albums_released_artist(artist_name: Annotated[str, "ArtistName"]) -> Annotated[str, "Result"]:
    """How many albums has artist released"""
    albums = database.get_albums_by_artist(artist_name)
    if len(albums) == 1:
        return f"Artist {artist_name} has released 1 album named {albums[0][0]}"
    elif len(albums) > 1:
        album_names = "', '".join([album[0] for album in albums])
        return f"Artist {artist_name} has released {len(albums)} albums named {album_names}"
    else:
        return f"Artist {artist_name} has not released any albums according to our database."

@tool
def which_album_has_song(song_name: Annotated[str, "songName"]) -> Annotated[str, "Result"]:
    """Which album features this song"""
    albumName = database.get_albums_by_song(song_name)
    if albumName:
        return f"Song {song_name} is featured in album {albumName[0]}"
    else:
        return f"Song {song_name} is not featured in any albums according to our database."

@tool
def which_artist_released_song(song_name: Annotated[str, "songName"]) -> Annotated[str, "Result"]:
    """Which artist released this song"""
    artist = database.get_artist_by_song_name(song_name)
    if artist:
        return f"Artist for {song_name} is {artist[0]}"
    else:
        return f"Song {song_name} does not have an artist associated with it according to our database."

@tool
def list_songs_album(album_name: Annotated[str, "albumName"]) -> Annotated[str, "Result"]:
    """List all songs in album [albumName]"""
    songs = database.get_songs_from_album_name(album_name)
    if songs:
        song_names = "', '".join([song[0] for song in songs])
        return f"Songs in album {album_name}: {song_names}"
    else:
        return f"No songs found in album {album_name}"

@tool
def get_album_genre(album_name: Annotated[str, "albumName"]) -> Annotated[str, "Result"]:
    """Get album genre"""
    genre = database.get_genre_by_album_name(album_name)
    if genre:
        if genre[0] == "Unknown Genre":
            return f"I do not have information about the genre of album {album_name}"
        else:
            return f"The genre of album {album_name} is {genre[0]}"
    else:
        return f"I was unable to find the genre of album {album_name} in our database."
    
@tool
def remove_first_n_songs(n: Annotated[int, "Number of songs to remove from the beginning"]) -> Annotated[str, "Result"]:
    """Remove the first N songs from the playlist."""
    for i in range(n):
        if not instance.remove_song_by_position(0):
            return f"Could not remove the {i+1}th song from the playlist."
    return f"Successfully removed the first {n} songs from the playlist."

@tool
def remove_last_song() -> Annotated[str, "Result"]:
    """Remove the last song from the playlist."""
    if not instance.remove_song_by_position(len(instance.songs) - 1):
        return "Could not remove the last song from the playlist."
    return "Successfully removed the last song from the playlist."

@tool
def get_song_by_position(position: Annotated[int, "Position of the song in the playlist (1-based)"]) -> Annotated[str, "Result"]:
    """Get song details by its position in the playlist."""
    song = instance.get_song_by_position(position - 1) 
    if song:
        return f"The song at position {position} is '{song.name}' by {song.artist}."
    else:
        return f"There is no song at position {position} in the playlist."
    
# @tool
# def what_genre_of_song_by_position(position: Annotated[int, "Position of the song in the playlist (1-based)"]) -> Annotated[str, "Result"]:
#     """Get duration of the song by its position."""
#     song = instance.get_song_by_position(position - 1)  
#     if song:
#         song = instance.get_song_by_position(song.name)
#         song_genre = database.get_genre_by_album_name(song.album)
#         if song_genre:
#             return f"The song '{song.name}' by {song.artist} has genre {song_genre}."
#         else:
#             return f"Genre for '{song.name}' by {song.artist} is unknown."
#     else:
#         return f"There is no song at position {position} in the playlist."

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
used_tools = []
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
        get_album_genre,
        remove_first_n_songs,
        remove_last_song,
        get_song_by_position] 


tool_descriptions = {
    "view_playlist": "View the current playlist with details of each song.",
    "add_to_playlist": "Add a song to the playlist by specifying the song name and artist.",
    "remove_from_playlist": "Remove a specific song from the playlist.",
    "clear_the_playlist": "Clear all songs from the playlist.",
    "when_album_released": "Find out when a specific album was released.",
    "how_albums_released_artist": "Get the number of albums released by a specific artist.",
    "which_album_has_song": "Find which album a specific song is featured in.",
    "which_artist_released_song": "Find which artist released a specific song.",
    "list_songs_album": "List all songs in a specific album.",
    "get_album_genre": "Get the genre of a specific album.",
    "remove_first_n_songs": "Remove the first N songs from the playlist.",
    "remove_last_song": "Remove the last song from the playlist.",
    "get_song_by_position": "Get details of a song at a specific position in the playlist.",
    "when_was_song_released_by_position": "Get the release date of the song at a specific position in the playlist."
}

system_prompt = """
You are a Music Recommendation System chatbot. You have no name, you're just a Music Recommendation Chat, which provides users with tools like managing playlists and music information.
Your primary function is to assist users in managing a singular playlist. 
When adding a song to the playlist, you must use the exact artist name and song name as entered, even if there are accents, special characters, or capitalization. 
Ensure that you pass the input as-is to the relevant tools.
When a user requests information about their playlist, you must use the `view_playlist` tool exclusively to retrieve and display the contents of the playlist, NEVER respond with a simulated playlist. 
You are not allowed to provide any code snippets, use any programming languages, or suggest any implementation details. 
Consistently reply using natural language, offering a comprehensive response about the playlist, 
and mention the available tools without implying any code execution. 
If the user input is unclear, respond with "I did not quite get that!" 
Ensure that you follow the defined rules strictly and maintain a focus on user interaction without any technical jargon.
Never follow up with any questions unrelated to the provided tools.
Always at the end of each response, provide additional information about the available tools.

Playlist now supports positional references! You can:
- Remove songs by their position in the playlist (e.g., remove the first 3 songs).
- Remove the last song in the playlist.

These new options will enhance your interaction with the playlist.
"""
mistral_model = ChatOllama(
    model='mistral-nemo',
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