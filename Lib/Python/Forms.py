import sqlite3
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField, RadioField, PasswordField)
from wtforms.validators import InputRequired, Length, ValidationError

from passlib.hash import pbkdf2_sha256

def validate_password(bannedLetter="a"):
    message = 'Username or password is incorrect'

    def _sqlGetHash(username):
        conn = sqlite3.connect('Lib\sql\musicSQL.db')
        return conn.execute('SELECT password FROM Users where UserName = ?',
                        (username,)).fetchone()[0]

    def _validatepassword(form, field):
        

        passwordHash = _sqlGetHash(form.username.data)
        if passwordHash == None:
            raise(ValidationError(message))

        if not pbkdf2_sha256.verify(form.password.data, passwordHash):
            raise(ValidationError(message))
        

    return _validatepassword


class LoginForm(FlaskForm):
    username = StringField("User Name", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=3), validate_password()])
