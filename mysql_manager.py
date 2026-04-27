# mysql_manager.py - MySQL version of data persistence
# Drop-in replacement for the JSON file storage in data_manager.py

import mysql.connector
import json
from db_config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from models import User, Playlist


def get_connection():
    """Create and return a MySQL connection."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def save_user(user):
    """Insert or update a user in MySQL."""
    conn = get_connection()
    cursor = conn.cursor()
    liked = json.dumps(user.liked_song_ids)
    recent = json.dumps(user.recently_played)
    cursor.execute("""
        INSERT INTO users (username, password, liked_songs, recently_played)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            password=VALUES(password),
            liked_songs=VALUES(liked_songs),
            recently_played=VALUES(recently_played)
    """, (user.username, user.password, liked, recent))

    # Save playlists
    cursor.execute("DELETE FROM playlists WHERE owner=%s", (user.username,))
    for pl in user.playlists:
        cursor.execute("""
            INSERT INTO playlists (name, owner, song_ids, created_at)
            VALUES (%s, %s, %s, %s)
        """, (pl.name, user.username, json.dumps(pl.song_ids), pl.created_at))

    conn.commit()
    cursor.close()
    conn.close()


def load_user(username):
    """Load a User object from MySQL. Returns None if not found."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None

    user = User(row["username"], row["password"])
    user.liked_song_ids  = json.loads(row["liked_songs"]   or "[]")
    user.recently_played = json.loads(row["recently_played"] or "[]")

    # Load playlists
    cursor.execute("SELECT * FROM playlists WHERE owner=%s", (username,))
    for prow in cursor.fetchall():
        pl = Playlist(prow["name"], prow["owner"])
        pl.song_ids   = json.loads(prow["song_ids"] or "[]")
        pl.created_at = str(prow["created_at"])
        user.playlists.append(pl)

    cursor.close()
    conn.close()
    return user


def user_exists(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None


def save_analytics(analytics_dict):
    """Save play counts to MySQL."""
    conn = get_connection()
    cursor = conn.cursor()
    for song_id, count in analytics_dict.items():
        cursor.execute("""
            INSERT INTO analytics (song_id, play_count)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE play_count=VALUES(play_count)
        """, (int(song_id), count))
    conn.commit()
    cursor.close()
    conn.close()


def load_analytics():
    """Load analytics from MySQL. Returns dict {song_id_str: count}."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT song_id, play_count FROM analytics")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {str(r[0]): r[1] for r in rows}