from os import path
import os
import secrets
import sqlite3

from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import CSRFProtect

from Lib.Python.Forms import AdminSettings, LoginForm, ModifyUser
from Lib.Python.Users import User, updateUserInfo, verifyUser
from Lib.Python.YtHandler import searchLibrary

app = Flask(__name__)
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
    # test = User(user_id)
    return User(user_id)

# This removes the session from memory and logs out the user


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(app.url_for('login'))

# If a user attemps to access a page but isn't logged in,
# this redirects them to the login page
# NOTE: this will eventually have to be changed to allow
# for the case where non-admin users try to access admin pages


@login_manager.unauthorized_handler
def unauthorised():
    return redirect(app.url_for('login'))


# This is the function for the login page
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        login_user(User(form.username.data))

        next = request.args.get('next')
        return app.redirect(next or app.url_for('dashboard'))

        # return app.redirect(app.url_for("dashboard"))

    return render_template("login.html", form=form)


# LOGGED IN PAGES

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route("/settings", methods=['GET', 'POST'])
@login_required
def userSettings():
    form = ModifyUser(obj=current_user)
    if form.validate_on_submit():
        updateUserInfo(current_user.get_id(), form)
        flash("Successfully updated")

    return render_template("userSettings.html", form=form)


@app.route("/scanLibrary")
@login_required
def scanLibrary():
    searchLibrary(current_user.id, current_user.playListID)
    return render_template('dashboard.html')


if __name__ == '__main__':

    # Create the database if it doesn't exist
    if not os.path.exists('Lib\sql\musicSQL.db'):
        conn = sqlite3.connect('Lib\sql\musicSQL.db')
        with open('Lib\sql\schema.sql') as f:
            conn.executescript(f.read())
        conn.close()

    app.run(debug=True)
