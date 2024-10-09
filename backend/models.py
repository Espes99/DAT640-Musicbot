from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

class Song(db.Model):
    id = db.Column(db.UUID, primary_key=True, default=uuid4)
    name = db.Column(db.String(100), unique=False, nullable=False)
    album_id = db.Column(db.UUID, db.ForeignKey('album.id'), nullable=False)
    artist = db.Column(db.String(100), unique=False, nullable=False)
    length = db.Column(db.DateTime, unique=False, nullable=False)
    album = db.relationship("Album", back_populates="songs")

    def __repr__(self):
        return f"{self.name}"

class Album(db.Model):
    id = db.Column(db.UUID, primary_key=True, default=uuid4)
    name = db.Column(db.String(100), unique=False, nullable=False)
    artist_id = db.Column(db.UUID, db.ForeignKey('artist.id'), nullable=False)
    release_year = db.Column(db.String(100), unique=False, nullable=False)
    artist = db.relationship("Artist", back_populates="albums")
    songs = db.relationship("Song", back_populates="album", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.name}"

class Artist(db.Model):
    id = db.Column(db.UUID, primary_key=True, default=uuid4)
    name = db.Column(db.String(100), unique=False, nullable=False)
    albums = db.relationship("Album", back_populates="artist", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.name}"
