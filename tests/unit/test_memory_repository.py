from datetime import date, datetime
from typing import List

import pytest

from movie.domain.model import User, Movie, Genre, Review, add_review
from movie.adapters.repository import RepositoryException


def test_repository_can_add_a_user(in_memory_repo):
    user = User('Dave', '123456789')
    in_memory_repo.add_user(user)
    assert user in in_memory_repo._users
    assert in_memory_repo.get_user('dave') is user


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = User('fmercury', '8734gfe2058v')
    in_memory_repo.add_user(user)
    user = in_memory_repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_movie_count(in_memory_repo):
    number_of_movies = in_memory_repo.get_number_of_movies()

    # Check that the query returned 6 Movies.
    assert number_of_movies == 1000


def test_repository_can_add_movie(in_memory_repo):
    movie = Movie('Moana', 2016)
    in_memory_repo.add_movie(movie)
    assert in_memory_repo.get_movie(1001) is movie


def test_repository_can_retrieve_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(1)

    # Check that the movie has the expected title.
    assert movie.title == 'Guardians of the Galaxy'

    # Check that the Movie is reviewed as expected.
    review_one = [review for review in movie.reviews if review.review_text == "I love this movie"][
        0]
    review_two = [review for review in movie.reviews if review.review_text == "Master piece!"][0]

    assert review_one.user.username == 'fmercury'
    assert review_two.user.username == "thorke"

    # Check that the Movie has the expected genre.
    assert movie.has_genre(Genre('Action'))
    assert movie.has_genre(Genre('Adventure'))


def test_repository_does_not_retrieve_a_non_existent_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(1001)
    assert movie is None


def test_repository_can_retrieve_movies_by_year(in_memory_repo):
    movies = in_memory_repo.get_movies_by_release_year(2016)

    # Check that the query returned 297 Movies.
    assert len(movies) == 297


def test_repository_does_not_retrieve_a_movie_when_there_are_no_movies_for_a_given_year(in_memory_repo):
    movies = in_memory_repo.get_movies_by_release_year(2017)
    assert len(movies) == 0


def test_repository_can_get_first_movie(in_memory_repo):
    movie = in_memory_repo.get_first_movie()
    assert movie.title == 'Guardians of the Galaxy'


def test_repository_can_get_last_movie(in_memory_repo):
    movie = in_memory_repo.get_last_movie()
    assert  movie.title == 'Nine Lives'


def test_repository_can_get_movies_by_ids(in_memory_repo):
    movies = in_memory_repo.get_movies_by_id([2, 3, 4])

    assert len(movies) == 3
    assert movies[0].title == 'Prometheus'
    assert movies[1].title == "Split"
    assert movies[2].title == 'Sing'


def test_repository_does_not_retrieve_movie_for_non_existent_id(in_memory_repo):
    movies = in_memory_repo.get_movies_by_id([2, 1001])
    assert len(movies) == 1


def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    movies = in_memory_repo.get_movies_by_id([0, 1001])

    assert len(movies) == 0


def test_repository_returns_movie_ids_by_genre(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_by_genre('Action')

    assert 991 in movie_ids
    assert 949 in movie_ids


def test_repository_returns_an_empty_list_for_non_existent_genre(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_by_genre('Frightening')

    assert len(movie_ids) == 0


def test_repository_can_add_a_genre(in_memory_repo):
    genre = Genre('Annoying')
    in_memory_repo.add_genre(genre)

    assert genre in in_memory_repo.get_genres()


def test_repository_can_add_a_review(in_memory_repo):
    user = User('thorke', '902fjsdf')
    movie = in_memory_repo.get_movie(2)
    review = add_review("Highly recommended!", user, movie, 0)

    in_memory_repo.add_review(review)

    assert review in in_memory_repo.get_reviews()


def test_repository_can_retrieve_reviews(in_memory_repo):
    assert len(in_memory_repo.get_reviews()) == 2



