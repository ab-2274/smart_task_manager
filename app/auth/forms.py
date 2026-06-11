from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64, message="Username must be between 3 and 64 characters."),
        Regexp(r'^[\w_]+$', message="Username must contain only letters, numbers, and underscores.")
    ])
    
    email = StringField('Email Address', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address."),
        Length(max=120)
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match.")
    ])
    
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email address is already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address.")
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    
    remember = BooleanField('Keep me logged in')
    
    submit = SubmitField('Sign In')


from flask_login import current_user

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64, message="Username must be between 3 and 64 characters."),
        Regexp(r'^[\w_]+$', message="Username must contain only letters, numbers, and underscores.")
    ])
    
    email = StringField('Email Address', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address."),
        Length(max=120)
    ])
    
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message="Please enter your current password to verify identity.")
    ])
    
    new_password = PasswordField('New Password (Optional)', validators=[
        Length(min=0)
    ])
    
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message="New passwords must match.")
    ])
    
    submit = SubmitField('Save Profile Changes')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email address is already registered.')

