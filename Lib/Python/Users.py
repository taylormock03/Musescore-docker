from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256
import sqlite3

class User(UserMixin):
          
    def __init__(self, identifier) -> None:
        # check if the username or userId is being passed
        self.loadUserInfo(identifier, id=identifier.isnumeric())
        
    def loadUserInfo(self, identifier, id):
        conn = sqlite3.connect('Lib/sql/musicSQL.db')

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
        conn = sqlite3.connect('Lib/sql/musicSQL.db')
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

    conn = sqlite3.connect('Lib/sql/musicSQL.db')
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

    conn = sqlite3.connect('Lib/sql/musicSQL.db')
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
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    songs = conn.execute(query, (userID,)).fetchall()

    return songs

# Gets all the tags that a user has used
def getUserTags(userID):
    query = """
        SELECT DISTINCT Tag FROM Catalog
        WHERE UserID = ?

    """

    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    tags = conn.execute(query, (userID,)).fetchall()

    return tags
 
def getAllUsers():
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    users = conn.execute("SELECT UserId, userName from Users").fetchall()
    conn.close()
    return users

# Create a new user
def addUser(name, password, isAdmin=True):
    conn=sqlite3.connect('Lib/sql/musicSQL.db')
    conn.execute("INSERT INTO Users(userName, password, isAdmin) VALUES (?,?,?)",
                 (name,
                  password,
                  "TRUE" if isAdmin else "FALSE"
                 )
                 )
    conn.commit()
    conn.close()

# Gets all the users who have signed up, but not yet been approved
def getSignups():
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    users = conn.execute("Select userName FROM UserSignup").fetchall()
    conn.close()
    userNames = []

    for name in users:
        userNames.append(name[0])
    return userNames

def acceptSignups(signups):
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    for newUser in signups:
        # Get the user's details
        name, password = conn.execute('Select userName, password FROM UserSignup WHERE userName= ?',
                     (newUser,)).fetchone()
        
        # Migrate them to the active users table
        conn.execute("INSERT INTO Users(userName, password, isAdmin) VALUES (?,?,?)",
                 (name,
                  password,
                "FALSE"
                 ))
        
        # remove them from the signup table
        conn.execute('DELETE FROM UserSignup WHERE userName=?',
                     (name,))
    
    conn.commit()
    conn.close()
        

def declineSignups(signups):
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    for newUser in signups:
        # remove them from the signup table
        conn.execute('DELETE FROM UserSignup WHERE userName=?',
                     (newUser,))
        
    conn.commit()
    conn.close()

def addSignup(form):
    name = form.username.data
    password =pbkdf2_sha256.hash(form.password.data)

    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    conn.execute("INSERT INTO UserSignup(username, password) VALUES (? , ?)",
                 (name, password))
    
    conn.commit()
    conn.close()

def removeUser(id):
    conn = sqlite3.connect('Lib/sql/musicSQL.db')

    conn.execute('DELETE FROM Users WHERE UserId=?',
                     (id,))
    
    conn.commit()
    conn.close()


print(pbkdf2_sha256.hash("test"))