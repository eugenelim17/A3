from sqlalchemy import select, inspect

from movie.adapters.orm import metadata


def test_database_populate_inspect_table_names(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    assert inspector.get_table_names() == ['genres', 'movie_genres', 'movies', 'reviews', 'users']


def test_database_populate_select_all_genres(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_genres_table = inspector.get_table_names()[0]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_genres_table]])
        result = connection.execute(select_statement)
        all_genre_names = []
        for row in result:
            all_genre_names.append(row['genre_name'])

        assert all_genre_names == ['Action', 'Adventure', 'Sci-Fi', 'Mystery', 'Horror', 'Thriller', 'Animation', 'Comedy', 'Family', 'Fantasy', 'Drama', 'Music', 'Biography', 'Romance', 'History', 'Crime', 'Western', 'War', 'Musical', 'Sport']


def test_database_populate_select_all_users(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_users_table = inspector.get_table_names()[4]

    with database_engine.connect() as connection:
        # query for records in table users
        select_statement = select([metadata.tables[name_of_users_table]])
        result = connection.execute(select_statement)

        all_users = []
        for row in result:
            all_users.append(row['username'])

        assert all_users == ['thorke', 'fmercury', 'tobinwonderland']


def test_database_populate_select_all_reviews(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_reviews_table = inspector.get_table_names()[3]
    print(name_of_reviews_table)
    with database_engine.connect() as connection:
        # query for records in table reviews
        select_statement = select([metadata.tables[name_of_reviews_table]])
        result = connection.execute(select_statement)

        all_reviews = []
        for row in result:
            all_reviews.append((row['id'], row['user_id'], row['movie_id'], row['review']))

        assert all_reviews == [(1, 2, 1, 'I love this movie'),
                               (2, 1, 1, 'Master piece!')]


def test_database_populate_select_all_movies(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_movies_table = inspector.get_table_names()[2]

    with database_engine.connect() as connection:
        # query for records in table movies
        select_statement = select([metadata.tables[name_of_movies_table]])
        result = connection.execute(select_statement)

        all_movies = []
        for row in result:
            all_movies.append((row['id'], row['title']))

        nr_movies = len(all_movies)

        assert all_movies[0] == (1, 'Guardians of the Galaxy')
        assert all_movies[nr_movies // 2] == (501, 'Maze Runner: The Scorch Trials')
        assert all_movies[nr_movies - 1] == (1000, 'Nine Lives')
