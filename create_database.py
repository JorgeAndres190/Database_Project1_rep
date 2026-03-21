import sqlite3

conn = sqlite3.connect("netflix.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS Genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    genre_name TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Shows (
    show_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    release_year INTEGER,
    genre_id INTEGER,
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
)
""")

conn.commit()
conn.close()

print("Database and tables created successfully.")