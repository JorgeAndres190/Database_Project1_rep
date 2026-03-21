import requests
import sqlite3

conn = sqlite3.connect("netflix.db")
cur = conn.cursor()

url = "https://api.tvmaze.com/shows"
response = requests.get(url)
shows = response.json()

for show in shows[:50]:
    title = show["name"]

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

    # Insert show
    cur.execute("""
        INSERT INTO Shows (title, release_year, genre_id)
        VALUES (?, ?, ?)
    """, (title, release_year, genre_id))

conn.commit()
conn.close()

print("Data inserted successfully.")