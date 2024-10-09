from dialoguekit.participant.agent import Agent
from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.participant import DialogueParticipant
import sqlite3
from uuid import uuid4
import re
from datetime import datetime

import playlist

class MusicBotAgent(Agent):

    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.songs = self. get_all_songs()
        self.current_playlist = playlist.Playlist(name='My Playlist', songs=[f"({song[0]} - {song[1]} - {song[2]})" for song in self.songs]) 
    
    def initialize_database(self):
        """Initializes connection to SQLite database and populates data if empty."""
        conn = sqlite3.connect('music.db')
        return conn
    
    def get_song(self):
        with sqlite3.connect('music.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM song LIMIT 1') 
            song = cursor.fetchone()
        return song
    
    def get_all_songs(self, limit=2):
        with sqlite3.connect('music.db') as conn:
            cursor = conn.cursor()
            # Fetch all relevant song details
            cursor.execute('SELECT name, artist, length FROM song LIMIT ?', (limit,))
            rows = cursor.fetchall()

            # Create Song objects from the fetched data
            songs = []
            for row in rows:
                name, artist, length = row
                length = datetime.strptime(length, '%H:%M:%S')
                songs.append((name, artist, length))
                
        return songs

    
    def welcome(self) -> None:
        """Sends the agent's welcome message."""
        utterance = AnnotatedUtterance(
            "Welcome to the chat! What can I do for you?",
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
        if utterance_lower == "exit":
            self.goodbye()
            return
        elif 'view playlist' in utterance_lower:
            playlist_contents = self.current_playlist
            print("hello", playlist_contents.view_playlist())
            song_response = playlist_contents.view_playlist()
            
        #TODO ESPEN
        """ if 'add' in msg_lower:
        match = re.search(r"add ['\"]?(.+?)['\"]?(?: to the playlist)?$", msg_lower)
        if match:
            song_name = match.group(1)
            if current_playlist.add_song(song_name):
                emit('message', {
                    'message':{
                        'text': f"Added '{song_name}' to the playlist."}
                    })
            else:
                emit('message', {
                    'message':{
                        'text': f"'{song_name}' already in the playlist."}
                    })
        else:
            emit('message', {
                'message':{ 
                'text': "Please specify the song to add."}
                }) """
        """ elif 'remove' in msg_lower:
        match = re.search(r"remove ['\"]?(.+?)['\"]?(?: from the playlist)?$", msg_lower)
        if match:
            song_name = match.group(1)
            if current_playlist.remove_song(song_name):
                emit('message', {
                    'message':{
                        'text': f"Removed '{song_name}' from the playlist."}
                    })
            else:
                emit('message', {
                    'message': {
                        'text': f"'{song_name}' is not in the playlist."}
                    })
        else:
            emit('message', {
                'message': {
                    'text': "Please specify the song to remove."}
                }) """

        """ elif 'clear playlist' in msg_lower:
        current_playlist.clear_playlist()
        emit('message', {
                    'message': {
                        'text': "Playlist has been cleared."
                    }
                }) """
        #END TODO ESPEN


        # Fetch an existing song from the database
        """ existing_song = self.get_song()
        
        # If a song exists, reply with the song information; otherwise, give a default response
        if existing_song:
            song_response = f"(Parroting) {existing_song[0]}"
        else:
            song_response = "Sorry, I couldn't find any songs." """
        
        response = AnnotatedUtterance(
            song_response,
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(response)