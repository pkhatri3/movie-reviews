from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class SearchForm(FlaskForm):
    search_query = StringField('Search for a movie', validators=[DataRequired(), Length(min=1, max=30)])
    submit = SubmitField('Submit')

class MovieReviewForm(FlaskForm):
    name = StringField('Name/Alias', validators=[DataRequired(), Length(min=1, max=50)])
    text = TextAreaField('Content of Review', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Submit')