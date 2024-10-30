from dialoguekit.participant.agent import Agent
from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.participant import DialogueParticipant
import re
import database
import playlist
import sqlite3
import os
from REL.mention_detection import MentionDetection
from REL.utils import process_results
from REL.entity_disambiguation import EntityDisambiguation

wiki_version = "wiki_2014"  
base_url = "data/rel_data"  


mention_detection = MentionDetection(base_url, wiki_version)
config = {"mode": "eval", "model_path": f"ed-{wiki_version}"}
entity_disambiguation = EntityDisambiguation(base_url, wiki_version, config)


def disambiguate_song_with_rel(song_name, artist_name=None):
    text = f"{song_name} by {artist_name}" if artist_name else song_name
    
    # Prepare input for REL
    input_text = {"song_query": (text, [])}
    mentions, _ = mention_detection.find_mentions(input_text, mention_detection)

    predictions, _ = entity_disambiguation.predict(mentions)
    result = process_results(mentions, predictions, input_text)

    disambiguated_songs = []
    for mention, entity in result["song_query"]:
        disambiguated_songs.append({
            "song": mention[2],
            "linked_entity": entity[0], 
            "confidence": entity[1]  
        })
    

    if not disambiguated_songs:
        return database.get_song_by_name(song_name, artist_name)
    
    return disambiguated_songs


db_connection = database.get_db_connection()

