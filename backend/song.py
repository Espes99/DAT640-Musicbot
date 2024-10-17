class Song:
    def __init__(self, song_id, name, album_id, artist, length):
        self.song_id = song_id
        self.name = name
        self.album_id = album_id
        self.artist = artist
        self.length = length

    def __str__(self):
        return f'{self.name} by {self.artist}'

    def get_details(self):
        return {
            'id': self.song_id,
            'name': self.name,
            'album_id': self.album_id,
            'artist': self.artist,
            'length': self.length
        }
    
    #Added to override default method when comparing objects in python
    def __eq__(self, other):
        if isinstance(other, Song):
            return self.song_id == other.song_id
        return False

    def __hash__(self):
        return hash(self.song_id)
