import os
import shutil
import sqlite3
from passlib.hash import pbkdf2_sha256

from Lib.Python.Users import addUser

def getImportDirectory():
    try:
        with open("globalSettings",'r') as file:
            for x in file.readlines():
                if "importDirectory" in x:
                    importDirectory= x.split("=")[1]
                    importDirectory = importDirectory.strip()
        return importDirectory
    except:
        return "NONE"

# Creates an empty data base with a default 'admin' user
def createDB():
    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    with open('Lib/sql/schema.sql') as f:
        conn.executescript(f.read())
    
    conn.commit()
    conn.close()
    addUser("admin", pbkdf2_sha256.hash("admin"), isAdmin=True)


def initialiseSettings():
    settings=["importDirectory=NONE"]

    with open("globalSettings",'w') as file:
        file.writelines(settings)

def updateEnvironment(form):
    settings = []
    for x in form:
        if x.name == 'csrf_token':
            continue

        settings.append(x.name + "=" + x.data+'\n')

    with open("globalSettings",'w') as file:
        file.writelines(settings)

# This returns a list of all files in the imports folder
def getImportSongs():
    importDirectory = getImportDirectory()
    if importDirectory!= "NONE":
        print(os.listdir(importDirectory))
        return os.listdir(importDirectory)
    print("NONE")
        

def importSong(form):
    fileName= form.importFile.data
    songID= form.song.data

    conn = sqlite3.connect('Lib/sql/musicSQL.db')
    conn.execute('UPDATE Songs SET filePath= ? WHERE SongID = ?',
                        (fileName, songID ,))
    conn.commit()
    conn.close()

    fileOrigin = getImportDirectory() + "/" + fileName
    shutil.move(fileOrigin, "Songs/" + fileName)


    return