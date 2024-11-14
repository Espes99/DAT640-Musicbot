from typing import Annotated
import database
from langchain_core.tools import tool
import random

class Playlist:
    def __init__(self, name, db_connection):
        self.name = name
        self.songs = []
        self.db_connection = db_connection
        self.songs = database.populate_playlist()

    def add_song_no_artist(self, song_name):
        song = database.get_song_by_name(song_name)
        if song:
            if song not in self.songs:
                self.songs.append(song)
                return True, song
            else:
                return False, song
        else:
            return False, song
        
    def add_song(self, song_name, artist_name):
        songs = database.get_song_by_name_and_artist(song_name, artist_name)
        if len(songs) > 0:
            if songs[0] not in self.songs:
                self.songs.append(songs[0])
                return True, songs[0]
            else:
                return False, songs[0]
        else:
            return False, songs[0]
        
    def remove_song(self, song_name, artist_name):
        songs = database.get_song_by_name_and_artist(song_name, artist_name)
        if songs:
            if songs[0] in self.songs:
                self.songs.remove(songs[0])
                return True, songs[0]
            else:
                return False, songs[0]
        else:
            return False, songs[0]
    
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
        
    def get_song_by_position(self, position: int):
        if position < 0 or position >= len(self.songs):
            return None
        return self.songs[position]
    
    def remove_song_by_position(self, position: int):
        if position < 0 or position >= len(self.songs):
            return False
        del self.songs[position]
        return True
    
    def recommend_music(self):
        if not self.songs:
            return "Your playlist is empty, so I cannot recommend music based on it."
        
        recommendations = set()
        
        for song in self.songs:
            album = database.get_album_by_id(song.album_id)
            artist_name = database.get_artist_by_id(album[2])
            if album:
                genre = album[4] 
                release_year = album[3]  
                
                recommendations.update(self._get_recommendations(artist_name, genre, release_year))
                
            if len(recommendations) >= 10:
                break

        if not recommendations:
            return "I couldn't find any recommendations based on your playlist."

        return ', '.join([f'{song.name} by {song.artist}' for song in recommendations])

    def _get_recommendations(self, artist_name, genre, release_year):
        artist_songs = database.get_songs_by_artist(artist_name)
        genre_songs = database.get_songs_by_genre(genre) if genre != "Unknown Genre" or genre != "" else []
        year_songs = database.get_songs_by_year(release_year) if release_year != "Unknown Release Date" or release_year != "" else []
        
        recommendations = set(artist_songs + genre_songs + year_songs)
        recommendations = [song for song in recommendations if song not in self.songs]

        final_recommendations = []

        if artist_songs:
            random_artist_song = random.choice(artist_songs)
            final_recommendations.append(random_artist_song)
            print(f"Selected {random_artist_song.name} by {random_artist_song.artist} based on the same artist: {artist_name}")

        if genre_songs:
            random_genre_song = random.choice(genre_songs)
            final_recommendations.append(random_genre_song)
            print(f"Selected {random_genre_song.name} by {random_genre_song.artist} based on the same genre: {genre}")

        if year_songs:
            random_year_song = random.choice(year_songs)
            final_recommendations.append(random_year_song)
            print(f"Selected {random_year_song.name} by {random_year_song.artist} based on the release year: {release_year}")

        remaining_slots = random.randint(2, 7)
        remaining_recommendations = list(set(recommendations) - set(final_recommendations))
        random.shuffle(remaining_recommendations)
        final_recommendations.extend(remaining_recommendations[:remaining_slots])

        for song in remaining_recommendations[:remaining_slots]:
            print(f"Added {song.name} by {song.artist} to fill the remaining slots in the recommendation list.")

        return final_recommendations[:random.randint(5, 10)]
    

    def add_song_from_creation(self, song_name: str, artist_name, song_length):
        song = database.get_song_or_add_song(song_name, artist_name, song_length)
        if song:
            if song not in self.songs:
                self.songs.append(song)
                return True, song
            else:
                print(f"Song '{song_name}' by '{artist_name}' already exists in the playlist.")
                return False, song
        else:
            print(f"I couldn't find or add '{song_name}' by '{artist_name}' to the playlist.")
            return False, song
        
    def get_most_occuring_genre(self):
        genres = [database.get_album_by_id(song.album_id)[4] for song in self.songs]
        return max(set(genres), key = genres.count)