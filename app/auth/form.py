# Import Form and RecaptchaField (optional)
from flask_wtf import FlaskForm # , RecaptchaField

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import TextField, PasswordField, SubmitField # BooleanField

# Import Form validators
from wtforms.validators import Required, EqualTo


# Define the login form (WTForms)

class LoginForm(FlaskForm):
    username    = TextField('Username')
    password = PasswordField('Password', [
                Required(message='Must provide a password. ;-)')])
    submit = SubmitField('Log in')

class SignupForm(FlaskForm):
    username    = TextField('Username')
    password = PasswordField('Password', [
                Required(message='Must provide a password. ;-)')])
    submit = SubmitField('Sign up')
