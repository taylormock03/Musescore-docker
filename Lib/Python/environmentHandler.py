import os
import shutil
import sqlite3

def getImportDirectory():
    with open("globalSettings",'r') as file:
        for x in file.readlines():
            if "importDirectory" in x:
                importDirectory= x.split("=")[1]
                importDirectory = importDirectory.strip()
    return importDirectory


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
    return os.listdir(importDirectory)
            


def importSong(form):
    fileName= form.importFile.data
    songID= form.song.data

    conn = sqlite3.connect('Lib\sql\musicSQL.db')
    conn.execute('UPDATE Songs SET filePath= ? WHERE SongID = ?',
                        (fileName, songID ,))
    conn.commit()
    conn.close()

    fileOrigin = getImportDirectory() + "/" + fileName
    shutil.move(fileOrigin, "Songs/" + fileName)


    return