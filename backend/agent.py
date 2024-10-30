from dialoguekit.participant.agent import Agent
from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.participant import DialogueParticipant
import re
import database
import playlist
import sqlite3
import os

db_connection = database.get_db_connection()
class MusicBotAgent(Agent):
    def __init__(self, agent_id: str = "music-bot"):
        super().__init__(agent_id)
        self.db_connection = database.get_db_connection()
        self.songs = self.get_all_songs()
        self.current_playlist = playlist.Playlist(name='My Playlist', db_connection=db_connection)
        self.HELP_MESSAGE = """Available commands:
                            - 'add [song name]': Adds a song to the playlist.
                            - 'remove [song name]': Removes a song from the playlist.
                            - 'view playlist': Displays the current playlist.
                            - 'clear playlist': Clears the entire playlist.
                            - 'exit': Exits the chat."""


    def get_all_songs(self, limit=2):
        with sqlite3.connect(os.path.join('data', 'music.db')) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT name, artist, length FROM song LIMIT ?', (limit,))
            rows = cursor.fetchall()
            songs = []
            for row in rows:
                name, artist, length = row
                songs.append((name, artist, length))
            return songs
    
    def get_song(self):
        with sqlite3.connect(os.path.join('data', 'music.db')) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT name FROM song LIMIT 1') 
            song = cursor.fetchone()
            return song
    
    def get_album_by_name(self, album_name):
        with sqlite3.connect(os.path.join('data', 'music.db')) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                SELECT album.*, artist.name AS artist_name
                FROM album
                JOIN artist ON album.artist_id = artist.id
                WHERE LOWER(album.name) = LOWER(?)
            ''', (album_name,))
            album = cursor.fetchone()
            print("result:", album)
            return album if album else None
        
    def get_albums_by_artist(self, artist_name):
        with sqlite3.connect(os.path.join('data', 'music.db')) as connection:
            cursor = connection.cursor()
            cursor.execute('''
            SELECT id FROM artist WHERE LOWER(name) = LOWER(?)
            ''', (artist_name,))
            artist = cursor.fetchone()
            if artist:
                artist_id = artist[0]
                cursor.execute('''
                    SELECT name FROM album WHERE artist_id = ?
                ''', (artist_id,))
                albums = cursor.fetchall()
                return [album[0] for album in albums]
            else:
                return []
    
    def get_albums_by_song(self, song_name):
        with sqlite3.connect(os.path.join('data', 'music.db')) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                SELECT album.name 
                FROM song
                JOIN album ON song.album_id = album.id
                WHERE LOWER(song.name) = LOWER(?);
            ''', (song_name,))
            album = cursor.fetchone()
            return album
    
    def welcome(self) -> None:
        """Sends the agent's welcome message."""
        utterance = AnnotatedUtterance(
            "Welcome to the chat! What can I do for you? Type 'help' for more information.",
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)
    
    def goodbye(self) -> None:
        """Sends the agent's goodbye message."""
        utterance = AnnotatedUtterance(
            "It was nice talking to you. Bye",
            intent=self.stop_intent,
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def receive_utterance(self, utterance: Utterance) -> None:
        """Gets called each time there is a new user utterance.

        If the received message is "EXIT" it will close the conversation.

        Args:
            utterance: User utterance.
        """

        utterance_lower = utterance.text.lower()
        song_response = "Sorry, I couldn't do anything about that."
        if utterance_lower == "exit":
            self.goodbye()
            return
        
        elif 'view playlist' in utterance_lower:
            playlist_contents = self.current_playlist
            print("hello", playlist_contents.view_playlist())
            song_response = playlist_contents.view_playlist()
            
        elif 'add' in utterance_lower:
            match = re.search(r"add ['\"]?(.+?)['\"]?(?: to the playlist)?$", utterance_lower)
            if match:
                song_name = match.group(1)
                if self.current_playlist.add_song(song_name):
                    song_response = f"Added '{song_name}' to the playlist."
                else:
                    song_response = f"Unable to add '{song_name}' (Already in the playlist, or does not exist in database)."

        elif 'remove' in utterance_lower:
            match = re.search(r"remove ['\"]?(.+?)['\"]?(?: from the playlist)?$", utterance_lower)
            if match:
                song_name = match.group(1)
                if self.current_playlist.remove_song(song_name):
                    song_response = f"Removed '{song_name}' from the playlist."
                else:
                    song_response = f"'{song_name}' is not in the playlist."

        elif 'clear playlist' in utterance_lower:
            if self.current_playlist.clear_playlist():
                song_response = "Playlist has been cleared."
            else:
                song_response = "Playlist could not be cleared."

        elif 'when' in utterance_lower:
         match = re.search(r"when was album (.+?) released\??$", utterance_lower, re.IGNORECASE)
         if match:
             album_name = match.group(1).strip()
             print("album_name", album_name)
             album = self.get_album_by_name(album_name)
             song_response = f"Album {album[1]} was released in {album[3]} by {album[4]}"
             
        elif 'how' in utterance_lower:
         match = re.search(r"how many albums has artist (.+?) released\??$", utterance_lower, re.IGNORECASE)
         if match:
            artist_name = match.group(1).strip()
            albums = self.get_albums_by_artist(artist_name)
            print("PLAYLISTLENGTH", len(albums), albums)
            if len(albums) == 0:
                song_response = f"Artist {artist_name} has released no albums released according to our database."
            elif len(albums) == 1:
                song_response = f"Artist {artist_name} has released 1 album named {albums[0][0]}"
            else:
                song_response = f"Artist {artist_name} has released {len(albums)} albums named {', '.join(albums)}"
        
        elif 'which' in utterance_lower:
         match = re.search(r"which album features song (.+?)\??$", utterance_lower, re.IGNORECASE)
         if match:
            song_name = match.group(1).strip()
            album = self.get_albums_by_song(song_name)
            song_response = f"Song {song_name} is featured in album {album[0]}"

        elif utterance_lower in ['help', 'list']:
            song_response = self.HELP_MESSAGE
        
        response = AnnotatedUtterance(
            song_response,
            participant=DialogueParticipant.AGENT,
        )

        self._dialogue_connector.register_agent_utterance(response)