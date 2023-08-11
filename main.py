from functools import wraps
from os import path

import secrets
import sqlite3

from flask import Flask, request, render_template, redirect, url_for, flash, send_file,abort
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import CSRFProtect
from markupsafe import escape

from Lib.Python.Forms import AdminChooseUser, AdminModifyUser, AdminGlobalRules, LoginForm, ModifyUser, importForm, songForm
from Lib.Python.SongHandler import getSong, updateSong
from Lib.Python.Users import User, getUserSongs, updateUserInfo, updateUserInfoAdmin, verifyUser
from Lib.Python.YtHandler import searchLibrary
from Lib.Python.environmentHandler import importSong, initialiseSettings, updateEnvironment

# Environment Initialisation
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

# Create the database if it doesn't exist
if not path.exists('Lib\sql\musicSQL.db'):
    conn = sqlite3.connect('Lib\sql\musicSQL.db')
    with open('Lib\sql\schema.sql') as f:
        conn.executescript(f.read())
    conn.close()

if not path.exists("globalSettings"):
    initialiseSettings()


# If a user attemps to access a page but isn't logged in,
# this redirects them to the login page

@login_manager.unauthorized_handler
def unauthorised():
    return redirect(app.url_for('login'))

# This is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# END initialisation


@app.route("/test")
def test():
    return render_template("test.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
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
    songs = getUserSongs(current_user.get_id())
    return render_template('dashboard.html', songs = songs)

# This is where a user can modify their own settings
@app.route("/settings", methods=['GET', 'POST'])
@login_required
def userSettings():
    form = ModifyUser(obj=current_user)
    if form.validate_on_submit():
        updateUserInfo(current_user.get_id(), form)
        flash("Successfully updated")

    return render_template("userSettings.html", form=form)

@app.route("/adminSettings")
@login_required
def adminSettings():
    # If someone who is not an admin tries to access this, they will be rejected
    if not current_user.admin:
        abort(403)
    
    return render_template('adminDash.html')


# This allows the admin to select a specific user that will be modified in the following function
@app.route("/adminUserSelect", methods=['GET', 'POST'])
@login_required
def adminUserSelect():
    # If someone who is not an admin tries to access this, they will be rejected
    if not current_user.admin:
        abort(403)

    form = AdminChooseUser()
    if form.validate_on_submit():
        return app.redirect(url_for('adminUserSettings', userID=form.userID.data))

    
    return render_template('adminUserSelect.html', form=form)


# This allows the administrator to modify the settings of a user
@app.route("/adminUser/<userID>", methods=['GET', 'POST'])
@login_required
def adminUserSettings(userID):
    # If someone who is not an admin tries to access this, they will be rejected
    if not current_user.admin:
        abort(403)

    user = load_user(userID)
    form = AdminModifyUser(obj=user)
    if form.validate_on_submit():
        updateUserInfoAdmin(form)
        flash("Success")
    
    return render_template('adminUsers.html', form=form, userID=userID)

@app.route("/adminGlobal", methods=['GET', 'POST'])
@login_required
def adminGlobalSettings():
    # If someone who is not an admin tries to access this, they will be rejected
    if not current_user.admin:
        abort(403)
    
    form = AdminGlobalRules()
    if form.validate_on_submit():
        updateEnvironment(form)
        flash("Success")

    return render_template("adminGlobal.html", form=form)

@app.route("/scanLibrary")
@login_required
def scanLibrary():
    searchLibrary(current_user.id, current_user.playListID)
    return render_template('dashboard.html')

@app.route("/import", methods=['GET', 'POST'])
@login_required
def manualImport():
    form = importForm()
    if form.validate_on_submit():
        flash("Importing...")
        importSong(form)
        flash("Success")

    return render_template('importSongs.html', form = form)


@app.route("/songs/<songID>")
@login_required
def viewSong(songID):
    songID = escape(songID)
    song = getSong(songID)
    return render_template('songView.html', song=song)


@app.route("/download/<filepath>")
@login_required
def downloadSong(filepath):
    filename = escape(filepath)
    filepath = "./Songs/" + escape(filepath)
    return send_file(
        filepath,
        download_name=filename,
        as_attachment=True
    )

@app.route("/edit/<songID>", methods=['GET', 'POST'])
@login_required
def editSong(songID):
    songID = escape(songID)
    song = getSong(songID)
    form = songForm(obj = song)
    if form.validate_on_submit():
        updateSong(form)
        return app.redirect(url_for('viewSong', songID=songID))
    return render_template('songEdit.html', form = form, songID = songID)






if __name__ == '__main__':

    

    app.run(debug=True)
