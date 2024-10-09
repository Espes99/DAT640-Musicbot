import database

class Playlist:
    def __init__(self, name, db_connection):
        self.name = name
        self.songs = []
        self.db_connection = db_connection
        self.songs.append(database.get_song_by_name('here comes the sun'))
        print(len(self.songs))

    def add_song(self, song_name):
        song = database.get_song_by_name(song_name)
        if song:
            if song not in self.songs:
                self.songs.append(song)
                return True
            else:
                return False 
        else:
            return False
        
    def remove_song(self, song_name):
        song = database.get_song_by_name(song_name)
        if song:
            if song in self.songs:
                self.songs.remove(song)
                return True
            else:
                return False
        else:
            return False
        
    def view_playlist(self):
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