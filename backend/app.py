from dialoguekit.platforms import FlaskSocketPlatform
from agent import MusicBotAgent
import database

if __name__ == '__main__':
    database.initialize_database()
    
    platform = FlaskSocketPlatform(MusicBotAgent)
    platform.start()