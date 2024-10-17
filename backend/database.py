import sqlite3
import os
import song 

# Define the path to your database file
DB_PATH = os.path.join('data', 'music.db')

def get_db_connection():
    """Creates and returns a database connection."""
    conn = sqlite3.connect(DB_PATH)
    return conn

def initialize_database():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create artist table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    # Create album table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS album (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            artist_id INTEGER NOT NULL,
            release_year INTEGER,
            FOREIGN KEY(artist_id) REFERENCES artist(id)
        )
    ''')

    # Create song table
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
    """Returns song details by song name, case-insensitive."""
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


# Population code
# import sqlite3
# import os

# # Define the path to your database file
# DB_PATH = os.path.join('data', 'music.db')

# def get_db_connection():
#     """Creates and returns a database connection."""
#     conn = sqlite3.connect(DB_PATH)
#     return conn

# def initialize_database():
#     """Initializes the database and creates tables if they don't exist."""
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Create artist table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS artist (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL
#         )
#     ''')

#     # Create album table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS album (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             artist_id INTEGER NOT NULL,
#             release_year INTEGER,
#             FOREIGN KEY(artist_id) REFERENCES artist(id)
#         )
#     ''')

#     # Create song table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS song (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             album_id INTEGER,
#             artist TEXT NOT NULL,
#             length TEXT NOT NULL,
#             FOREIGN KEY(album_id) REFERENCES album(id)
#         )
#     ''')

#     conn.commit()
#     conn.close()

# def populate_database():
#     """Populates the database with artists, albums, and songs."""
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Sample data for artists
#     artists = [
#         ('The Beatles',),
#         ('Queen',),
#         ('Michael Jackson',),
#         ('Taylor Swift',),
#         ('Ed Sheeran',),
#         ('Adele',),
#         ('Bruno Mars',),
#         ('Beyoncé',),
#         ('Coldplay',),
#         ('Maroon 5',)
#     ]

#     # Insert artists into the database
#     cursor.executemany('INSERT INTO artist (name) VALUES (?)', artists)
#     conn.commit()

#     # Fetch artist IDs
#     cursor.execute('SELECT id, name FROM artist')
#     artist_dict = {name: artist_id for artist_id, name in cursor.fetchall()}

#     # Sample data for albums
#     albums = [
#         ('Abbey Road', artist_dict['The Beatles'], 1969),
#         ('A Night at the Opera', artist_dict['Queen'], 1975),
#         ('Thriller', artist_dict['Michael Jackson'], 1982),
#         ('1989', artist_dict['Taylor Swift'], 2014),
#         ('÷ (Divide)', artist_dict['Ed Sheeran'], 2017),
#         ('25', artist_dict['Adele'], 2015),
#         ('Doo-Wops & Hooligans', artist_dict['Bruno Mars'], 2010),
#         ('Lemonade', artist_dict['Beyoncé'], 2016),
#         ('A Head Full of Dreams', artist_dict['Coldplay'], 2015),
#         ('Songs About Jane', artist_dict['Maroon 5'], 2002)
#     ]

#     # Insert albums into the database
#     cursor.executemany('INSERT INTO album (name, artist_id, release_year) VALUES (?, ?, ?)', albums)
#     conn.commit()

#     # Fetch album IDs
#     cursor.execute('SELECT id, name FROM album')
#     album_dict = {name: album_id for album_id, name in cursor.fetchall()}

#     # Sample data for songs
#     songs = [
#         # Songs by The Beatles
#         ('Come Together', album_dict['Abbey Road'], 'The Beatles', '4:20'),
#         ('Something', album_dict['Abbey Road'], 'The Beatles', '3:03'),
#         ('Here Comes the Sun', album_dict['Abbey Road'], 'The Beatles', '3:06'),
#         ('Let It Be', None, 'The Beatles', '4:03'),

#         # Songs by Queen
#         ('Bohemian Rhapsody', album_dict['A Night at the Opera'], 'Queen', '5:55'),
#         ('Love of My Life', album_dict['A Night at the Opera'], 'Queen', '3:38'),
#         ('Don\'t Stop Me Now', None, 'Queen', '3:29'),

