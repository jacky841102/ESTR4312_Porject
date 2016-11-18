# Import Form and RecaptchaField (optional)
from flask_wtf import FlaskForm # , RecaptchaField

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import FileField, StringField, SubmitField

# Import Form validators
from wtforms import validators

# Define the login form (WTForms)

class BlendingForm(FlaskForm):
    foreImg = FileField(u'Foreground image')
    backImg = FileField(u'Background image')
    mask = FileField(u'Mask')
    submit = SubmitField('Upload')

class BlurForm(FlaskForm):
    img = FileField(u'Blur image')
    submit = SubmitField('Upload')

class EdgeForm(FlaskForm):
    img = FileField(u'Find image edge')
    submit = SubmitField('Upload')

class HDRForm(FlaskForm):
    img1 = FileField(u'Image1')
    expo1 = StringField(u'Exposure time 1')
    img2 = FileField(u'Image2')
    expo2 = StringField(u'Exposure time 2')
    img3 = FileField(u'Image3')
    expo3 = StringField(u'Exposure time 3')
    submit = SubmitField('Upload')
