# models.py - Core data models for PySpotify
# Contains OOP classes: User, Song, Playlist

import json
import os
from datetime import datetime


class Song:
    """Represents a music track with metadata."""

    def __init__(self, song_id, title, artist, genre, album="Unknown", year=2020, duration="3:30"):
        self.song_id = song_id
        self.title = title
        self.artist = artist
        self.genre = genre
        self.album = album
        self.year = year
        self.duration = duration
        self.play_count = 0  # analytics: how many times selected

    def to_dict(self):
        """Convert song to dictionary for JSON storage."""
        return {
            "song_id": self.song_id,
            "title": self.title,
            "artist": self.artist,
            "genre": self.genre,
            "album": self.album,
            "year": self.year,
            "duration": self.duration,
            "play_count": self.play_count
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Song instance from a dictionary."""
        song = cls(
            data["song_id"], data["title"], data["artist"],
            data["genre"], data.get("album", "Unknown"),
            data.get("year", 2020), data.get("duration", "3:30")
        )
        song.play_count = data.get("play_count", 0)
        return song

    def __repr__(self):
        return f"Song({self.title} by {self.artist})"


class Playlist:
    """Represents a user-created playlist of songs."""

    def __init__(self, name, owner_username):
        self.name = name
        self.owner = owner_username
        self.song_ids = []  # list of song IDs
        self.created_at = datetime.now().strftime("%Y-%m-%d")

    def add_song(self, song_id):
        """Add a song to playlist if not already present."""
        if song_id not in self.song_ids:
            self.song_ids.append(song_id)
            return True
        return False  # already in playlist

    def remove_song(self, song_id):
        """Remove a song from the playlist."""
        if song_id in self.song_ids:
            self.song_ids.remove(song_id)
            return True
        return False

    def to_dict(self):
        return {
            "name": self.name,
            "owner": self.owner,
            "song_ids": self.song_ids,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        pl = cls(data["name"], data["owner"])
        pl.song_ids = data.get("song_ids", [])
        pl.created_at = data.get("created_at", "")
        return pl


class User:
    """Represents a registered user of PySpotify."""

    def __init__(self, username, password):
        self.username = username
        self.password = password          # stored as plain text (beginner scope)
        self.liked_song_ids = []          # favorites
        self.playlists = []               # list of Playlist objects
        self.recently_played = []         # last 10 song IDs

    def like_song(self, song_id):
        """Toggle like status for a song."""
        if song_id in self.liked_song_ids:
            self.liked_song_ids.remove(song_id)
            return False  # unliked
        else:
            self.liked_song_ids.append(song_id)
            return True   # liked

    def is_liked(self, song_id):
        return song_id in self.liked_song_ids

    def add_to_recently_played(self, song_id):
        """Track recently played songs (max 10)."""
        if song_id in self.recently_played:
            self.recently_played.remove(song_id)
        self.recently_played.insert(0, song_id)
        self.recently_played = self.recently_played[:10]  # keep only last 10

    def create_playlist(self, name):
        """Create a new playlist."""
        # Check for duplicate names
        existing = [p.name for p in self.playlists]
        if name in existing:
            return None
        pl = Playlist(name, self.username)
        self.playlists.append(pl)
        return pl

    def get_playlist(self, name):
        """Find a playlist by name."""
        for pl in self.playlists:
            if pl.name == name:
                return pl
        return None

    def delete_playlist(self, name):
        """Delete a playlist by name."""
        self.playlists = [p for p in self.playlists if p.name != name]

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "liked_song_ids": self.liked_song_ids,
            "playlists": [p.to_dict() for p in self.playlists],
            "recently_played": self.recently_played
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data["username"], data["password"])
        user.liked_song_ids = data.get("liked_song_ids", [])
        user.recently_played = data.get("recently_played", [])
        user.playlists = [Playlist.from_dict(p) for p in data.get("playlists", [])]
        return user
