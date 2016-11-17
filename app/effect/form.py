# Import Form and RecaptchaField (optional)
from flask_wtf import FlaskForm # , RecaptchaField

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import FileField, StringField# BooleanField

# Import Form validators
from wtforms import validators

# Define the login form (WTForms)

class BlendingForm(FlaskForm):
    foreImg = FileField(u'Foreground image')
    backImg = FileField(u'Background image')
    mask = FileField(u'Mask')

class BlurForm(FlaskForm):
    img = FileField(u'Blur image')

class EdgeForm(FlaskForm):
    img = FileField(u'Find image edge')
