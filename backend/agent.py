from dialoguekit.participant.agent import Agent
from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.participant import DialogueParticipant
import sqlite3
from uuid import uuid4
import re
from datetime import datetime
import database
import playlist

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
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT name, artist, length FROM song LIMIT ?', (limit,))
        rows = cursor.fetchall()
        songs = []
        for row in rows:
            name, artist, length = row
            songs.append((name, artist, length))
        return songs
    
    def get_song(self):
        with sqlite3.connect('music.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM song LIMIT 1') 
            song = cursor.fetchone()
        return song
    
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

        elif utterance_lower in ['help', 'list']:
            song_response = self.HELP_MESSAGE


        response = AnnotatedUtterance(
            song_response,
            participant=DialogueParticipant.AGENT,
        )

        self._dialogue_connector.register_agent_utterance(response)