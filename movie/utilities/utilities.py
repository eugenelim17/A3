from flask import Blueprint, request, render_template, redirect, url_for, session

import movie.adapters.repository as repo
import movie.utilities.services as services

# Configure Blueprint.
from movie.adapters import database_repository

utilities_blueprint = Blueprint(
    'utilities_bp', __name__)


def get_selected_movies(quantity=3):
    movies = services.get_random_movies(quantity, repo.repo_instance)
    movie_urls = dict()
    for movie in movies:
        movie_urls['hyperlink'] = url_for('movies_bp.movies_by_year', year=movie['release_year'])
    return movie_urls


def get_genres_and_urls():
    genre_names = services.get_genre_names(repo.repo_instance)
    genre_urls = dict()
    for genre_name in genre_names:
        genre_urls[genre_name] = url_for('movies_bp.movies_by_genre', genre=genre_name)

    return genre_urls


def get_actors_and_urls():
    actor_names = services.get_actor_names(repo.repo_instance)
    actor_urls = dict()
    for actor_name in actor_names:
        actor_urls[actor_name] = url_for('home_bp.movies_by_actor', actor=actor_name)
    return actor_urls
