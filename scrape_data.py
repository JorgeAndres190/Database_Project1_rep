import requests
import sqlite3
import re
import html

conn = sqlite3.connect("netflix.db")
cur = conn.cursor()


def ensure_description_column():
    cur.execute("PRAGMA table_info(Shows)")
    columns = [row[1] for row in cur.fetchall()]

    if "description" not in columns:
        cur.execute("ALTER TABLE Shows ADD COLUMN description TEXT")


def ensure_image_url_column():
    cur.execute("PRAGMA table_info(Shows)")
    columns = [row[1] for row in cur.fetchall()]

    if "image_url" not in columns:
        cur.execute("ALTER TABLE Shows ADD COLUMN image_url TEXT")


def ensure_rating_column():
    cur.execute("PRAGMA table_info(Shows)")
    columns = [row[1] for row in cur.fetchall()]

    if "rating" not in columns:
        cur.execute("ALTER TABLE Shows ADD COLUMN rating REAL")


def clean_summary(summary):
    if not summary:
        return "No description available."

    text = re.sub(r"<[^>]+>", "", summary)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()

    return text or "No description available."


ensure_description_column()
ensure_image_url_column()
ensure_rating_column()
conn.commit()

url = "https://api.tvmaze.com/shows"
response = requests.get(url)
shows = response.json()

for show in shows[:50]:
    title = show["name"]
    summary = show.get("summary")
    description = clean_summary(summary)
    image_url = show["image"]["medium"] if show.get("image") else None
    rating = show["rating"]["average"] if show.get("rating") and show["rating"].get("average") else None

    if show["premiered"]:
        release_year = int(show["premiered"][:4])
    else:
        release_year = None

    if show["genres"]:
        genre_name = show["genres"][0]
    else:
        genre_name = "Unknown"

    # Insert genre if it does not already exist
    cur.execute("""
        INSERT OR IGNORE INTO Genres (genre_name)
        VALUES (?)
    """, (genre_name,))

    # Get the genre_id
    cur.execute("""
        SELECT genre_id
        FROM Genres
        WHERE genre_name = ?
    """, (genre_name,))
    genre_id = cur.fetchone()[0]

    cur.execute("""
        SELECT show_id
        FROM Shows
        WHERE title = ?
    """, (title,))
    existing_show = cur.fetchone()

    if existing_show:
        cur.execute("""
            UPDATE Shows
            SET release_year = ?, genre_id = ?, description = ?, image_url = ?, rating = ?
            WHERE show_id = ?
        """, (release_year, genre_id, description, image_url, rating, existing_show[0]))
    else:
        cur.execute("""
            INSERT INTO Shows (title, release_year, genre_id, description, image_url, rating)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, release_year, genre_id, description, image_url, rating))

conn.commit()
conn.close()

print("Data inserted successfully.")