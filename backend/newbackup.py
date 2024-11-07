from flask import Flask
from flask_socketio import SocketIO, emit
from ollama import *
from langchain_ollama import ChatOllama
import playlist
import database

# Database connection and Flask setup
db_connection = database.get_db_connection()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Define tools
playlist_instance = playlist.Playlist(name='My Playlist', db_connection=db_connection)
tools = [playlist_instance.view_playlist]
print("Tool details:", tools)
prompt = """
You are a music chatbot. You ONLY answer questions about songs, albums, or artists in the playlist or database.
You have one tool called `view_playlist`. ALWAYS use this tool when the user asks to view or see the playlist.

### Example Usage
- User: "Show me the playlist."
  - You must use the `view_playlist` tool.
- User: "Can I see the playlist?"
  - You must use the `view_playlist` tool.

Do NOT generate any random text. If the input is not about the playlist, say: "Ask me any questions about a playlist."
"""

# Mistral model setup
mistral_model = ChatOllama(
    model='mistral',
    num_ctx=4,
    temperature=0.2,
    system=prompt
).bind_tools(tools)

@app.route('/')
def index():
    return "Chatbot backend is running."

@socketio.on('connect')
def handle_connect():
    emit('message', {'message': {'text': "Welcome to the chat! What can I do for you?"}})

@socketio.on('message')
def handle_message(msg):
    message_field = msg.get("message", "")
    msg_lower = message_field.lower()

    # Debug print to check incoming message
    print("Received message:", msg_lower)

    try:
        # Invoke the Mistral model
        response = mistral_model.invoke(message_field)
        print("Model response:", response)
        
        # Check if the response includes an attempt to use the tool
        if "view_playlist" in response.content:
            print("The model indicated tool usage.")
        else:
            print("The model did not indicate tool usage.")
        
        # Emit the response content back to the user
        emit('message', {'message': {'text': response.content}})
    except Exception as e:
        print("Error invoking model or tool:", e)
        emit('message', {'message': {'text': "Something went wrong."}})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True)