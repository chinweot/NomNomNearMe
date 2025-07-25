from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm): 
    
    # registration fields 
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email Address', validators=[DataRequired(), Length(min=6, max=35), Email()])
    password = PasswordField('New Password', validators=[
        DataRequired(), Length(min=8),
        EqualTo('confirm', message='Passwords must match')])
    
    # idk how this works, i j saw this on stackoverflow, implement later? 
    confirm = PasswordField('Repeat Password')
    phone = StringField('Phone Number', validators=[Length(min=10, max=20)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    
    submit = SubmitField('Login')

    # HAVEN'T IMPLEMENTED YET 
    remember = BooleanField('Remember Me') 