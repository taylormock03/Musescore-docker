import sqlite3
from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField, RadioField, PasswordField, SelectField)
from wtforms.validators import InputRequired, Length, ValidationError

from passlib.hash import pbkdf2_sha256


def validate_password():
    message = 'Username or password is incorrect'

    def _sqlGetHash(username):
        conn = sqlite3.connect('Lib\sql\musicSQL.db')
        return conn.execute('SELECT password FROM Users where UserName = ?',
                        (username,)).fetchone()

    def _validatepassword(form, field):
        

        passwordHash = _sqlGetHash(form.username.data)
        if passwordHash == None:
            raise(ValidationError(message))

        if not pbkdf2_sha256.verify(form.password.data, passwordHash[0]):
            raise(ValidationError(message))
        

    return _validatepassword

def validate_username():
    def _sqlGetUsername(username):
        conn = sqlite3.connect('Lib\sql\musicSQL.db')
        return conn.execute('SELECT UserName FROM Users where UserName = ?',
                        (username,)).fetchone()
    
    def _sqlGetID(id):
        conn = sqlite3.connect('Lib\sql\musicSQL.db')
        return conn.execute('SELECT UserName FROM Users where UserId = ?',
                        (id,)).fetchone()
    
    def _checkExists(form,field):
        x=_sqlGetUsername(field.data)
        if x == None:
            return

        elif  x[0] == _sqlGetID(form.id.data):
            return
        
        else:
            raise (ValidationError("Username is already being used"))
        
        
    return _checkExists

class LoginForm(FlaskForm):
    username = StringField("User Name", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=3), validate_password()])


class ModifyUser(FlaskForm):
    username = StringField("User Name", validators=[InputRequired(), validate_username()])
    playListID = StringField("Playlist ID", )
    id = StringField()



print(pbkdf2_sha256.hash("test"))