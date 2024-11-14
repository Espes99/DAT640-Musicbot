import re
import sqlite3
import os
import song 
import musicbrainzngs
import unicodedata
import re
from unidecode import unidecode
import song


DB_PATH = os.path.join('data', 'music.db')
musicbrainzngs.set_useragent("DAT640-MUSICBOT", "1.0", "s.melkevig@stud.uis.no")

def normalize_string(input_string):
    # Normalize the string to remove special characters
    return unicodedata.normalize('NFKD', input_string).encode('ASCII', 'ignore').decode('utf-8').lower()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS album (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            artist_id INTEGER NOT NULL,
            release_year INTEGER,
            genre TEXT,
            FOREIGN KEY(artist_id) REFERENCES artist(id),
            UNIQUE(name, artist_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS song (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            album_id INTEGER,
            artist TEXT NOT NULL,
            length TEXT NOT NULL,
            FOREIGN KEY(album_id) REFERENCES album(id),
            UNIQUE(name, album_id, artist)
        )
    ''')

def normalize_text(text):
    # Normalize text to remove accents and convert to lowercase
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    # Remove punctuation using regex
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower()

def drop_accents(text):
    if text:
        text = unidecode(text)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    return text

def get_song(song_name):
    conn = get_db_connection()
    conn.create_function("DROPACCENTS", 1, drop_accents)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM song
        WHERE DROPACCENTS(LOWER(name)) LIKE '%' || DROPACCENTS(LOWER(?)) || '%'
    ''', (song_name,))
    
    song_row = cursor.fetchall()
    print("Heisa", song_row)
    conn.close()
    
    if song_row:
        songMapped = []
        for songen in song_row:
            if not any(drop_accents(existing_song.name).lower() == drop_accents(songen[1]).lower() and existing_song.artist.lower() == songen[3].lower() for existing_song in songMapped):
                songMapped.append(song.Song(songen[0], songen[1], songen[2], songen[3], songen[4]))
                if len(songMapped) > 5:
                    break
        return songMapped
    return None

def get_song_or_add_song(song_name, artist_name, song_length):
    try:
        print("Fetching song", song_name, artist_name)
        song_fetched = get_song_by_name(song_name, artist_name)
        if song_fetched:
            return song_fetched
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO song (name, album_id, artist, length)
                VALUES (?,?,?,?)
            ''', (song_name, None, artist_name, song_length))
            conn.commit()
            song_to_return = get_song_by_name(song_name, artist_name)
            return song_to_return
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        try:
            conn.close()
        except:
            pass
    

def get_song_by_name(song_name, artist_name):
    conn = get_db_connection()
    conn.create_function("DROPACCENTS", 1, drop_accents)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM song
        WHERE DROPACCENTS(LOWER(name)) = DROPACCENTS(LOWER(?)) AND DROPACCENTS(LOWER(artist)) = DROPACCENTS(LOWER(?))
    ''', (song_name, artist_name))
    song_row = cursor.fetchone()
    print("songrow", song_row)
    conn.close()
    if song_row:
        songMapped = song.Song(song_row[0], song_row[1], song_row[2], song_row[3], song_row[4])
        return songMapped
    return None

def get_song_by_name_and_artist(song_name, artist_name):
    conn = get_db_connection()
    conn.create_function("DROPACCENTS", 1, drop_accents)
    cursor = conn.cursor()
    print("artistname", drop_accents(artist_name))
    print("songname", drop_accents(song_name))
    cursor.execute('''
        SELECT * FROM song
        WHERE DROPACCENTS(LOWER(name)) LIKE '%' || DROPACCENTS(LOWER(?)) || '%' AND DROPACCENTS(LOWER(artist)) = DROPACCENTS(LOWER(?))
    ''', (song_name, artist_name))
    song_row = cursor.fetchall()
    print("songrow", song_row)
    conn.close()
    if song_row:
        song_mapped = []
        for songen in song_row:
            # Check if songen[1] is not already in any song in song_mapped
            if not any(drop_accents(existing_song.name).lower() == drop_accents(songen[1]).lower() for existing_song in song_mapped):
                song_mapped.append(song.Song(songen[0], songen[1], songen[2], songen[3], songen[4]))
        return song_mapped
    return None


