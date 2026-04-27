
# data_manager.py
# Handles songs, users (MySQL), analytics, and recommendations

import os
import hashlib
from models import Song, User
import mysql_manager as db


# ─────────────────────────────────────────────
# PREDEFINED SONG DATASET
# ─────────────────────────────────────────────
SONGS_DATA = [
    # Pop
    {"song_id": 1,  "title": "Blinding Lights",     "artist": "The Weeknd",       "genre": "Pop",       "album": "After Hours",         "year": 2019, "duration": "3:20"},
    {"song_id": 2,  "title": "Shape of You",         "artist": "Ed Sheeran",       "genre": "Pop",       "album": "÷ (Divide)",          "year": 2017, "duration": "3:53"},
    {"song_id": 3,  "title": "Levitating",            "artist": "Dua Lipa",         "genre": "Pop",       "album": "Future Nostalgia",    "year": 2020, "duration": "3:23"},
    {"song_id": 4,  "title": "Stay",                  "artist": "The Kid LAROI",    "genre": "Pop",       "album": "F*CK LOVE 3",         "year": 2021, "duration": "2:21"},
    {"song_id": 5,  "title": "As It Was",             "artist": "Harry Styles",     "genre": "Pop",       "album": "Harry's House",       "year": 2022, "duration": "2:37"},
    {"song_id": 6,  "title": "Anti-Hero",             "artist": "Taylor Swift",     "genre": "Pop",       "album": "Midnights",           "year": 2022, "duration": "3:20"},
    {"song_id": 7,  "title": "Flowers",               "artist": "Miley Cyrus",      "genre": "Pop",       "album": "Endless Summer Vacation","year": 2023, "duration": "3:21"},
    {"song_id": 8,  "title": "Bad Guy",               "artist": "Billie Eilish",    "genre": "Pop",       "album": "When We All Fall Asleep","year": 2019, "duration": "3:14"},
    # Hip-Hop
    {"song_id": 9,  "title": "God's Plan",            "artist": "Drake",            "genre": "Hip-Hop",   "album": "Scorpion",            "year": 2018, "duration": "3:18"},
    {"song_id": 10, "title": "HUMBLE.",               "artist": "Kendrick Lamar",   "genre": "Hip-Hop",   "album": "DAMN.",               "year": 2017, "duration": "2:57"},
    {"song_id": 11, "title": "Rockstar",              "artist": "Post Malone",      "genre": "Hip-Hop",   "album": "Beerbongs & Bentleys","year": 2017, "duration": "3:38"},
    {"song_id": 12, "title": "Sicko Mode",            "artist": "Travis Scott",     "genre": "Hip-Hop",   "album": "Astroworld",          "year": 2018, "duration": "5:12"},
    {"song_id": 13, "title": "Lucid Dreams",          "artist": "Juice WRLD",       "genre": "Hip-Hop",   "album": "Goodbye & Good Riddance","year": 2018, "duration": "3:59"},
    {"song_id": 14, "title": "Old Town Road",         "artist": "Lil Nas X",        "genre": "Hip-Hop",   "album": "7 EP",                "year": 2019, "duration": "1:53"},
    {"song_id": 15, "title": "Sunflower",             "artist": "Post Malone",      "genre": "Hip-Hop",   "album": "Spider-Man OST",      "year": 2018, "duration": "2:38"},
    {"song_id": 16, "title": "Hotline Bling",         "artist": "Drake",            "genre": "Hip-Hop",   "album": "Views",               "year": 2015, "duration": "4:27"},
    # R&B
    {"song_id": 17, "title": "Peaches",               "artist": "Justin Bieber",    "genre": "R&B",       "album": "Justice",             "year": 2021, "duration": "3:18"},
    {"song_id": 18, "title": "Leave The Door Open",   "artist": "Bruno Mars",       "genre": "R&B",       "album": "An Evening...",       "year": 2021, "duration": "4:02"},
    {"song_id": 19, "title": "Essence",               "artist": "Wizkid",           "genre": "R&B",       "album": "Made in Lagos",       "year": 2020, "duration": "4:41"},
    {"song_id": 20, "title": "Heartless",             "artist": "Kanye West",       "genre": "R&B",       "album": "808s & Heartbreak",   "year": 2008, "duration": "3:31"},
    {"song_id": 21, "title": "Adorn",                 "artist": "Miguel",           "genre": "R&B",       "album": "Kaleidoscope Dream",  "year": 2012, "duration": "3:42"},
    {"song_id": 22, "title": "All of Me",             "artist": "John Legend",      "genre": "R&B",       "album": "Love in the Future",  "year": 2013, "duration": "4:29"},
    # Rock
    {"song_id": 23, "title": "Bohemian Rhapsody",     "artist": "Queen",            "genre": "Rock",      "album": "A Night at the Opera","year": 1975, "duration": "5:55"},
    {"song_id": 24, "title": "Hotel California",      "artist": "Eagles",           "genre": "Rock",      "album": "Hotel California",    "year": 1977, "duration": "6:30"},
    {"song_id": 25, "title": "Smells Like Teen Spirit","artist": "Nirvana",         "genre": "Rock",      "album": "Nevermind",           "year": 1991, "duration": "5:01"},
    {"song_id": 26, "title": "Sweet Child O' Mine",   "artist": "Guns N' Roses",    "genre": "Rock",      "album": "Appetite for Destruction","year": 1987, "duration": "5:56"},
    {"song_id": 27, "title": "Believer",              "artist": "Imagine Dragons",  "genre": "Rock",      "album": "Evolve",              "year": 2017, "duration": "3:24"},
    {"song_id": 28, "title": "Thunder",               "artist": "Imagine Dragons",  "genre": "Rock",      "album": "Evolve",              "year": 2017, "duration": "3:07"},
    {"song_id": 29, "title": "Yellow",                "artist": "Coldplay",         "genre": "Rock",      "album": "Parachutes",          "year": 2000, "duration": "4:29"},
    {"song_id": 30, "title": "The Scientist",         "artist": "Coldplay",         "genre": "Rock",      "album": "A Rush of Blood",     "year": 2002, "duration": "5:09"},
    # Electronic / Dance
    {"song_id": 31, "title": "Clarity",               "artist": "Zedd",             "genre": "Electronic","album": "Clarity",             "year": 2012, "duration": "4:30"},
    {"song_id": 32, "title": "Wake Me Up",            "artist": "Avicii",           "genre": "Electronic","album": "True",                "year": 2013, "duration": "4:07"},
    {"song_id": 33, "title": "Titanium",              "artist": "David Guetta",     "genre": "Electronic","album": "Nothing but the Beat","year": 2011, "duration": "4:05"},
    {"song_id": 34, "title": "Animals",               "artist": "Martin Garrix",    "genre": "Electronic","album": "Animals EP",          "year": 2013, "duration": "6:18"},
    {"song_id": 35, "title": "Lean On",               "artist": "Major Lazer",      "genre": "Electronic","album": "Peace is the Mission","year": 2015, "duration": "2:56"},
    {"song_id": 36, "title": "Levels",                "artist": "Avicii",           "genre": "Electronic","album": "Levels EP",           "year": 2011, "duration": "5:38"},
    # Jazz
    {"song_id": 37, "title": "Take Five",             "artist": "Dave Brubeck",     "genre": "Jazz",      "album": "Time Out",            "year": 1959, "duration": "5:26"},
    {"song_id": 38, "title": "So What",               "artist": "Miles Davis",      "genre": "Jazz",      "album": "Kind of Blue",        "year": 1959, "duration": "9:22"},
    {"song_id": 39, "title": "Autumn Leaves",         "artist": "Bill Evans",       "genre": "Jazz",      "album": "Portrait in Jazz",    "year": 1959, "duration": "5:35"},
    {"song_id": 40, "title": "Fly Me to the Moon",   "artist": "Frank Sinatra",    "genre": "Jazz",      "album": "It Might as Well...", "year": 1964, "duration": "2:28"},
    # Classical
    {"song_id": 41, "title": "Moonlight Sonata",      "artist": "Beethoven",        "genre": "Classical", "album": "Piano Sonatas",       "year": 1801, "duration": "15:00"},
    {"song_id": 42, "title": "Fur Elise",             "artist": "Beethoven",        "genre": "Classical", "album": "Bagatelles",          "year": 1810, "duration": "3:00"},
    {"song_id": 43, "title": "Canon in D",            "artist": "Pachelbel",        "genre": "Classical", "album": "Chamber Music",       "year": 1680, "duration": "6:00"},
    # Latin
    {"song_id": 44, "title": "Despacito",             "artist": "Luis Fonsi",       "genre": "Latin",     "album": "Vida",                "year": 2017, "duration": "3:48"},
    {"song_id": 45, "title": "Con Calma",             "artist": "Daddy Yankee",     "genre": "Latin",     "album": "Con Calma",           "year": 2019, "duration": "3:15"},
    {"song_id": 46, "title": "Taki Taki",             "artist": "DJ Snake",         "genre": "Latin",     "album": "Carte Blanche",       "year": 2018, "duration": "3:32"},
    # Soul / Indie
    {"song_id": 47, "title": "Redbone",               "artist": "Childish Gambino", "genre": "Soul",      "album": "Awaken, My Love!",    "year": 2016, "duration": "5:26"},
    {"song_id": 48, "title": "This Is America",       "artist": "Childish Gambino", "genre": "Soul",      "album": "Single",              "year": 2018, "duration": "3:44"},
    {"song_id": 49, "title": "Electric Feel",         "artist": "MGMT",             "genre": "Indie",     "album": "Oracular Spectacular","year": 2007, "duration": "3:49"},
    {"song_id": 50, "title": "Mr. Brightside",        "artist": "The Killers",      "genre": "Indie",     "album": "Hot Fuss",            "year": 2003, "duration": "3:42"},
]


