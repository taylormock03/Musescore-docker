from os import path
import secrets
import sqlite3

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_wtf import CSRFProtect


from Lib.Python.Forms import LoginForm

app= Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

# Generate the secret key of the server
if path.exists('secret'):
    with open("secret", 'r') as key:
        app.config['SECRET_KEY'] = key.read()
else:
    with open('secret', 'w') as file:
        file.write(secrets.token_hex(64))
    with open("secret", 'r') as key:
        app.config['SECRET_KEY'] = key.read()


# initialise the login manager
login_manager = LoginManager()
login_manager.init_app(app)

# This is used to reload the user object from 
# the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        print("hello world")

    return render_template("login.html", form=form)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    conn = sqlite3.connect('Lib\sql\musicSQL.db')
    with open('Lib\sql\schema.sql') as f:
        conn.executescript(f.read())
    conn.close()
    app.run(debug=True)

    