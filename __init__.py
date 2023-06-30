import sqlite3

from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
   
    return conn


def initialiseSQLServer(conn, tables):
    for x in tables:
        create_table(conn, x)

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


if __name__ == '__main__':
    
    
    conn = create_connection(r"Lib/sql/musicSQL.db")
    tables=[
        """CREATE TABLE IF NOT EXISTS "Users"  (
            "UserId" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, 
            "password" TEXT NOT NULL, 
            "userName" TEXT UNIQUE NOT NULL, 
            "oauth" TEXT, 
            "playlistID" TEXT)""",
        
        """CREATE TABLE IF NOT EXISTS "Songs" (
            "SongID" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, 
            "Name" TEXT NOT NULL, 
            "Artist" TEXT, 
            "MuseScoreLink" TEXT, 
            "YoutubeLink" TEXT, 
            "Thumbnail" TEXT, 
            "filePath" TEXT)""",

        """CREATE TABLE IF NOT EXISTS "Catalog" (
            "UserID" TEXT NOT NULL, 
            "SongID" TEXT NOT NULL, 
            FOREIGN KEY (UserID) References Users (UserID),
            FOREIGN KEY (SongID) References Songs (SongID)
            PRIMARY KEY (UserID, SongID))"""

    ]
    
    initialiseSQLServer(conn,tables)


    conn.close()