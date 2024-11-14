import song
import database, playlist
from langchain_core.tools import tool
from typing import Annotated
from typing import Optional
from spotify_playlist import load_playlists_from_json, create_playlist_based_on_input, recommend_music_based_on_most_occuring_genre_in_playlist

db_connection = database.get_db_connection()
instance = playlist.Playlist(name='My Playlist', db_connection=db_connection)
song_history = []
@tool
def view_playlist() -> Annotated[str, "Contents of the playlist"]:
    """View playlist"""
    playlist = instance.view_playlist()
    return playlist

@tool
def add_song_by_artist_to_playlist(songname: str, artistname: Optional[str] = None) -> str:
    """Add song by artist name or empty artist name to playlist"""
    global song_history
    if artistname is None or artistname == "":
         songs_to_choose_from = database.get_song(songname, instance.get_most_occuring_genre())
         if songs_to_choose_from:
            song_details = [f" {i + 1}. Title: {song.name}, Artist: {song.artist}. " for i, song in enumerate(songs_to_choose_from)]
            song_history = songs_to_choose_from
            return f"Which song with name {songname} would you like to add to the playlist? I see that you like {instance.get_most_occuring_genre()}. Here are songs you can choose from:\n" + "\n".join(song_details)
    songs = database.get_song_by_name_and_artist(songname, artistname, instance.get_most_occuring_genre())
    if songs:
        if len(songs) == 1:
            print("SONGS: ",songs[0])
            success, song = instance.add_song(songs[0].name, songs[0].artist)
            song_history = []
            if success:
                return f'Added {song.name} by {song.artist} to playlist'
            else:
                return f'I was unable to add {songs[0].name} by {songs[0].artist} to playlist'
        song_details = [f" {i + 1}. Title: {song.name}, Artist: {song.artist}. " for i, song in enumerate(songs)]
        song_history = songs
        return f"Which song with name {songname} would you like to add to the playlist? I see that you like {instance.get_most_occuring_genre()}. Here are songs you can choose from:\n" + "\n".join(song_details)
    else:
        return f'Hmm... I was unable to add {songname} by {artistname} to playlist. It may already be in the playlist, or does not exist in the database. Try again.'

@tool 
def add_song_by_position(song_position: Annotated[int, "Position of the song in the playlist (1-based)"]) -> Annotated[str, "Result"]:
    """Add a song to the playlist either from the recommended history or song choices."""
    global song_history
    
    if not song_history:
        return "Error: No songs available in the history."
    print("Type of song history: ", type(song_history[0]))
    if isinstance(song_history[0], str):  
        song_entries = song_history[0].split(', ')

        if song_position < 1 or song_position > len(song_entries):
            return "Error: Position out of range in recommended history."

        song_entry = song_entries[song_position - 1]
        try:
            song_name, artist_name = song_entry.split(' by ')
        except ValueError:
            return "Error: Invalid song format in recommended history."

        song_history = []  
        success, songs = instance.add_song(song_name, artist_name)
        if success:
            return f"Added '{songs.name}' by {songs.artist} to the playlist at position {song_position}."
        else:
            return f"I couldn't add '{song_name}' by {artist_name} to the playlist at position {song_position}."
    
    elif isinstance(song_history[0], song.Song):  
        songs = song_history[song_position - 1]
        success, songen = instance.add_song(songs.name, songs.artist)
        song_history = [] 
        if success:
            return f'Added {songen.name} by {songen.artist} to playlist'
        else:
            return f'I couldn\'t add {songs.name} by {songs.artist} to the playlist'
    elif isinstance(song_history[0], list):  
        songs = song_history[0][song_position - 1]
        success, songen = instance.add_song(songs.name, songs.artist)
        song_history = [] 
        if success:
            return f'Added {songen.name} by {songen.artist} to playlist'
        else:
            return f'I couldn\'t add {songs.name} by {songs.artist} to the playlist'
    else:
        return "Error: Invalid song history format."

@tool
def remove_from_playlist(songname: Annotated[str, "SongName"], artistname: Annotated[str, "ArtistName"]) -> Annotated[str, "Result"]:
    """remove song by artist from playlist"""
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

@tool
def recommend_music() -> Annotated[str, "Result"]:
    """Recommend songs based on the current playlist."""
    recommendations = instance.recommend_music()
    global song_history
    song_history.append(recommendations)
    if not recommendations:
        return "I couldn't find any recommendations based on your playlist."
    
    return recommendations

@tool
def recommend_music_based_on_others_playlists()-> Annotated[str, "Result"]:
    """Recommend songs based on other playlists."""
    playlists = load_playlists_from_json()  
    global song_history
    recommendations = recommend_music_based_on_most_occuring_genre_in_playlist(instance, playlists)
    listen = []
    for rec in recommendations:
        songobject = song.Song(rec[0], rec[1], rec[2], rec[3], rec[4])
        listen.append(songobject)
    song_history.append(listen)
    if not recommendations:
        return "I couldn't find any recommendations based on your playlist and the other users' playlists."
    
    return [f" {i + 1}. Title: {song.name}, Artist: {song.artist}. " for i, song in enumerate(listen)]


@tool
def create_playlist_from_input(user_input: Annotated[str, "User input for categories to playlist creation and track limit that is optional"], trackLimit: Optional[int] = None) -> Annotated[str, "Result"]:
    """Create a playlist based on user input as categories and an optional tracklimit."""
    playlists = load_playlists_from_json()  
    track_limit_mapping = {
        "gym": 10,
        "car": 20,
        "car ride": 20,
        "workout": 18,
        "study": 7,
        "party": 15
    }

    if trackLimit is None:
        for key, limit in track_limit_mapping.items():
            if key in user_input.lower():
                trackLimit = limit
                break

    playlist_output = create_playlist_based_on_input(user_input, playlists, db_connection, trackLimit = None if trackLimit is None or trackLimit == "" else trackLimit)
    global instance
    instance.clear_playlist()
    instance = playlist_output
    
    return f"Here is your playlist with {trackLimit} songs, based on '{user_input}':\n{instance.view_playlist()}"