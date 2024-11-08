from typing import Annotated
import database
from langchain_core.tools import tool

class Playlist:
    def __init__(self, name, db_connection):
        self.name = name
        self.songs = []
        self.db_connection = db_connection
        self.songs = database.populate_playlist()

    def add_song(self, song_name, artist_name):
        song = database.get_song_by_name(song_name, artist_name)
        if song:
            if song not in self.songs:
                self.songs.append(song)
                return True, song
            else:
                return False, song
        else:
            return False, song
        
    def remove_song(self, song_name, artist_name):
        song = database.get_song_by_name(song_name, artist_name)
        if song:
            if song in self.songs:
                self.songs.remove(song)
                return True, song
            else:
                return False, song
        else:
            return False, song
    
    def view_playlist(self):
        """View the details of all songs in the playlist."""
        if self.songs:
            playlist_details = []
            for song in self.songs:
                playlist_details.append(f'{song.name} by {song.artist} ({song.length})')
            return ', '.join(playlist_details)
        else:
            return 'Your playlist is empty.'
        
    def clear_playlist(self):
        self.songs.clear()
        length = len(self.songs)
        if length == 0:
            return True
        else:
            return False