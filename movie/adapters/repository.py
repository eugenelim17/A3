import abc
from typing import List
from datetime import date

from movie.domain.model import User, Director, Genre, Actor, Movie, Review, WatchList


repo_instance = None


class RepositoryException(Exception):

    def __init__(self, message=None):
        pass


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_genre(self, genre: Genre):
        """ Adds a genre to the repository. """

    @abc.abstractmethod
    def get_genres(self):
        """ Returns the genres stored in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def add_user(self, user: User):
        """" Adds a User to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, username) -> User:
        """ Returns the User named username from the repository.

        If there is no User with the given username, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_movie(self, movie: Movie):
        """ Adds a Movie to the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movie(self, id: int) -> Movie:
        """ Returns Movie with this id from the repository.

        If there is no Movie with the given id, this method returns None.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movies_by_genre(self, target_genre: Genre) -> List[Movie]:
        """ Returns a list of Movies that have a particular genre.

        If there are no Movies with the given genre, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movie_ids_by_genre(self, genre_name: str) -> List[int]:
        """ Returns a list of Movie IDs that have a particular genre.

        If there are no Movies with the given genre, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movie_ids_by_actor(self, actor_name: str) -> List[int]:
        """ Returns a list of Movies that stars a particular actor.

        If there are no Movies with the given actor, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_actors(self):
        """ Returns the actors stored in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movie_ids_for_title(self, title: str):
        """ Returns a list of ids representing Movie with a title.

        If there are no Movie with this title, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movies_by_release_year(self, release_year: int) -> List[Movie]:
        """ Returns a list of Movies that were released in a given year.

        If there are no Movies in the given year, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_number_of_movies(self):
        """ Returns the number of Movies in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_first_movie(self) -> Movie:
        """ Returns the first Movie from the repository.

        Returns None if the repository is empty.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_last_movie(self) -> Movie:
        """ Returns the last Movie from the repository.

        Returns None if the repository is empty.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movies_by_id(self, id_list):
        """ Returns a list of Movies, whose ids match those in id_list, from the repository.

        If there are no matches, this method returns an empty list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_movies(self):
        raise NotImplementedError

    @abc.abstractmethod
    def add_review(self, review: Review):
        """ Adds a Review to the repository.

        If the Review doesn't have bidirectional links with an Movie and a User, this method raises a
        RepositoryException and doesn't update the repository.
        """
        if review.user is None or review not in review.user.reviews:
            raise RepositoryException('Review not correctly attached to a User')
        if review.movie is None or review not in review.movie.reviews:
            raise RepositoryException('Review not correctly attached to a Movie')

    @abc.abstractmethod
    def get_reviews(self):
        """ Returns the Reviews stored in the repository. """
        raise NotImplementedError

    @abc.abstractmethod
    def get_id_of_previous_movie(self, movie: Movie):
        """ Returns the id of an Movie that immediately precedes movie.

        If movie is the first Movie in the repository, this method returns None because there are no previous Movies.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_id_of_next_movie(self, movie: Movie):
        """ Returns the date of an Movie that immediately follows movie.

        If movie is the last Movie in the repository, this method returns None because there are no next Movie.
        """
        raise NotImplementedError












