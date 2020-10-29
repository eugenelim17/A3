from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

import movie.adapters.repository as repo
import movie.utilities.utilities as utilities
import movie.movies.services as services

home_blueprint = Blueprint(
    'home_bp', __name__)


@home_blueprint.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm(request.form)
    if request.method == 'POST':
        return movies_by_actor(form)
    return render_template('home/home.html', form=form, selected_movies=utilities.get_selected_movies())


@home_blueprint.route('/movies_by_actor', methods=['GET', 'POST'])
def movies_by_actor(form):
    actor_name = form.actor.data

    movies_per_page = 3

    # Read query parameters.
    cursor = request.args.get('cursor')
    movie_to_show_reviews = request.args.get('view_reviews_for')

    if movie_to_show_reviews is None:
        # No view-reviews query parameter, so set to a non-existent movie id.
        movie_to_show_reviews = -1
    else:
        # Convert movie_to_show_reviews from string to int.
        movie_to_show_reviews = int(movie_to_show_reviews)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movie ids for movie with genre_name.
    movie_ids = services.get_movie_ids_by_actor(actor_name, repo.repo_instance)

    # Retrieve the batch of movies to display on the Web page.
    movies = services.get_movies_by_id(movie_ids[cursor:cursor + movies_per_page], repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('home_bp.movies_by_actor', actor=actor_name, cursor=cursor - movies_per_page)
        first_movie_url = url_for('home_bp.movies_by_actor', actor=actor_name)

    if cursor + movies_per_page < len(movie_ids):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('home_bp.movies_by_actor', actor=actor_name, cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movie_ids) / movies_per_page)
        if len(movie_ids) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('home_bp.movies_by_actor', actor=actor_name, cursor=last_cursor)

    # Construct urls for viewing movie reviews and adding reviews.
    for movie in movies:
        movie['view_review_url'] = url_for('home_bp.movies_by_actor', actor=actor_name, cursor=cursor,
                                           view_comments_for=movie['id'])
        movie['add_review_url'] = url_for('home_bp.movies_by_actor', movie=movie['id'])

    # Generate the webpage to display the movies.
    return render_template(
        'movies/movies.html',
        title='Movies',
        movies=movies,
        form=form,
        movies_title='Movies starring actor: ' + actor_name,
        selected_movies=utilities.get_selected_movies(len(movies) * 2),
        handler_url=url_for('home_bp.movies_by_actor'),
        actor_urls=utilities.get_actors_and_urls(),
        genre_urls=utilities.get_genres_and_urls(),
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_reviews_for_movie=movie_to_show_reviews,
    )


class SearchForm(FlaskForm):
    actor = StringField('Actor', [
        DataRequired()])
    submit = SubmitField('Search')
