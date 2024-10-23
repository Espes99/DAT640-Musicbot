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
