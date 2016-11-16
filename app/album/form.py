# Import Form and RecaptchaField (optional)
from flask_wtf import FlaskForm # , RecaptchaField

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import FileField # BooleanField

# Import Form validators
from wtforms import validators

# Define the login form (WTForms)

class UploadForm(FlaskForm):
    photo = FileField(u'Image File')
