import pytest

import datetime

from sqlalchemy.exc import IntegrityError

from movie.domain.model import User, Movie, Review, Genre, add_review, make_genre_association

movie_year = 2016


def insert_user(empty_session, values=None):
    new_name = "Andrew"
    new_password = "1234"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                          {'username': new_name, 'password': new_password})
    row = empty_session.execute('SELECT id from users where username = :username',
                                {'username': new_name}).fetchone()

    return row[0]


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                              {'username': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT username, id from users'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_movie(empty_session):
    empty_session.execute(
        'INSERT INTO movies (title, genres, description, director, actors, release_year) VALUES '
        '("Parasite", "Thriller", "Korean movie", "Jun", "Kitae", :release_year)',
        {'release_year': movie_year}
    )
    row = empty_session.execute('SELECT id from movies').fetchone()
    return row[0]


def insert_genres(empty_session):
    empty_session.execute(
        'INSERT INTO genres (genre_name) VALUES ("Scary"), ("Very Scary"), ("Thriller")'
    )
    rows = list(empty_session.execute('SELECT id from genres'))

    keys = tuple(row[0] for row in rows)
    return keys


def insert_movie_genre_associations(empty_session, movie_key, genre_keys):
    stmt = 'INSERT INTO movie_genres (movie_id, genre_id) VALUES (:movie_id, :genre_id)'
    for genre_key in genre_keys:
        empty_session.execute(stmt, {'movie_id': movie_key, 'genre_id': genre_key})


def insert_reviewed_movie(empty_session):
    movie_key = insert_movie(empty_session)
    user_key = insert_user(empty_session)

    timestamp_1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp_2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    empty_session.execute(
        'INSERT INTO reviews (user_id, movie_id, review, timestamp) VALUES '
        '(:user_id, :movie_id, "Review 1", :timestamp_1),'
        '(:user_id, :movie_id, "Review 2", :timestamp_2)',
        {'user_id': user_key, 'movie_id': movie_key, 'timestamp_1': timestamp_1, 'timestamp_2': timestamp_2}
    )

    row = empty_session.execute('SELECT id from movies').fetchone()
    return row[0]


def make_movie():
    movie = Movie('Moana', movie_year)
    return movie


def make_user():
    user = User("Andrew", "aaa111")
    return user


def make_genre():
    genre = Genre("Newest")
    return genre


def test_loading_of_users(empty_session):
    users = list()
    users.append(("andrew", "1234"))
    users.append(("cindy", "1111"))
    insert_users(empty_session, users)
    expected = [
        User("Andrew", "1234"),
        User("Cindy", "1111")
    ]
    assert empty_session.query(User).all() == expected


def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT username, password FROM users'))
    assert rows == [("andrew", "aaa111")]


def test_saving_of_users_with_common_username(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("Andrew", "111")
        empty_session.add(user)
        empty_session.commit()


def test_loading_of_movie(empty_session):
    insert_movie(empty_session)
    q = empty_session.query(Movie).filter(Movie.title == 'Parasite')
    assert empty_session.query(q.exists())


def test_loading_of_genred_movie(empty_session):
    movie_key = insert_movie(empty_session)
    genre_keys = insert_genres(empty_session)
    insert_movie_genre_associations(empty_session, movie_key, genre_keys)

    movie = empty_session.query(Movie).get(movie_key)
    genre = Genre('Thriller')
    assert movie.has_genre('Thriller')


def test_loading_of_reviewed_movie(empty_session):
    insert_reviewed_movie(empty_session)

    rows = empty_session.query(Movie).all()
    movie = rows[0]

    assert len(movie.reviews) == 2

    for review in movie.reviews:
        assert review._movie is movie


def test_saving_of_review(empty_session):
    movie_key = insert_movie(empty_session)
    user_key = insert_user(empty_session, ("Andrew", "1234"))

    rows = empty_session.query(Movie).all()
    movie = rows[0]
    users = empty_session.query(User).all()
    user = None
    for u in users:
        if u.username == 'Andrew':
            user = u
            break
    # Create a new Review that is bidirectionally linked with the User and Movie.
    review_text = "Some review text."
    review = add_review(review_text, user, movie)

    # Note: if the bidirectional links between the new review and the User and
    # Movie objects hadn't been established in memory, they would exist following
    # committing the addition of the review to the database.
    empty_session.add(review)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_id, movie_id, review FROM reviews'))

    assert rows == [(user_key, movie_key, review_text)]


def test_saving_of_movie(empty_session):
    movie = make_movie()
    empty_session.add(movie)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT date, title, first_para, hyperlink, image_hyperlink FROM articles'))
    release_year = movie_year
    assert rows == [('Guardians', release_year)]


def test_saving_genred_movie(empty_session):
    movie = make_movie()
    genre = make_genre()

    # Establish the bidirectional relationship between the movie and the Genre.
    make_genre_association(movie, genre)

    # Persist the Movie (and Genre).
    # Note: it doesn't matter whether we add the Genre or the Movie. They are connected
    # bidirectionally, so persisting either one will persist the other.
    empty_session.add(movie)
    empty_session.commit()

    # Test test_saving_of_movie() checks for insertion into the movies table.
    rows = list(empty_session.execute('SELECT id FROM movies'))
    movie_key = rows[0][0]

    # Check that the genres table has a new record.
    rows = list(empty_session.execute('SELECT id, name FROM genres'))
    genre_key = rows[0][0]
    assert rows[0][1] == "News"

    # Check that the movie_genres table has a new record.
    rows = list(empty_session.execute('SELECT movie_id, genre_id from movie_genres'))
    movie_foreign_key = rows[0][0]
    genre_foreign_key = rows[0][1]

    assert movie_key == movie_foreign_key
    assert genre_key == genre_foreign_key


def test_save_reviewed_movie(empty_session):
    # Create Movie User objects.
    movie = make_movie()
    empty_session.add(movie)
    user = make_user()

    # Save the new Movie.
    empty_session.add(movie)
    empty_session.commit()

    # Create a new review that is bidirectionally linked with the User and Movie.
    review_text = "Some review text."
    review = add_review(review_text, user, movie)

    # Test test_saving_of_movie() checks for insertion into the movies table.
    rows = list(empty_session.execute('SELECT id FROM movies'))
    movie_key = rows[0][0]

    # Test test_saving_of_users() checks for insertion into the users table.
    rows = list(empty_session.execute('SELECT id FROM users'))
    user_key = rows[0][0]

    # Check that the reviews table has a new record that links to the movies and users
    # tables.
    rows = list(empty_session.execute('SELECT user_id, movie_id, review FROM reviews'))
    assert rows == [(user_key, movie_key, review_text)]
