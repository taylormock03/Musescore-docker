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

def updateSong(form):
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    
    conn.execute("UPDATE Songs Set Name = ?, Artist = ?, MuseScoreLink = ?, YoutubeLink = ? WHERE SongID = ?",
                 (form.name.data,
                  form.artist.data,
                  form.msLink.data if form.msLink.data!="" else None,
                  form.ytLink.data if form.ytLink.data!="" else None,
                  form.id.data,))
    conn.commit()
    conn.close()

# Returns all songs names in the database. Primarily used for manual imports
def getAllSongs():

    query = """
        SELECT SongID, Name from Songs

    """
    conn = sqlite3.connect('Lib\sql\musicSQL.db')
    songs = conn.execute(query).fetchall()

    return songs