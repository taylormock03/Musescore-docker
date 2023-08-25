import sqlite3

# returns an object with the song's data
def getSong(id):
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    info = conn.execute("select * from Songs where SongID = ?",
                        (id,)).fetchone()
    
    class Song():
        def __init__(self, info) -> None:
            self.id = info[0]
            self.name = info[1]
            self.artist = info[2]
            self.msLink = info[3]
            self.ytLink = info[4]
            self.thumbnail = info[5]
            self.filePath = info[6]

    return Song(info)

def updateSong(form, userID):
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    
    conn.execute("UPDATE Songs Set Name = ?, Artist = ?, MuseScoreLink = ?, YoutubeLink = ? WHERE SongID = ?",
                 (form.name.data,
                  form.artist.data,
                  form.msLink.data if form.msLink.data!="" else None,
                  form.ytLink.data if form.ytLink.data!="" else None,
                  form.id.data,))
    
    conn.execute("UPDATE Catalog Set Tag = ? WHERE SongID = ? AND UserID = ?",
                (form.tag.data if form.tag.data!="" else None,
                form.id.data,
                userID))
    conn.commit()
    conn.close()

# Returns all songs names in the database. Primarily used for manual imports
def getAllSongs():

    query = """
        SELECT SongID, Name from Songs
    """
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    songs = conn.execute(query).fetchall()

    return songs


def getSongID(name):
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    info = conn.execute("select SongID from Songs where Name = ?",
                        (name,)).fetchone()
    try:
        return info[0]
    # if no song is found, return a null values (it will be unsubscriptable so it'll fail the try)
    except:
        return None

def getArtistSongs(artist, userID):
    query = '''
    SELECT  Name, SongID, Artist, Thumbnail from Songs
        where SongID IN 
            (Select SongID from Catalog
            where UserID = ?
            
            )
        AND Artist = ?
'''

    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    songs = conn.execute(query, (userID, artist)).fetchall()

    try: 
        songs[0]
        return songs
    
    except:
        return None

def getTagSongs(tag, userID):
    query = '''
    SELECT  Name, SongID, Artist, Thumbnail from Songs
        where SongID IN 
            (Select SongID from Catalog
            where UserID = ? AND Tag = ?
            
            )
'''

    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    songs = conn.execute(query, (userID, tag)).fetchall()

    try: 
        songs[0]
        return songs
    
    except:
        return None
    
def getSongTag(songID, userID):
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    songs = conn.execute("SELECT Tag from Catalog where UserID = ? AND SongID = ?", (userID, songID)).fetchone()
    
    try:
        return songs[0]
    except:
        return None