# 3rd-party packages
from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
from dotenv import load_dotenv

# stdlib
import os
from datetime import datetime

# local
from flask_app.forms import SearchForm, MovieReviewForm
from flask_app.model import MovieClient

# don't change the name
app = Flask(__name__)

load_dotenv()

required_settings = ('MONGO_URI', 'OMDB_API_KEY', 'SECRET_KEY')
missing_settings = [setting for setting in required_settings if not os.getenv(setting)]
if missing_settings:
    settings = ', '.join(missing_settings)
    raise RuntimeError(
        f'Missing required environment variables: {settings}. '
        'Copy .env.example to .env and provide values before starting the app.'
    )

app.config.from_mapping(
    MONGO_URI=os.environ['MONGO_URI'],
    SECRET_KEY=os.environ['SECRET_KEY'],
)
OMDB_API_KEY = os.environ['OMDB_API_KEY']

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

# don't change the name
mongo = PyMongo(app)

# don't change the name
movie_client = MovieClient(OMDB_API_KEY)

# --- Do not modify this function ---
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for('query_results', query=form.search_query.data))

    return render_template('index.html', form=form)

@app.route('/search-results/<query>', methods=['GET'])
def query_results(query):
    error_msg = None
    results = []

    try:
        results = movie_client.search(query)
    except ValueError as e:
        error_msg = str(e)

    return render_template('query_results.html', query=query, results=results, error_msg=error_msg)

@app.route('/movies/<movie_id>', methods=['GET', 'POST'])
def movie_detail(movie_id):
    error_msg = None
    movie = None

    try:
        movie = movie_client.retrieve_movie_by_id(movie_id)
    except ValueError as e:
        error_msg = str(e)

    form = MovieReviewForm()

    if form.validate_on_submit():
        review = {
            "imdb_id": movie_id,
            "commenter": form.name.data,
            "content": form.text.data,
            "date": current_time()
        }

        mongo.db.reviews.insert_one(review)
        return redirect(url_for('movie_detail', movie_id=movie_id))

    reviews = list(mongo.db.reviews.find({"imdb_id": movie_id}))
    return render_template('movie_detail.html', movie=movie, form=form, reviews=reviews, error_msg=error_msg)

# Not a view function, used for creating a string for the current time.
def current_time() -> str:
    return datetime.now().strftime('%B %d, %Y at %H:%M:%S')
