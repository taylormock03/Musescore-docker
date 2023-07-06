import sqlite3
from flask import flash
from ytmusicapi import YTMusic


def searchLibrary(userId, playlistId):
    Yt = YTMusic()
    playlist = ""
    try:
        playlist = Yt.get_playlist(playlistId, limit=None)
    except:
        flash("The Playlist is Currently Unavailable")
        return

    print(playlist)
    conn = sqlite3.connect('Lib\sql\musicSQL.db')
    for song in playlist['tracks']:
        updateLibrary(userId, song, conn)
    conn.commit()
    conn.close()


def updateLibrary(userId, song, conn):

    # If the video ID is blank, the video no longer exists on youtube
    if song['videoId'] == None:
        return

    # Check if the song has already been stored by the songs table
    songStored = conn.execute("SELECT SongID from Songs WHERE SongID = ?",
                              (song['videoId'],)).fetchone()

    # insert the new song into the Songs table
    if songStored == None:
        try:
            thumbnail = song['thumbnails'][1]['url']
        except:
            try:
                thumbnail = song['thumbnails'][0]['url']
            except:
                thumbnail = None
        conn.execute("INSERT INTO Songs(SongID, Name, Artist, YoutubeLink, Thumbnail) VALUES (?, ?, ?, ?, ?)",
                     (song['videoId'],
                      song['title'],
                      song['artists'][0]["name"],
                      "https://music.youtube.com/watch?v=" + song['videoId'],
                      thumbnail,)
                     )

    # Check if the user already has song in their catalog
    songinCatalog = conn.execute("SELECT SongID from Catalog WHERE SongID = ? AND UserID = ?",
                                 (song['videoId'], userId,)).fetchone()

    if songinCatalog == None:
        conn.execute("INSERT INTO Catalog VALUES (?, ?)",
                     (userId,
                      song['videoId'],
                      ))
    return
