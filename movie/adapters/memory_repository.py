import csv
import os

from datetime import date, datetime
from typing import List

from bisect import bisect, bisect_left, insort_left

from werkzeug.security import generate_password_hash

from movie.adapters.repository import AbstractRepository, RepositoryException
from movie.domain.model import Movie, Director, User, Genre, Actor, WatchList, Review, add_review, make_genre_association


class MemoryRepository(AbstractRepository):
    # Movies ordered by Title, not id. id is assumed unique.

    def __init__(self):
        self._movies = list()
        self._movies_title = list()
        self._movies_index = dict()
        self._actors = list()
        self._users = list()
        self._genres = list()
        self._reviews = list()
        self._directors = list()

    def add_genre(self, genre: Genre):
        super().add_genre(genre)
        self._genres.append(genre)

    def get_genres(self):
        return self._genres

    def add_review(self, review: Review):
        super().add_review(review)
        self._reviews.append(review)

    def get_reviews(self):
        return self._reviews

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.username == username), None)

    def add_actor(self, actor: Actor):
        self._actors.append(actor)

    def get_actor(self, actor_full_name):
        return next((actor for actor in self._actors if actor.actor_full_name == actor_full_name), None)

    def get_actors(self):
        return self._actors

    def add_director(self, director: Director):
        self._directors.append(director)

    def get_director(self, director_full_name):
        return next((director for director in self._directors if director.director_full_name == director_full_name),
                    None)

    def add_movie(self, movie: Movie):
        movie.id = len(self._movies) + 1
        self._movies.append(movie)
        self._movies_title.append(movie)

    def get_movie(self, id: int) -> Movie:
        movie = None

        try:
            movie = self._movies[id - 1]
        except KeyError:
            pass  # Ignore exception and return None.
        except IndexError:
            pass  # Ignore exception and return None.

        return movie

    def get_movies_by_title(self, title: str) -> List[Movie]:
        matching_movies = list()

        try:
            for movie in self._movies:
                if movie.title == title:
                    matching_movies.append(movie)
        except ValueError:
            # No movies for specified title. Simply return an empty list.
            pass
        return matching_movies

    def add_movie_index(self, movie: Movie):
        self._movies_index[movie.id] = movie

    def get_movie_ids_for_title(self, title: str):
        # Linear search, to find the first occurrence of a movie with the wanted title.
        movie = next((movie for movie in self._movies if movie.title == title), None)

        # Retrieve the ids of movies associated with the title.
        if movie is not None:
            movie_ids = [movie.id for movie in movie.title]
        else:
            movie_ids = list()

        return movie_ids

    def get_movie_ids_by_genre(self, genre_name: str):
        # Linear search, to find the first occurrence of the wanted genre.
        genre = next((genre for genre in self._genres if genre.genre_name == genre_name), None)

        # Retrieve the ids of movies with the Genre
        if genre is not None:
            movie_ids = [movie.id for movie in self._movies if genre in movie.genres]
        else:
            # No movies with this particular genre, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_movie_ids_by_actor(self, actor_name: str):
        # Linear search, to find the first occurrence of the wanted actor
        actor = next((actor for actor in self._actors if actor.actor_full_name == actor_name), None)

        # Retrieve the ids of movies starring the actor.
        if actor is not None:
            movie_ids = [movie.id for movie in self._movies if actor in movie.actors]
        else:
            # No movie starring this actor, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_movies_by_genre(self, target_genre: Genre) -> List[Movie]:
        # Linear search, to find the first occurrence of the wanted genre.
        genre = next((genre for genre in self._genres if genre.genre_name == target_genre), None)

        # Retrieve the ids of movies with the Genre
        if genre is not None:
            movies = [movie for movie in genre.genre_movies]
        else:
            # No movies with this particular genre, so return an empty list.
            movies = list()

        return movies

    def get_movies_by_release_year(self, target_year: int) -> List[Movie]:
        matching_movies = list()

        for movie in self._movies:
            if movie.release_year == target_year:
                matching_movies.append(movie)
            else:
                continue
        return matching_movies

    def get_number_of_movies(self):
        return len(self._movies)

    def get_first_movie(self):

        return self._movies[0]

    def get_last_movie(self):
        return self._movies[-1]

    def get_movies_by_id(self, id_list):
        # Strip out any ids in id_list that don't represent Movie ids in the repository.
        existing_ids = [id for id in id_list if id in self._movies_index.keys()]

        # Fetch the Movies.
        movies = [self._movies_index[id] for id in existing_ids]
        return movies

    # Helper method to return movie index.
    def movie_index(self, movie: Movie):
        index = bisect_left(self._movies, movie)
        if index != len(self._movies) and self._movies[index].release_year == movie.release_year:
            return index
        raise ValueError

    def get_id_of_previous_movie(self, movie: Movie):
        previous_id = None

        try:
            index = self.movie_index(movie)
            for stored_movie in reversed(self._movies[0:index]):
                if stored_movie.id < movie.id:
                    previous_id = stored_movie.id
                    break
        except ValueError:
            # No earlier movies, so return None.
            pass

        return previous_id

    def get_id_of_next_movie(self, movie: Movie):
        next_id = None

        try:
            index = self.movie_index(movie)
            for stored_movie in self._movies[index + 1:len(self._movies)]:
                if stored_movie.id > movie.id:
                    next_id = stored_movie.id
                    break
        except ValueError:
            # No subsequent movies, so return None.
            pass

        return next_id

    @property
    def movies_index(self):
        return self._movies_index

    @property
    def get_movies(self):
        return self._movies


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_movies_and_ids(data_path: str, repo: MemoryRepository):
    ids = dict()
    for row in read_csv_file(os.path.join(data_path, 'moviefile.csv')):
        movie = Movie(row[1], int(row[6]))
        movie.id = int(row[0])
        movie.description = row[3]
        movie.runtime_minutes = int(row[7])

        director = Director(row[4])
        repo.add_director(director)
        movie.director = director

        parsed_genres = row[2].split(',')
        for genre_string in parsed_genres:
            genre = Genre(genre_string)
            movie.add_genre(genre)
            repo.add_genre(genre)

            parsed_actors = row[5].split(',')
            for actor_string in parsed_actors:
                actor = Actor(actor_string)
                repo.add_actor(actor)
                movie.add_actor(actor)

        # Add the Movie to the repository.
        repo.add_movie(movie)
        repo.add_movie_index(movie)


def load_users_and_ids(data_path: str, repo: MemoryRepository):
    users = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'users.csv')):
        user = User(
            username=data_row[1],
            password=generate_password_hash(data_row[2])
        )
        repo.add_user(user)
        users[data_row[0]] = user
    return users


def load_reviews(data_path: str, repo: MemoryRepository, users):
    for data_row in read_csv_file(os.path.join(data_path, 'reviews.csv')):
        review = add_review(
            review_text=data_row[3],
            user=users[data_row[1]],
            movie=repo.get_movie(int(data_row[2]))
        )
        repo.add_review(review)


def populate(data_path: str, repo: MemoryRepository):
    # Load movies, users and reviews into the repository.
    load_movies_and_ids(data_path, repo)
    users = load_users_and_ids(data_path, repo)
    load_reviews(data_path, repo, users)
