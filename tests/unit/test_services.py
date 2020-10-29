from datetime import date

import pytest

from movie.authentication.services import AuthenticationException
from movie.domain.model import User
from movie.movies import services as movies_services
from movie.authentication import services as auth_services
from movie.movies.services import NonExistentMovieException


def test_can_add_user(in_memory_repo):
    new_username = 'jz'
    new_password = 'abcd1A23'

    auth_services.add_user(new_username, new_password, in_memory_repo)

    user_as_dict = auth_services.get_user(new_username, in_memory_repo)
    assert user_as_dict['username'] == new_username

    # Check that password has been encrypted.
    assert user_as_dict['password'].startswith('pbkdf2:sha256:')


def test_cannot_add_user_with_existing_name(in_memory_repo):
    username = 'thorke'
    password = 'abcd1A23'

    with pytest.raises(auth_services.NameNotUniqueException):
        auth_services.add_user(username, password, in_memory_repo)


def test_authentication_with_valid_credentials(in_memory_repo):
    new_username = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_username, new_password, in_memory_repo)

    try:
        auth_services.authenticate_user(new_username, new_password, in_memory_repo)
    except AuthenticationException:
        assert False


def test_authentication_with_invalid_credentials(in_memory_repo):
    new_username = 'pmccartney'
    new_password = 'abcd1A23'

    auth_services.add_user(new_username, new_password, in_memory_repo)

    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user(new_username, '0987654321', in_memory_repo)


def test_can_add_review(in_memory_repo):
    movie_id = 3
    review_text = 'Really Enjoyableeeee!!'
    user = User('fmercury', 'ASdwdc9')

    # Call the service layer to add the review.
    movies_services.add_review(movie_id, review_text, user, in_memory_repo)

    # Retrieve the reviews for the movie from the repository.
    reviews_as_dict = movies_services.get_reviews_for_movie(movie_id, in_memory_repo)

    # Check that the reviews include a review with the new review text.
    assert next(
        (dictionary['review_text'] for dictionary in reviews_as_dict if dictionary['review_text'] == review_text),
        None) is not None


def test_can_get_movie(in_memory_repo):
    movie_id = 1

    movie_as_dict = movies_services.get_movie(movie_id, in_memory_repo)

    assert movie_as_dict['id'] == movie_id
    assert movie_as_dict['release_year'] == 2014
    assert movie_as_dict['title'] == 'Guardians of the Galaxy'
    assert len(movie_as_dict['reviews']) == 2

    genre_names = [genre.genre_name for genre in movie_as_dict['genres']]
    assert 'Action' in genre_names
    assert 'Adventure' in genre_names
    assert 'Sci-Fi' in genre_names


def test_cannot_get_movie_with_non_existent_id(in_memory_repo):
    movie_id = 1004

    # Call the service layer to attempt to retrieve the movie.
    with pytest.raises(movies_services.NonExistentMovieException):
        movies_services.get_movie(movie_id, in_memory_repo)


def test_get_first_movie(in_memory_repo):
    movie_as_dict = movies_services.get_first_movie(in_memory_repo)

    assert movie_as_dict['id'] == 1


def test_get_last_article(in_memory_repo):
    movie_as_dict = movies_services.get_last_movie(in_memory_repo)

    assert movie_as_dict['id'] == 1000


def test_get_movies_by_release_year_with_one_year(in_memory_repo):
    target_year = 2009

    movies_as_dict = movies_services.get_movies_by_release_year(target_year, in_memory_repo)

    assert len(movies_as_dict) == 51
    assert movies_as_dict[0]['id'] == 78


def test_get_movies_by_release_year_with_non_existent_year(in_memory_repo):
    target_year = 2020

    movies_as_dict = movies_services.get_movies_by_release_year(target_year, in_memory_repo)

    # Check that there are no movie released in 2020 in our csv file.
    assert len(movies_as_dict) == 0


def test_get_movies_by_id(in_memory_repo):
    target_movie_ids = [5, 6, 7, 8]
    movies_as_dict = movies_services.get_movies_by_id(target_movie_ids, in_memory_repo)

    # Check that 2 movies were returned from the query.
    assert len(movies_as_dict) == 4

    # Check that the movie ids returned were 5 and 6.
    movie_ids = [movie['id'] for movie in movies_as_dict]
    assert {5, 6}.issubset(movie_ids)


def test_get_reviews_for_movie(in_memory_repo):
    reviews_as_dict = movies_services.get_reviews_for_movie(1, in_memory_repo)

    # Check that 2 reviews were returned for movie with id 1.
    assert len(reviews_as_dict) == 2

    # Check that the reviews relate to the movie whose id is 1.
    movie_ids = [review['movie_id'] for review in reviews_as_dict]
    movie_ids = set(movie_ids)
    assert 1 in movie_ids and len(movie_ids) == 1


def test_get_reviews_for_non_existent_movie(in_memory_repo):
    with pytest.raises(NonExistentMovieException):
        reviews_as_dict = movies_services.get_reviews_for_movie(1009, in_memory_repo)


def test_get_reviews_for_movie_without_reviews(in_memory_repo):
    reviews_as_dict = movies_services.get_reviews_for_movie(2, in_memory_repo)
    assert len(reviews_as_dict) == 0
