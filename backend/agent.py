from dialoguekit.participant.agent import Agent
from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.participant import DialogueParticipant
import database
import playlist
from ollama import *
from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode 

db_connection = database.get_db_connection()

class MusicBotAgent(Agent):
    def __init__(self, agent_id: str = "music-bot"):
        super().__init__(agent_id)
        self.db_connection = database.get_db_connection()
        playlist_instance = playlist.Playlist(name='My Playlist', db_connection=db_connection)
        self.tools = [playlist_instance.view_playlist]
        self.prompt = f""" You are a music chatbot that will only answer questions about songs, albums or artists that are in the playlist or about songs that are in the database """
        self.mistral_model = ChatOllama(model='mistral', num_ctx=4, temperature=0.2, system = self.prompt).bind_tools(self.tools)

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
        if utterance_lower == "exit":
            self.goodbye()
            return
        else:
            song_response = response.content
        response = AnnotatedUtterance(
            song_response,
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(response)