#         # Songs by Michael Jackson
#         ('Thriller', album_dict['Thriller'], 'Michael Jackson', '5:57'),
#         ('Beat It', album_dict['Thriller'], 'Michael Jackson', '4:18'),
#         ('Billie Jean', album_dict['Thriller'], 'Michael Jackson', '4:54'),

#         # Songs by Taylor Swift
#         ('Blank Space', album_dict['1989'], 'Taylor Swift', '3:51'),
#         ('Shake It Off', album_dict['1989'], 'Taylor Swift', '3:39'),
#         ('Style', album_dict['1989'], 'Taylor Swift', '3:51'),

#         # Songs by Ed Sheeran
#         ('Shape of You', album_dict['÷ (Divide)'], 'Ed Sheeran', '3:53'),
#         ('Perfect', album_dict['÷ (Divide)'], 'Ed Sheeran', '4:23'),
#         ('Galway Girl', album_dict['÷ (Divide)'], 'Ed Sheeran', '2:50'),

#         # Songs by Adele
#         ('Hello', album_dict['25'], 'Adele', '4:55'),
#         ('When We Were Young', album_dict['25'], 'Adele', '4:50'),
#         ('Send My Love', album_dict['25'], 'Adele', '3:43'),

#         # Songs by Bruno Mars
#         ('Just the Way You Are', album_dict['Doo-Wops & Hooligans'], 'Bruno Mars', '3:40'),
#         ('Grenade', album_dict['Doo-Wops & Hooligans'], 'Bruno Mars', '3:42'),
#         ('The Lazy Song', album_dict['Doo-Wops & Hooligans'], 'Bruno Mars', '3:09'),

#         # Songs by Beyoncé
#         ('Formation', album_dict['Lemonade'], 'Beyoncé', '3:26'),
#         ('Sorry', album_dict['Lemonade'], 'Beyoncé', '3:53'),
#         ('Hold Up', album_dict['Lemonade'], 'Beyoncé', '3:41'),

#         # Songs by Coldplay
#         ('Adventure of a Lifetime', album_dict['A Head Full of Dreams'], 'Coldplay', '4:23'),
#         ('Hymn for the Weekend', album_dict['A Head Full of Dreams'], 'Coldplay', '4:18'),
#         ('Up&Up', album_dict['A Head Full of Dreams'], 'Coldplay', '6:45'),

#         # Songs by Maroon 5
#         ('She Will Be Loved', album_dict['Songs About Jane'], 'Maroon 5', '4:17'),
#         ('This Love', album_dict['Songs About Jane'], 'Maroon 5', '3:26'),
#         ('Sunday Morning', album_dict['Songs About Jane'], 'Maroon 5', '4:06'),

#         # Additional songs without albums
#         ('Uptown Funk', None, 'Bruno Mars', '4:30'),
#         ('Rolling in the Deep', None, 'Adele', '3:48'),
#         ('Yellow', None, 'Coldplay', '4:29'),
#         ('Bad Guy', None, 'Billie Eilish', '3:14'),
#         ('Blinding Lights', None, 'The Weeknd', '3:20'),
#         ('Levitating', None, 'Dua Lipa', '3:23'),
#         ('Watermelon Sugar', None, 'Harry Styles', '2:54'),
#         ('Drivers License', None, 'Olivia Rodrigo', '4:02'),
#         ('Happy', None, 'Pharrell Williams', '3:53'),
#         ('Shake It Off', None, 'Taylor Swift', '3:39'),  # Duplicate song to show handling
#     ]

#     # Insert songs into the database
#     cursor.executemany('INSERT INTO song (name, album_id, artist, length) VALUES (?, ?, ?, ?)', songs)
#     conn.commit()

#     conn.close()
#     print("Database has been populated with sample data.")

# if __name__ == '__main__':
#     initialize_database()
#     populate_database()
