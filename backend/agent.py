from dialoguekit.participant.agent import Agent
from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.participant import DialogueParticipant
from modelTools import *
import database
import playlist
from ollama import *
from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode 
from langchain_core.messages import HumanMessage

db_connection = database.get_db_connection()

system_prompt = """
You are a Music Recommendation System chatbot, here to assist users in managing and enhancing their playlist experience. You are a helpful assistant that provides users with tools to manage their playlists, discover new music, and gain insights into their favorite songs and artists. 

Important rules to follow:
- If artist is not provided, execute add_song_by_artist_to_playlist tool with artist name being None.
- You will never respond with "Who is the artist?". If artist is not provided, execute add_song_by_artist_to_playlist tool.
- You must only interact with the playlist specified in the code. Never generate or refer to random artists or songs that are not in the user's playlist.
- You should never generate or infer artist names or song names. If a song name is provided without an artist name, the artist name is nullable and should be treated as None.
- You should not create or assume any details not explicitly provided by the user. Always ask the user for clarification if there is ambiguity.
- Never display code snippets, commands, or any programming-related details. Only use the tools specified in the prompt to interact with the user.
- If the user input does not trigger any of the tools or is unclear, respond with "I did not quite get that."
- Whenever the user refers to a playlist, always use the playlist_instance with name "My playlist". You will NOT ask the user to specify which playlist.
- The tools available to you are:
  - `view_playlist`: View the contents of the playlist.
  - `add_song_by_artist_to_playlist`: Add a song to the playlist by specifying the song name and artist, but artist CAN be None. 
                                      If user writes "add baby" the system will recoginize that the artist name is not provided, and thereby None and execute add_song_by_artist_to_playlist with artistname being None.
                                      For instance if user writes "add baby by justin bieber" the system will recoginize that the artist name is "justin bieber" and that the song name is baby.
  - `remove_from_playlist`: Remove a song from the playlist by specifying the artist name and song name, or by position.
  - `clear_the_playlist`: Clear the entire playlist.
  - `when_album_released`: Get the release date of an album by specifying the album name.
  - `how_albums_released_artist`: Get the release dates of all albums by an artist by specifying the artist name.
  - `which_album_has_song`: Get the album that contains a specific song by specifying the song name.
  - `which_artist_released_song`: Get the artist that released a specific song by specifying the song name.
  - `list_songs_album`: Get a list of songs in an album by specifying the album name.
  - `get_album_genre`: Get the genre of an album by specifying the album name.
  - `remove_first_n_songs`: Remove the first n songs from the playlist.
  - `remove_last_song`: Remove the last song from the playlist.
  - `get_song_by_position`: Get the details of a song by specifying the position in the playlist.
  - `recommend_music`: Get music recommendations based on user preferences and listening habits.

Only use these tools and never use any other source of knowledge. Be sure to follow these rules strictly. 

If the user provides input that doesn’t clearly correspond to one of the available tools or if its too vague, respond with "I did not quite get that."
"""
playlist_instance = playlist.Playlist(name='My Playlist', db_connection=db_connection)

tools = [view_playlist,
        add_song_by_artist_to_playlist, 
        remove_from_playlist, 
        clear_the_playlist, 
        when_album_released, 
        how_albums_released_artist, 
        which_album_has_song, 
        which_artist_released_song, 
        list_songs_album,
        get_album_genre,
        remove_first_n_songs,
        remove_last_song,
        get_song_by_position,
        get_song_by_position,
        recommend_music]

class MusicBotAgent(Agent):
    def __init__(self, agent_id: str = "music-bot"):
        super().__init__(agent_id)
        
        self.mistral_model = ChatOllama(
            model='qwen2.5-coder:14b',
            num_ctx=4000,
            temperature=0.2,
            system=system_prompt
        ).bind_tools(tools)

        self.db_connection = database.get_db_connection()

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

    def receive_utterance(self, utterance: Utterance) -> None:
        utterance_lower = utterance.text.lower()
        count = 0
        # Loop until tool_calls is not null
        while True:
            print(count)
            response = self.mistral_model.invoke(utterance_lower)
            print("MODEL: ", response)
            song_response = response.content
            
            # If the utterance is "exit", end the conversation
            if utterance_lower == "exit":
                self.goodbye()
                return

            tool_calls = response.response_metadata.get("message", {}).get("tool_calls", [])
            print("TOOL CALLS: ", tool_calls)   
            # If tool_calls is not empty, break the loop
            if tool_calls:
                for tool_call in tool_calls:
                    tool_name = tool_call['function'].get("name")
                    tool_input = tool_call['function']['arguments']
                    print(tool_name)
                    print(tool_input)
                    
                    for tool in tools:
                        if tool.name == tool_name:
                            result = tool.invoke(tool_input)
                            song_response = result
                            break
                break  # Exit the loop when tool_calls is not empty

        # Return the annotated response
        response = AnnotatedUtterance(
            song_response,
            participant=DialogueParticipant.AGENT,
        )
        count += 1
        print()
        self._dialogue_connector.register_agent_utterance(response)