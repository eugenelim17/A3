from datetime import date, datetime

import pytest

from movie.adapters.database_repository import SqlAlchemyRepository
from movie.domain.model import User, Movie, Genre, Review, add_review
from movie.adapters.repository import RepositoryException


def test_repository_can_add_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('Dave', '123456789')
    repo.add_user(user)

    repo.add_user(User('Martin', '123456789'))
    user2 = repo.get_user('Dave')
    assert user2 == user and user2 is user


def test_repository_can_retrieve_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_movie_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_movies = repo.get_number_of_movies()

    # Check that the query returned 1000 Movie.
    assert number_of_movies == 1000


def test_repository_can_add_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_movies = repo.get_number_of_movies()

    new_movie_id = number_of_movies + 1

    movie = Movie('Parasite', 2019, new_movie_id)
    repo.add_movie(movie)

    assert repo.get_movie(new_movie_id) == movie


def test_repository_can_retrieve_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(1)

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


def test_repository_does_not_retrieve_a_non_existent_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(1001)
    assert movie is None


def test_repository_can_retrieve_movies_by_year(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_release_year(2016)

    # Check that the query returned 297 Movies.
    assert len(movies) == 297


def test_repository_does_not_retrieve_an_article_when_there_are_no_articles_for_a_given_date(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_release_year(2017)
    assert len(movies) == 0


def test_repository_can_retrieve_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genres = repo.get_genres()

    assert len(genres) == 10

    genre_one = [genre for genre in genres if genre.genre_name == 'Action'][0]
    genre_two = [genre for genre in genres if genre.genre_name == 'Adventure'][0]
    genre_three = [genre for genre in genres if genre.genre_name == 'Sci-Fi'][0]
    genre_four = [genre for genre in genres if genre.genre_name == 'Mystery'][0]

    assert genre_one.number_of_genre_movies == 53
    assert genre_two.number_of_genre_movies == 2
    assert genre_three.number_of_genre_movies == 64
    assert genre_four.number_of_genre_movies == 1


def test_repository_can_get_first_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_first_movie()
    assert movie.title == 'Guardians of the Galaxy'


def test_repository_can_get_last_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_last_movie()
    assert movie.title == 'Nine Lives'


def test_repository_can_get_movies_by_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_id([2, 3, 4])

    assert len(movies) == 3
    assert movies[0].title == 'Prometheus'
    assert movies[1].title == "Split"
    assert movies[2].title == 'Sing'


def test_repository_does_not_retrieve_movie_for_non_existent_id(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_id([2, 209])

    assert len(movies) == 1
    assert movies[0].title == 'Prometheus'


def test_repository_returns_an_empty_list_for_non_existent_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_id([0, 1001])

    assert len(movies) == 0


def test_repository_returns_movie_ids_for_existing_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie_ids = repo.get_movie_ids_by_genre('Action')

    assert 991 in movie_ids
    assert 949 in movie_ids


def test_repository_returns_an_empty_list_for_non_existent_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genre_ids = repo.get_movie_ids_by_genre('United States')

    assert len(genre_ids) == 0


def test_repository_can_add_a_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genre = Genre('WOW')
    repo.add_genre(genre)

    assert genre in repo.get_genres()


def test_repository_can_add_a_review(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('thorke', '902fjsdf')
    movie = repo.get_movie(2)
    review = add_review("Highly recommended!", user, movie, 0)

    repo.add_review(review)

    assert review in repo.get_reviews()


def test_repository_does_not_add_a_comment_without_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(2)
    review = Review(movie, 'LOL', None, None)

    with pytest.raises(RepositoryException):
        repo.add_review(review)


def test_repository_can_retrieve_reviews(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    assert len(repo.get_reviews()) == 2


def make_movie(new_movie_release_year):
    movie = Movie('The Promised Neverland', new_movie_release_year)
    return movie


def test_can_retrieve_a_movie_and_add_a_review_to_it(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # Fetch Movie and User.
    movie = repo.get_movie(5)
    author = repo.get_user('thorke')

    # Create a new Review, connecting it to the Movie and User.
    review = add_review('First death in Australia', author, movie)

    movie_fetched = repo.get_movie(5)
    author_fetched = repo.get_user('thorke')

    assert review in movie_fetched.reviews
    assert review in author_fetched.reviews
