import json
import os
import re
import playlist


def load_playlists_from_json() -> list:
    """Load playlists from JSON files"""
    print("Loading playlists from JSON files...")
    playlists = []
    playlist_folder_path = 'data/playlists'
    for filename in os.listdir(playlist_folder_path):
        if filename.endswith('.json'):
            with open(os.path.join(playlist_folder_path, filename), 'r') as file:
                data = json.load(file)
                playlists.extend(data['playlists'])
    return playlists


def extract_keywords(user_input: str) -> list:
    """Extract relevant keywords from user input by splitting based on stop words."""
    stop_words = [
        'a', 'an', 'the', 'and', 'but', 'if', 'or', 'on', 'at', 'for', 'to', 'by', 'with', 'in', 'of', 'as', 'this', 
        'that', 'it', 'is', 'was', 'were', 'are', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 
        'did', 'doing', 'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'any', 'are', 'aren’t',
        'aren’t', 'being', 'below', 'between', 'both', 'but', 'by', 'can’t', 'cannot', 'could', 'couldn’t', 'didn’t', 
        'don’t', 'down', 'during', 'few', 'for', 'from', 'further', 'hadn’t', 'hasn’t', 'haven’t', 'having', 'having'
    ]
    
    # Clean and lower the input string
    user_input = re.sub(r'[^\w\s]', ' ', user_input.lower())
    words = user_input.split()
    # Remove stop words from the input
    filtered_words = [word for word in words if word not in stop_words]
    print(f"Filtered keywords: {filtered_words}")
    return filtered_words

def score_spotify_playlists(user_input: str, playlists: list) -> list:
    """Score playlists based on keyword matches"""
    keywords = extract_keywords(user_input)
    
    scored_playlists = []
    for playlist in playlists:
        name = playlist['name'].lower()
        score = sum([keyword in name for keyword in keywords])  
        
        scored_playlists.append((playlist, score))
    
    scored_playlists.sort(key=lambda x: x[1], reverse=True)

    print(f"Top 5 scored playlists:")
    for playlist, score in scored_playlists[:5]:
        print(f"Playlist: {playlist['name']} - Score: {score}")
    
    return scored_playlists


def create_playlist_based_on_input(user_input: str, playlists: list, connection, trackLimit: int) -> playlist.Playlist:
    """Create a playlist based on the user's input"""
    scored_playlists = score_spotify_playlists(user_input, playlists)
    print(f"Found {len(scored_playlists)} playlists based on the user input")
    created_playlist = playlist.Playlist(name=f"Playlist based on: {user_input}", db_connection=connection)
    created_playlist.clear_playlist()
    track_limit = trackLimit if trackLimit else 10
    
    for playlist_scored, score in scored_playlists:
        if score > 0: 
            for track in playlist_scored['tracks']:
                print()
                song_name = track['track_name']
                artist_name = track['artist_name']
                song_duration = track['duration_ms'] / 60000 
                minutes = int(song_duration // 1)  
                seconds = int((song_duration % 1) * 60)  
                formatted_duration = f"{minutes}:{seconds:02d}"
                success, song = created_playlist.add_song_from_creation(song_name, artist_name, formatted_duration)
                if success:
                    print(f"Added {song.name} by {song.artist} to the playlist")
                else:
                    print(f"I couldn't add {song_name} by {artist_name} to the playlist")
                print(f"Total songs in the playlist: {len(created_playlist.songs)}")
                if len(created_playlist.songs) >= track_limit:
                    break

        if len(created_playlist.songs) >= track_limit:
            break
    
    return created_playlist