class MusicBotAgent(Agent):
    def __init__(self, agent_id: str = "music-bot"):
        super().__init__(agent_id)
        self.db_connection = database.get_db_connection()
        self.current_playlist = playlist.Playlist(name='My Playlist', db_connection=db_connection)
        self.available_commands = [
            ("add [song name] by [artist name]", "Adds a song to the playlist."),
            ("remove [song name] by [artist name]", "Removes a song from the playlist."),
            ("view playlist", "Displays the current playlist."),
            ("clear playlist", "Clears the entire playlist."),
            ("when was album [album name] released?", "Returns the release date of the album."),
            ("how many albums has artist [artist name] released?", "Returns the number of albums released by the artist."),
            ("which album features song [song name]?", "Returns the album that features the song."),
            ("who is the artist of song [song name]?", "Returns the artist who performed the specified song."),
            ("list all songs in album [album name].", "Provides a list of all songs included in the specified album."),
            ("what is the genre of artist [artist name]?", "Returns the primary genre associated with the specified artist."),
            ("exit", "Exits the chat.")
        ]
        
        self.HELP_MESSAGE = "Available commands: " + " ".join(
            [f"- '{cmd}': {desc}" for cmd, desc in self.available_commands]
        )
        
        self.used_commands = []
        self.current_song = None

    def welcome(self) -> None:
        utterance = AnnotatedUtterance(
            "Welcome to the chat! What can I do for you? Type 'help' for more information.",
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def goodbye(self) -> None:
        utterance = AnnotatedUtterance(
            "It was nice talking to you. Bye",
            intent=self.stop_intent,
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def get_unused_commands(self):
        unused = [cmd for cmd, _ in self.available_commands if cmd not in self.used_commands]
        return unused
    
    def get_commands_with_song_name(self, song_name):
        commands_with_song_name = [
            cmd[0] for cmd in self.available_commands if "[song name]" in cmd[0]
        ]
        commands_with_song_name = [
            cmd.replace("[song name]", song_name) for cmd in commands_with_song_name
        ]
        return commands_with_song_name


    def format_commands(self, commands):
        if not commands:
            return "You have utilized all available commands!"
        formatted = " ".join([f"- '{cmd}'" for cmd in commands])
        return f"Commands you can try out: {formatted}"

    def receive_utterance(self, utterance: Utterance) -> None:
        utterance_lower = utterance.text.lower()
        song_response = "Sorry, I couldn't do anything about that."
        
        if utterance_lower == "exit":
            self.goodbye()
            return
        
        elif 'view playlist' in utterance_lower:
            playlist_contents = self.current_playlist
            song_response = playlist_contents.view_playlist()
            self.used_commands.append('view playlist')
            
        elif 'add' in utterance_lower:
            match = re.search(r"add ['\"]?(?P<song>.+?)['\"]?(?: by ['\"]?(?P<artist>.+?)['\"]?)?", utterance_lower)
            if match:
                song_name = match.group('song').strip()
                artist_name = match.group('artist').strip() if match.group('artist') else None
                
                # Call REL disambiguation
                disambiguated_songs = disambiguate_song_with_rel(song_name, artist_name)
                
                if len(disambiguated_songs) > 1:
                    # Present options to user if multiple versions are found
                    options = "\n".join([f"{idx+1}. {song['song']} ({song['linked_entity']}, Confidence: {song['confidence']})"
                                        for idx, song in enumerate(disambiguated_songs)])
                    song_response = f"Multiple matches found for '{song_name}'. Please choose:\n{options}"
                elif disambiguated_songs:
                    # If one match is found, add directly
                    song = disambiguated_songs[0]
                    hit, added_song = self.current_playlist.add_song(song["song"], artist_name)
                    song_response = f"Added '{added_song.name}' by {added_song.artist} to the playlist."
                else:
                    song_response = f"No matches found for '{song_name}'."

            self.used_commands.append('add [song name] by [artist name]')
            
        elif re.match(r'^\d+$', utterance_lower) and self.disambiguation_options:
            choice_index = int(utterance_lower) - 1
            if 0 <= choice_index < len(self.disambiguation_options):
                selected_song = self.disambiguation_options[choice_index]
                hit, added_song = self.current_playlist.add_song(selected_song["song"], selected_song["artist"])
                song_response = f"Added '{added_song.name}' by {added_song.artist} to the playlist."
            else:
                song_response = "Invalid choice. Please try again."
            self.disambiguation_options = None  

        elif 'remove' in utterance_lower:
            match = re.search(
                r"""remove\s+['"]?(?P<song>.+?)['"]?\s+
                    (?:by\s+['"]?(?P<artist>.+?)['"]?)?
                    (?:\s+to\s+the\s+playlist)?$""",
                utterance_lower,
                re.IGNORECASE | re.VERBOSE
            )
            if match:
                song_name = match.group('song').strip()
                artist_name = match.group('artist').strip() if match.group('artist') else None
                hit, song = self.current_playlist.remove_song(song_name, artist_name)
                if hit:
                    song_response = f"Removed '{song.name}' by {song.artist} from the playlist."
                elif not hit and song != None:
                    song_response = f"'{song.name}' by {song.artist} is not in the playlist."
                else:
                    song_response = f"Unable to remove '{song_name}' by {artist_name} from the playlist."
            self.used_commands.append('remove [song name] by [artist name]')

        elif 'clear playlist' in utterance_lower:
            if self.current_playlist.clear_playlist():
                song_response = "Playlist has been cleared."
            else:
                song_response = "Playlist could not be cleared."
            self.used_commands.append('clear playlist')

        elif 'when' in utterance_lower:
            match = re.search(r"when was album (.+?) released\??$", utterance_lower, re.IGNORECASE)
            if match:
                album_name = match.group(1).strip()
                album = database.get_album_by_name(album_name)
                if album:
                    song_response = f"Album '{album[1]}' was released in {album[3]} by {album[5]}"
                else:
                    song_response = f"Album '{album_name}' not found."
                self.used_commands.append('when was album [album name] released?')

        elif 'how' in utterance_lower:
            match = re.search(r"how many albums has artist (.+?) released\??$", utterance_lower, re.IGNORECASE)
            if match:
                artist_name = match.group(1).strip()
                albums = database.get_albums_by_artist(artist_name)
                if len(albums) == 1:
                    song_response = f"Artist '{artist_name}' has released 1 album named '{albums[0][0]}'"
                elif len(albums) > 1:
                    album_names = "', '".join([album[0] for album in albums])
                    song_response = f"Artist '{artist_name}' has released {len(albums)} albums named '{album_names}'"
                else:
                    song_response = f"Artist '{artist_name}' has not released any albums according to our database."
                self.used_commands.append('how many albums has artist [artist name] released?')

        elif 'which' in utterance_lower:
            match = re.search(r"which album features song (.+?)\??$", utterance_lower, re.IGNORECASE)
            if match:
                song_name = match.group(1).strip()
                album = database.get_albums_by_song(song_name)
                self.current_song = song_name
                if album:
                    song_response = f"Song '{song_name}' is featured in album '{album[0]}'"
                else:
                    song_response = f"Song '{song_name}' not found in any album."
                self.used_commands.append('which album features song [song name]?')

        elif 'who is the artist of song' in utterance_lower:
            match = re.search(r"who is the artist of song ['\"]?(.+?)['\"]?\??$", utterance_lower, re.IGNORECASE)
            if match:
                song_name = match.group(1).strip()
                artist = database.get_artist_by_song_name(song_name)
                if artist:
                    song_response = f"The artist of '{song_name}' is {artist}."
                else:
                    song_response = f"Artist for '{song_name}' not found."
                self.used_commands.append('who is the artist of song [song name]?')

        elif 'list all songs in album' in utterance_lower:
            match = re.search(r"list all songs in album ['\"]?(.+?)['\"]?\.*$", utterance_lower, re.IGNORECASE)
            if match:
                album_name = match.group(1).strip()
                songs = database.get_songs_from_album_name(album_name)
                if songs:
                    song_list = "', '".join([song[0] for song in songs])
                    song_response = f"Songs in album '{album_name}': '{song_list}'."
                else:
                    song_response = f"Album '{album_name}' not found or has no songs."
                self.used_commands.append('list all songs in album [album name].')

        elif 'what is the genre of album' in utterance_lower:
            match = re.search(r"what is the genre of album ['\"]?(.+?)['\"]?\??$", utterance_lower, re.IGNORECASE)
            if match:
                album_name = match.group(1).strip()
                genre = database.get_genre_by_album_name(album_name)
                if genre:
                    song_response = f"The genre of album '{album_name}' is {genre}."
                else:
                    song_response = f"Genre for album '{album_name}' not found."
                self.used_commands.append('what is the genre of album [album name]?')

        elif utterance_lower in ['help', 'list']:
            song_response = self.HELP_MESSAGE
            self.used_commands.append('help')

        else:
            song_response = "I'm sorry, I didn't understand that command. Type 'help' to see the list of available commands."

        response = AnnotatedUtterance(
            song_response,
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(response)

        if(self.current_song):
            song_response = f"More commands with '{self.current_song}: ' " + self.format_commands(self.get_commands_with_song_name(self.current_song))
            response = AnnotatedUtterance(
                song_response,
                participant=DialogueParticipant.AGENT,
            )
            self._dialogue_connector.register_agent_utterance(response)
            self.current_song = None
        else:
            if utterance_lower in ['help', 'list']:
                return
            else:
                    unused_commands = self.get_unused_commands()
                    unused_formatted = self.format_commands(unused_commands)
                    
                    if unused_commands:
                        second_response = AnnotatedUtterance(
                            unused_formatted,
                            participant=DialogueParticipant.AGENT,
                        )
                        self._dialogue_connector.register_agent_utterance(second_response)