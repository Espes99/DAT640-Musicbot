from dialoguekit.platforms import FlaskSocketPlatform
from agent import MusicBotAgent
import database

if __name__ == '__main__':
    # Initialize the database
    database.initialize_database()
    
    # Start the platform with the agent class
    platform = FlaskSocketPlatform(MusicBotAgent)
    platform.start()
