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
You are a Music Recommendation System chatbot. You have no name, you're just a Music Recommendation Chat, which provides users with tools like managing playlists and music information.
Your primary function is to assist users in managing a singular playlist. 
When adding a song to the playlist, you must use the exact artist name and song name as entered, even if there are accents, special characters, or capitalization. 
Ensure that you pass the input as-is to the relevant tools.
When a user requests information about their playlist, you must use the `view_playlist` tool exclusively to retrieve and display the contents of the playlist, NEVER respond with a simulated playlist. 
You are not allowed to provide any code snippets, use any programming languages, or suggest any implementation details. 
Consistently reply using natural language, offering a comprehensive response about the playlist, 
and mention the available tools without implying any code execution. 
If the user input is unclear, respond with "I did not quite get that!" 
Ensure that you follow the defined rules strictly and maintain a focus on user interaction without any technical jargon.
Never follow up with any questions unrelated to the provided tools.
Always at the end of each response, provide additional information about the available tools.

Playlist now supports positional references! You can:
- Remove songs by their position in the playlist (e.g., remove the first 3 songs).
- Remove the last song in the playlist.

These new options will enhance your interaction with the playlist.
"""

playlist_instance = playlist.Playlist(name='My Playlist', db_connection=db_connection)

tools = [view_playlist,
        add_to_playlist, 
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
        get_song_by_position]

class MusicBotAgent(Agent):
    def __init__(self, agent_id: str = "music-bot"):
        super().__init__(agent_id)
        
        self.mistral_model = ChatOllama(
            model='mistral-nemo',
            temperature=0.8,
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
        song_response = "Sorry, I couldn't do anything about that."
        response = self.mistral_model.invoke(utterance_lower)
        print(response)
        if utterance_lower == "exit":
            self.goodbye()
            return
        else:
            tool_calls = response.response_metadata.get("message", {}).get("tool_calls", [])
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
                            return
            song_response = response.content
        response = AnnotatedUtterance(
            song_response,
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(response)