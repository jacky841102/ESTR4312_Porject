# Import Form and RecaptchaField (optional)
from flask_wtf import FlaskForm # , RecaptchaField

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import FileField, StringField, SubmitField

# Import Form validators
from wtforms import validators

# Define the login form (WTForms)

class UploadForm(FlaskForm):
    photo = FileField(u'Image File')
    tags = StringField(u'Tags')
    submit = SubmitField('Upload')

class SearchForm(FlaskForm):
    tag = StringField(u'Tag')
    submit = SubmitField('Search')

class DeleteForm(FlaskForm):
    photo_id = StringField(u'Photo id')
