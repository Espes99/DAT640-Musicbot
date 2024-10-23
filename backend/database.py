import sqlite3
import os
import song 

DB_PATH = os.path.join('data', 'music.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS album (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            artist_id INTEGER NOT NULL,
            release_year INTEGER,
            FOREIGN KEY(artist_id) REFERENCES artist(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS song (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            album_id INTEGER,
            artist TEXT NOT NULL,
            length TEXT NOT NULL,
            FOREIGN KEY(album_id) REFERENCES album(id)
        )
    ''')


def get_song_by_name(song_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM song
        WHERE LOWER(name) = LOWER(?)
    ''', (song_name,))

    song_row = cursor.fetchone()
    conn.close()
    if song_row:
        songMapped = song.Song(song_row[0], song_row[1], song_row[2], song_row[3], song_row[4])
        return songMapped
    return None

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
