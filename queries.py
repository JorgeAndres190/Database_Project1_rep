import sqlite3

conn = sqlite3.connect("netflix.db")
cur = conn.cursor()

print("\n--- Query 1: JOIN Shows and Genres ---")
cur.execute("""
    SELECT Shows.title, Shows.release_year, Genres.genre_name
    FROM Shows
    JOIN Genres
    ON Shows.genre_id = Genres.genre_id
    ORDER BY Shows.title
""")

for row in cur.fetchall():
    print(row)

print("\n--- Query 2: Count shows in each genre using GROUP BY ---")
cur.execute("""
    SELECT Genres.genre_name, COUNT(Shows.show_id) AS total_shows
    FROM Shows
    JOIN Genres
    ON Shows.genre_id = Genres.genre_id
    GROUP BY Genres.genre_name
    ORDER BY total_shows DESC
""")

for row in cur.fetchall():
    print(row)

print("\n--- Query 3: Genres with more than 5 shows using HAVING ---")
cur.execute("""
    SELECT Genres.genre_name, COUNT(Shows.show_id) AS total_shows
    FROM Shows
    JOIN Genres
    ON Shows.genre_id = Genres.genre_id
    GROUP BY Genres.genre_name
    HAVING COUNT(Shows.show_id) > 5
    ORDER BY total_shows DESC
""")

for row in cur.fetchall():
    print(row)

conn.close()