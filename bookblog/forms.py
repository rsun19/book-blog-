from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from bookblog.models import User

class CommentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author_name = StringField("Author's name", validators=[DataRequired()])
    rating = StringField('Rating', validators=[DataRequired()])
    rating_int = StringField('Rating (int)', validators=[DataRequired()])
    content_before = TextAreaField('Content Before Spoiler', validators=[DataRequired()])
    content_after = TextAreaField('Content After Spoiler', validators=[DataRequired()])
    image_file = FileField('Insert Picture', validators=[FileAllowed(['jpg', 'png', 'webp'])])
    submit = SubmitField('Post')
    