class Playlist:
    def __init__(self, name, songs):
        self.name = name
        self.songs = songs

    def add_song(self, song):
        song = song.lower()
        if song not in self.songs:
            self.songs.append(song)
            return True
        else:
            return False
        
    def remove_song(self, song):
        if song in self.songs:
            self.songs.remove(song)
            return True
        else:
            return False
        
    def view_playlist(self):
        if self.songs:
            return '\n' + '\n'.join(self.songs)
        else:
            return 'Your playlist is empty.'
        
    def clear_playlist(self):
        self.songs.clear()
        length = len(self.songs)
        if length == 0:
            return 'Your playlist has been cleared.'
        else:
            return 'Clearing failed, or playlist was already empty'