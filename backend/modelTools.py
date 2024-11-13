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
def add_song_without_specified_artist_playlist(songname: Annotated[str, "SongName without artist"]) -> Annotated[str, "Result"]:
    """add to playlist based on song, NO ARTIST."""
    songs_to_choose_from = database.get_song(songname)
    if songs_to_choose_from:
        # Creating a list of formatted song details
        song_details = [f"Title: {song.name}, Artist: {song.artist}" for song in songs_to_choose_from]
        # Joining the list into a single string
        return f"Success! Here are the songs:\n" + "\n".join(song_details)
    else:
        return "No songs found."