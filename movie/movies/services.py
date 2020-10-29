from typing import List, Iterable

from movie.adapters.repository import AbstractRepository
from movie.domain.model import Movie, Review, Genre, Actor, User, add_review as make_review


class NonExistentMovieException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def get_genre_names(repo: AbstractRepository):
    genres = repo.get_genres()
    genre_names = [genre.genre_name for genre in genres]

    return genre_names


def add_review(movie_id: int, review_text: str, user: User, repo: AbstractRepository):
    # Check that the movie exists.
    movie = repo.get_movie(movie_id)
    if movie is None:
        raise NonExistentMovieException

    if user is None:
        raise UnknownUserException

    # Create review.
    review = make_review(review_text, user, movie)

    # Update the repository.
    repo.add_review(review)


def get_movie_ids_for_title(title, repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_for_title(title)

    return movie_ids


def get_movie_ids_by_actor(actor_name, repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_by_actor(actor_name)
    return movie_ids


def get_movie_ids_by_genre(genre, repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_by_genre(genre)

    return movie_ids


def get_movies_by_genre(genre, repo: AbstractRepository):
    movies = repo.get_movies_by_genre(genre)

    return movies


def get_genres(repo: AbstractRepository):
    genres = repo.get_genres()

    return genres


def get_movies(repo: AbstractRepository):
    movies = repo.get_movies()
    return movies


def get_movie(movie_id: int, repo: AbstractRepository):
    movie = repo.get_movie(movie_id)

    if movie is None:
        raise NonExistentMovieException

    return movie_to_dict(movie)


def get_first_movie(repo: AbstractRepository):
    movie = repo.get_first_movie()

    return movie_to_dict(movie)


def get_last_movie(repo: AbstractRepository):
    movie = repo.get_last_movie()
    return movie_to_dict(movie)


def get_movies_by_release_year(target_year, repo: AbstractRepository):
    # Returns movies for the target year (empty if no matches), the year of the previous movie (might be null),
    # the year of the next movie (might be null)

    movies = repo.get_movies_by_release_year(target_year)

    movies_dto = list()
    if len(movies) > 0:
        # Convert Movies to dictionary form.
        movies_dto = movies_to_dict(movies)
    return movies_dto


def get_movies_by_id(id_list, repo: AbstractRepository):
    movies = repo.get_movies_by_id(id_list)

    # Convert Movies to dictionary form.
    movies_as_dict = movies_to_dict(movies)

    return movies_as_dict


def get_reviews_for_movie(movie_id, repo: AbstractRepository):
    movie = repo.get_movie(movie_id)

    if movie is None:
        raise NonExistentMovieException

    return reviews_to_dict(movie.reviews)


# ============================================
# Functions to convert model entities to dicts
# ============================================

def review_to_dict(review: Review):
    review_dict = {
        'movie_id': review.movie.id,
        'review_text': review.review_text,
        'timestamp': review.timestamp
    }
    return review_dict


def reviews_to_dict(reviews: Iterable[Review]):
    return [review_to_dict(review) for review in reviews]


def movie_to_dict(movie: Movie):
    movie_dict = {
        'id': movie.id,
        'title': movie.title,
        'release_year': movie.release_year,
        'director': movie.director,
        'actors': movie.actors,
        'genres': movie.genres,
        'description': movie.description,
        'reviews': movie.reviews
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie]):
    return [movie_to_dict(movie) for movie in movies]


def actor_to_dict(actor: Actor, repo: AbstractRepository):
    actor_dict = {
        'name': actor.actor_full_name,
        'actor_movies': repo.get_movie_ids_by_actor(actor.actor_full_name)
    }
    return actor_dict


def actors_to_dict(actors: Iterable[Actor], repo: AbstractRepository):
    return [actor_to_dict(actor, repo) for actor in actors]


def genre_to_dict(genre: Genre):
    genre_dict = {
        'name': genre.genre_name,
        'genre_movies': [movie.id for movie in genre.genre_movies]
    }
    return genre_dict


def genres_to_dict(genres: Iterable[Genre]):
    return [genre_to_dict(genre) for genre in genres]


# ============================================
# Functions to convert dicts to model entities
# ============================================

def dict_to_movie(dict):
    movie = Movie(dict.title, dict.release_year, dict.id)
    movie.add_actor(dict.actors)
    for genre in dict.genre:
        movie.add_genre(genre)
    movie.director = dict.director
    movie.runtime_minutes = dict.runtime_minutes
    movie.description = dict.description
    return movie
