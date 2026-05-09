from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlalchemy import text
from typing import Optional

app = FastAPI()

DATABASE_URL = "sqlite:///netflix.db"
engine = create_engine(DATABASE_URL, echo=True)


class Genre(SQLModel, table=True):
    __tablename__ = "Genres"

    genre_id: Optional[int] = Field(default=None, primary_key=True)
    genre_name: str


class Show(SQLModel, table=True):
    __tablename__ = "Shows"

    show_id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    release_year: Optional[int] = None
    genre_id: Optional[int] = Field(default=None, foreign_key="Genres.genre_id")
    description: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None


def ensure_description_column():
    with Session(engine) as session:
        result = session.exec(text("PRAGMA table_info(Shows)"))
        columns = [row[1] for row in result]

        if "description" not in columns:
            session.exec(text("ALTER TABLE Shows ADD COLUMN description TEXT"))
            session.commit()


def ensure_image_url_column():
    with Session(engine) as session:
        result = session.exec(text("PRAGMA table_info(Shows)"))
        columns = [row[1] for row in result]

        if "image_url" not in columns:
            session.exec(text("ALTER TABLE Shows ADD COLUMN image_url TEXT"))
            session.commit()


def ensure_rating_column():
    with Session(engine) as session:
        result = session.exec(text("PRAGMA table_info(Shows)"))
        columns = [row[1] for row in result]

        if "rating" not in columns:
            session.exec(text("ALTER TABLE Shows ADD COLUMN rating REAL"))
            session.commit()


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    ensure_description_column()
    ensure_image_url_column()
    ensure_rating_column()


@app.get("/genres")
def get_genres():
    with Session(engine) as session:
        genres = session.exec(select(Genre)).all()
        return genres


@app.get("/shows")
def get_shows():
    with Session(engine) as session:
        shows = session.exec(select(Show)).all()
        return shows


@app.get("/shows/{show_id}")
def get_show(show_id: int):
    with Session(engine) as session:
        show = session.get(Show, show_id)
        return show


@app.get("/shows/search/{title}")
def search_shows(title: str):
    with Session(engine) as session:
        statement = select(Show).where(Show.title.contains(title))
        results = session.exec(statement).all()
        return results


app.mount("/", StaticFiles(directory="static", html=True), name="static")