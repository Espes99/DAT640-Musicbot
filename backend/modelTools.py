import database, playlist
from langchain_core.tools import tool
from typing import Annotated

db_connection = database.get_db_connection()
instance = playlist.Playlist(name='My Playlist', db_connection=db_connection)

@tool
def view_playlist() -> Annotated[str, "Contents of the playlist"]:
    """View playlist"""
    playlist = instance.view_playlist()
    return playlist

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