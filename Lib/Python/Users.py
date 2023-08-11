from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256
import sqlite3

class User(UserMixin):
          
    def __init__(self, identifier) -> None:
        # check if the username or userId is being passed
        self.loadUserInfo(identifier, id=identifier.isnumeric())
        
    def loadUserInfo(self, identifier, id):
        conn = sqlite3.connect('Lib\sql\musicSQL.db')

        # change which field is being searched based on if 'username' is the username or id
        if id:
            data = conn.execute('SELECT * FROM Users where userId = ?',
                        (identifier,)).fetchone()
        else:
            data = conn.execute('SELECT * FROM Users where userName = ?',
                        (identifier,)).fetchone()
        
        try:
            self.id = data[0]
            self.password = data[1]
            self.username = data[2]
            self.oAuth = data[3]
            self.playListID = data[4]
            self.admin = data[5]=="TRUE"
        except: pass
        return        


def verifyUser(username, password):
    def _sqlGetHash(username):
        conn = sqlite3.connect('Lib\sql\musicSQL.db')
        return conn.execute('SELECT password FROM Users where UserName = ?',
                        (username,)).fetchone()

    def _validatepassword(username, password):
        

        passwordHash = _sqlGetHash(username)
        if passwordHash == None:
            return False

        return pbkdf2_sha256.verify(password, passwordHash[0])
            
        
    return _validatepassword(username, password)
    
# This is for regular users who can modify their own data
def updateUserInfo(currentUser, form):

    conn = sqlite3.connect('Lib\sql\musicSQL.db')
    conn.execute('UPDATE Users SET userName= ?, playListID = ? WHERE UserId = ?',
                        (form.username.data, form.playListID.data, currentUser,))
    conn.commit()
    conn.close()

# This is used by administrators who are modifying the accounts of other users  
def updateUserInfoAdmin(form):
    if "$pbkdf2-sha256" in form.password.data:
        passwordHash= form.password.data
    else:
        passwordHash = pbkdf2_sha256.hash(form.password.data)

    if form.admin.data:
        isAdmin="TRUE"
    else:
        isAdmin="FALSE"

    conn = sqlite3.connect('Lib\sql\musicSQL.db')
    conn.execute('UPDATE Users SET userName= ?, playListID = ?, isAdmin=?, password=? WHERE UserId = ?',
                        (form.username.data, form.playListID.data, isAdmin, passwordHash, form.id.data,))
    conn.commit()
    conn.close()


def getUserSongs(userID):

    query = """
        SELECT  Name, SongID, Artist, Thumbnail from Songs
        where SongID IN 
            (Select SongID from Catalog
            where UserID = ?
            
            )
    """
    conn = sqlite3.connect('Lib\sql\musicSQL.db')
    songs = conn.execute(query, (userID,)).fetchall()

    return songs


def getAllUsers():
    conn = sqlite3.connect('Lib\sql\musicSQL.db')
    users = conn.execute("SELECT UserId, userName from Users").fetchall()
    conn.close()
    return users

print(pbkdf2_sha256.hash("test"))