def get_artist_by_id(artist_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM artist WHERE id =?
    ''', (artist_id,))
    artist_row = cursor.fetchone()
    conn.close()
    print("Artist NAME FOUND BY ID ", artist_row[1])
    return artist_row[1] if artist_row else None

def get_album_by_name(album_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT album.*, artist.name AS artist_name
        FROM album
        JOIN artist ON album.artist_id = artist.id
        WHERE LOWER(album.name) = LOWER(?)
    ''', (album_name,))
    album = cursor.fetchone()
    return album if album else None

def get_album_by_id(album_id):
    print("Getting album by id", album_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM album WHERE id =?
    ''', (album_id,))
    album = cursor.fetchone()
    print("Album FOUND BY ID ", album)
    return album if album else None
 
def get_albums_by_artist(artist_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id FROM artist WHERE LOWER(name) = LOWER(?)
    ''', (artist_name,))
    artist = cursor.fetchone()
    if artist:
        artist_id = artist[0]
        cursor.execute('''
            SELECT name FROM album WHERE artist_id = ?
        ''', (artist_id,))
        albums = cursor.fetchall()
        return [album for album in albums]
    else:
        return []


def get_albums_by_song(song_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT album.name 
        FROM song
        JOIN album ON song.album_id = album.id
        WHERE LOWER(song.name) = LOWER(?);
    ''', (song_name,))
    album = cursor.fetchone()
    return album if album else None


def get_songs_from_album_name(album_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT song.name 
        FROM song
        JOIN album ON song.album_id = album.id
        WHERE LOWER(album.name) = LOWER(?);
    ''', (album_name,))
    songs = cursor.fetchall()
    return songs if len(songs) > 0 else None
    
def get_genre_by_album_name(album_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT genre 
        FROM album
        WHERE LOWER(album.name) = LOWER(?);
    ''', (album_name,))
    genre = cursor.fetchone()
    return genre if genre else None


def get_artist_by_song_name(song_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT artist 
        FROM song
        WHERE LOWER(song.name) = LOWER(?);
    ''', (song_name,))
    artist = cursor.fetchone()
    return artist if artist else None

def normalize_song_name(song_name):
    return re.sub(r"[^\w\s]", "", song_name.lower())

def get_songs_by_artist(artist_name):
    print("Getting songs by artist", artist_name)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT *
        FROM song
        JOIN album ON song.album_id = album.id
        JOIN artist ON album.artist_id = artist.id
        WHERE LOWER(artist.name) = LOWER(?)
    ''', (artist_name,))
    songs = cursor.fetchall()

    seen_song_names = set()
    songs_by_artist = []

    if len(songs) > 0:
        for song_row in songs:
            song_name = song_row[1]
            normalized_name = normalize_song_name(song_name)
            if normalized_name not in seen_song_names:
                seen_song_names.add(normalized_name)

                songMapped = song.Song(song_row[0], song_row[1], song_row[2], song_row[3], song_row[4])
                songs_by_artist.append(songMapped)
    print("touple error not here")
    return songs_by_artist

def get_songs_by_genre(genre):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT *
        FROM song
        JOIN album ON song.album_id = album.id
        WHERE LOWER(album.genre) = LOWER(?)
    ''', (genre,))
    songs = cursor.fetchall()

    seen_song_names = set()
    songs_by_genre = []

    if len(songs) > 0:
        for song_row in songs:
            song_name = song_row[1]
            normalized_name = normalize_song_name(song_name)
            if normalized_name not in seen_song_names:
                seen_song_names.add(normalized_name)

                songMapped = song.Song(song_row[0], song_row[1], song_row[2], song_row[3], song_row[4])
                songs_by_genre.append(songMapped)
    return songs_by_genre

