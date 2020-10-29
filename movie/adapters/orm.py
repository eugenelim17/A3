from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship

from movie.domain import model

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
    Column('id', Integer, primary_key=True, autoincrement=True)
)

reviews = Table(
    'reviews', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.id')),
    Column('movie_id', ForeignKey('movies.id')),
    Column('review', String(1024), nullable=False),
    Column('timestamp', DateTime, nullable=False)
)

movies = Table(
    'movies', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('release_year', Integer, nullable=False),
    Column('title', String(255), nullable=False),
    Column('genres', String(1000), nullable=True),
    Column('description', String(1024), nullable=True),
    Column('director', String(255), nullable=True),
    Column('actors', String(1024), nullable=True)
)

genres = Table(
    'genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('genre_name', String(64), nullable=False)
)

movie_genres = Table(
    'movie_genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_id', ForeignKey('movies.id')),
    Column('genre_id', ForeignKey('genres.id'))
)


def map_model_to_tables():
    mapper(model.User, users, properties={
        '_User__username': users.c.username,
        '_User__password': users.c.password,
        '_User__reviews': relationship(model.Review, backref='_user')
    })
    mapper(model.Review, reviews, properties={
        '_Review__review': reviews.c.review,
        '_Review__timestamp': reviews.c.timestamp
    })
    movies_mapper = mapper(model.Movie, movies, properties={
        '_Movie__id': movies.c.id,
        '_Movie__release_year': movies.c.release_year,
        '_Movie__title': movies.c.title,
        '_Movie__genres': movies.c.genres,
        '_Movie__description': movies.c.description,
        '_Movie__director': movies.c.director,
        '_Movie__actors': movies.c.actors,
        '_Movie__reviews': relationship(model.Review, backref='_movie')
    })
    mapper(model.Genre, genres, properties={
        '_Genre__genre_name': genres.c.genre_name,
        '_Genre__genre_movies': relationship(
            movies_mapper,
            secondary=movie_genres,
            backref="_genres"
        )
    })