DATA_DIR = "pyspotify_data"


class DataManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.songs = self._load_songs()
        self.users = self._load_users()
        self.analytics = self._load_analytics()

    # ───────────────── SONGS ─────────────────

    def _load_songs(self):
        songs = {}
        for data in SONGS_DATA:
            song = Song.from_dict(data)
            songs[song.song_id] = song
        return songs

    def get_all_songs(self):
        return list(self.songs.values())

    def get_song(self, song_id):
        return self.songs.get(song_id)

    def search_songs(self, query):
        q = query.lower().strip()
        return list(filter(
            lambda s: q in s.title.lower() or q in s.artist.lower(),
            self.songs.values()
        ))

    def get_songs_by_genre(self, genre):
        return list(filter(lambda s: s.genre == genre, self.songs.values()))

    def get_genres(self):
        return sorted(set(s.genre for s in self.songs.values()))

    # ───────────────── USERS (MySQL) ─────────────────

    def _load_users(self):
        return {}

    def save_users(self):
        pass

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def save_user(self, user):
        self.users[user.username] = user
        db.save_user(user)

    def register_user(self, username, password):
        if not username or not password:
            return False, "Username and password cannot be empty."

        if db.user_exists(username):
            return False, "Username already exists."

        if len(password) < 4:
            return False, "Password must be at least 4 characters."

        hashed_password = self.hash_password(password)
        user = User(username, hashed_password)

        db.save_user(user)
        self.users[username] = user

        return True, "Account created successfully!"

    def login_user(self, username, password):
        user = db.load_user(username)

        if not user:
            return False, "Username not found."

        hashed_password = self.hash_password(password)

        if user.password != hashed_password:
            return False, "Incorrect password."

        self.users[username] = user
        return True, user

    # ───────────────── ANALYTICS ─────────────────

    def _load_analytics(self):
        return db.load_analytics()

    def save_analytics(self):
        db.save_analytics(self.analytics)

    def record_song_play(self, song_id):
        key = str(song_id)
        self.analytics[key] = self.analytics.get(key, 0) + 1

        if song_id in self.songs:
            self.songs[song_id].play_count = self.analytics[key]

        self.save_analytics()

    def get_top_songs(self, n=5):
        sorted_ids = sorted(
            self.analytics,
            key=lambda k: self.analytics[k],
            reverse=True
        )

        result = []
        for sid in sorted_ids[:n]:
            song = self.songs.get(int(sid))
            if song:
                result.append((song, self.analytics[sid]))

        return result

    def get_top_genres(self, n=3):
        genre_counts = {}

        for sid, count in self.analytics.items():
            song = self.songs.get(int(sid))
            if song:
                genre_counts[song.genre] = genre_counts.get(song.genre, 0) + count

        return sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:n]

    # ───────────────── RECOMMENDATIONS ─────────────────

    def get_recommendations(self, user, limit=6):
        recommendations = []

        recent_genres = []
        for sid in user.recently_played[:5]:
            song = self.songs.get(sid)
            if song:
                recent_genres.append(song.genre)

        liked = set(user.liked_song_ids)

        if recent_genres:
            preferred_genre = max(set(recent_genres), key=recent_genres.count)

            genre_songs = list(filter(
                lambda s: s.genre == preferred_genre and s.song_id not in liked,
                self.songs.values()
            ))

            recommendations.extend(genre_songs[:limit])

        if len(recommendations) < limit:
            top = [s for s, _ in self.get_top_songs(20)]

            for s in top:
                if s not in recommendations and s.song_id not in liked:
                    recommendations.append(s)

                if len(recommendations) >= limit:
                    break

        if not recommendations:
            recommendations = [
                s for s in self.songs.values()
                if s.song_id not in liked
            ][:limit]

        return recommendations[:limit]