def get_songs_by_year(year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT *
        FROM song
        JOIN album ON song.album_id = album.id
        WHERE album.release_year = ?
    ''', (year,))
    songs = cursor.fetchall()

    seen_song_names = set()
    songs_by_year = []
    if len(songs) > 0:
        for song_row in songs:
            song_name = song_row[1]
            normalized_name = normalize_song_name(song_name)
            if normalized_name not in seen_song_names:
                seen_song_names.add(normalized_name)

                songMapped = song.Song(song_row[0], song_row[1], song_row[2], song_row[3], song_row[4])
                songs_by_year.append(songMapped)
    return songs_by_year

def populate_playlist():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM song
        ORDER BY RANDOM()
        LIMIT 10
    ''')

    random_songs = cursor.fetchall()

    listen = []
    if len(random_songs) > 0:
        for song_row in random_songs:
            songMapped = song.Song(song_row[0], song_row[1], song_row[2], song_row[3], song_row[4])
            listen.append(songMapped)
        return listen
    return None


def add_to_database(results, conn):
    cursor = conn.cursor()

    artists = {(result['artist'],) for result in results}

    cursor.executemany('INSERT OR IGNORE INTO artist (name) VALUES (?)', artists)
    
    artist_ids =  { artist: cursor.execute('SELECT id FROM artist WHERE name = ?', (artist,)).fetchone()[0] for artist, in artists}

    albums = {(result['album_name'], artist_ids[result['artist']], result['album_release_year'], result['album_genre'],) for result in results if result['artist'] in artist_ids}

    cursor.executemany('INSERT OR IGNORE INTO album (name, artist_id, release_year, genre ) VALUES (?, ?, ?, ?)', albums)

    album_ids = { (album_name, artist_id): cursor.execute('SELECT id FROM album WHERE name = ? AND artist_id = ?', (album_name, artist_id)).fetchone()[0] for album_name, artist_id, _, _ in albums}

    songs = {(result['song_title'], album_ids.get((result['album_name'], artist_ids[result['artist']])), result['artist'], result['song_length'],) for result in results if (result['album_name'], artist_ids[result['artist']]) in album_ids}

    cursor.executemany('INSERT OR IGNORE INTO song (name, album_id, artist, length ) VALUES (?, ?, ?, ?)', songs)

    conn.commit()

    amount_of_songs = cursor.execute('SELECT COUNT(*) FROM song').fetchone()[0]

    return amount_of_songs

def format_song_length(length):
    if length is None:
        return "Unknown Song Length"
    
    seconds = int(length) // 1000
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    return f"{minutes}:{remaining_seconds:02d}"

def populate_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    database_amount = 0
    offset = 0
    while database_amount <= 1000000:
        cursor.execute("SELECT COUNT(*) FROM song")
        songs_in_database = cursor.fetchone()[0]
        database_amount = songs_in_database
        result = musicbrainzngs.search_recordings('i', limit=100, offset=offset)
        formatted_results = [
            {
                'song_title': rec['title'] if 'title' in rec and rec['title'] else 'Unknown Song title',
                'artist': rec['artist-credit'][0]['artist']['name'] if 'artist-credit' in rec else 'Unknown Artist',
                'song_length': format_song_length(rec['length']) if 'length' in rec and rec['length'] else format_song_length(None),
                'album_name': rec['release-list'][0]['title'] if 'release-list' in rec and rec['release-list'] else 'Unknown Album',
                'album_release_year': rec['release-list'][0]['date'].split('-')[0] if 'release-list' in rec and 'date' in rec['release-list'][0] and rec['release-list'] else 'Unknown Release Date',
                'album_genre': rec['tag-list'][0]['name'] if 'tag-list' in rec else 'Unknown Genre'
            }
            for rec in result['recording-list']
        ]
        amount = add_to_database(formatted_results, conn)
        count = amount - songs_in_database
        offset += 100
        print(f'Currently {count} songs added to database. Now a total of {amount}/1000000 songs')

if __name__ == '__main__':
    initialize_database()
    populate_database()
