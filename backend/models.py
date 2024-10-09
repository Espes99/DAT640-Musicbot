import sqlite3
from uuid import uuid4
from datetime import datetime

# Create a connection to an SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('music.db')
cursor = conn.cursor()

# Create tables for Artist, Album, and Song
cursor.execute('''
CREATE TABLE IF NOT EXISTS artist (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS album (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    artist_id TEXT NOT NULL,
    release_year TEXT NOT NULL,
    FOREIGN KEY (artist_id) REFERENCES artist(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS song (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    album_id TEXT NOT NULL,
    artist TEXT NOT NULL,
    length TEXT NOT NULL,
    FOREIGN KEY (album_id) REFERENCES album(id)
)
''')

conn.commit()  # Commit changes to the database

def insert_artist(name):
    artist_id = str(uuid4())
    cursor.execute('INSERT INTO artist (id, name) VALUES (?, ?)', (artist_id, name))
    conn.commit()
    return artist_id

# Function to insert album
def insert_album(name, artist_id, release_year):
    album_id = str(uuid4())
    cursor.execute('INSERT INTO album (id, name, artist_id, release_year) VALUES (?, ?, ?, ?)', 
                   (album_id, name, artist_id, release_year))
    conn.commit()
    return album_id

# Function to insert song
def insert_song(name, album_id, artist, length):
    song_id = str(uuid4())
    cursor.execute('INSERT INTO song (id, name, album_id, artist, length) VALUES (?, ?, ?, ?, ?)',
                   (song_id, name, album_id, artist, length))
    conn.commit()
    return song_id

# Insert real artists, albums, and songs
def populate_data():
    # Artist: The Beatles
    beatles_id = insert_artist('The Beatles')
    abbey_road_id = insert_album('Abbey Road', beatles_id, '1969')
    insert_song('Come Together', abbey_road_id, 'The Beatles', '00:04:20')
    insert_song('Something', abbey_road_id, 'The Beatles', '00:03:03')
    
    sgt_pepper_id = insert_album('Sgt. Pepper\'s Lonely Hearts Club Band', beatles_id, '1967')
    insert_song('Lucy in the Sky with Diamonds', sgt_pepper_id, 'The Beatles', '00:03:28')
    insert_song('A Day in the Life', sgt_pepper_id, 'The Beatles', '00:05:39')
    
    # Artist: Michael Jackson
    mj_id = insert_artist('Michael Jackson')
    thriller_id = insert_album('Thriller', mj_id, '1982')
    insert_song('Thriller', thriller_id, 'Michael Jackson', '00:05:57')
    insert_song('Beat It', thriller_id, 'Michael Jackson', '00:04:18')
    
    bad_id = insert_album('Bad', mj_id, '1987')
    insert_song('Bad', bad_id, 'Michael Jackson', '00:04:07')
    insert_song('Man in the Mirror', bad_id, 'Michael Jackson', '00:05:19')
    
    # Artist: Queen
    queen_id = insert_artist('Queen')
    night_at_opera_id = insert_album('A Night at the Opera', queen_id, '1975')
    insert_song('Bohemian Rhapsody', night_at_opera_id, 'Queen', '00:05:55')
    insert_song('Love of My Life', night_at_opera_id, 'Queen', '00:03:38')

    # Artist: Adele
    adele_id = insert_artist('Adele')
    twenty_one_id = insert_album('21', adele_id, '2011')
    insert_song('Rolling in the Deep', twenty_one_id, 'Adele', '00:03:48')
    insert_song('Someone Like You', twenty_one_id, 'Adele', '00:04:45')

    # Artist: Beyoncé
    beyonce_id = insert_artist('Beyoncé')
    lemonade_id = insert_album('Lemonade', beyonce_id, '2016')
    insert_song('Formation', lemonade_id, 'Beyoncé', '00:03:26')
    insert_song('Hold Up', lemonade_id, 'Beyoncé', '00:03:41')

    # Artist: Taylor Swift
    taylor_swift_id = insert_artist('Taylor Swift')
    folklore_id = insert_album('Folklore', taylor_swift_id, '2020')
    insert_song('Cardigan', folklore_id, 'Taylor Swift', '00:03:59')
    insert_song('Exile', folklore_id, 'Taylor Swift', '00:04:45')

populate_data()

# Fetch and display data
def get_albums_by_artist(artist_name):
    cursor.execute('''
    SELECT album.name, album.release_year FROM album
    JOIN artist ON artist.id = album.artist_id
    WHERE artist.name = ?
    ''', (artist_name,))
    albums = cursor.fetchall()
    return albums

def get_songs_by_album(album_name):
    cursor.execute('''
    SELECT song.name, song.artist, song.length FROM song
    JOIN album ON album.id = song.album_id
    WHERE album.name = ?
    ''', (album_name,))
    songs = cursor.fetchall()
    return songs

# Example: Fetch albums by The Beatles
albums_by_beatles = get_albums_by_artist('The Beatles')
print("Albums by The Beatles:", albums_by_beatles)

# Example: Fetch songs from Abbey Road
songs_in_abbey_road = get_songs_by_album('Abbey Road')
print("Songs in Abbey Road:", songs_in_abbey_road)

conn.close()