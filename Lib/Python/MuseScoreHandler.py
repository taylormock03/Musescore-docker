import multiprocessing
import os
import sqlite3
import threading
import queue
from bs4 import BeautifulSoup as bs4
from pathlib import Path
from musescore_scraper import AsyncMuseScraper
from typing import Optional, List
import asyncio
from functools import partial
import shutil
import urllib.parse
from requests_html import HTMLSession

import hrequests
import os



# This is the musescore function that 
# asynchronously downloads all scores passed to it
def downloadScore(urls):
    # return os.system(f'npx dl-librescore -i {urls} -t pdf -o /app/Songs -v true')
    import subprocess
    result = subprocess.getoutput(f'npx dl-librescore -i {urls} -t pdf -o /app/Songs -v true')
    
    idx1 = result.index('/app/Songs/')
    idx2 = result.index('\n✔')
    res = ''
    for idx in range(idx1 + len('/app/Songs/'), idx2):
        res = res + result[idx]

    return res

# This gets all songs that DON'T currently have a file associated with it
def getMissingSongs():
    conn = sqlite3.connect('/db/musicSQL.db')
    
    return conn.execute('SELECT Name FROM Songs where filePath IS NULL').fetchall()
    # return [[("Howl's Moving Castle")]]


def checkExistingURL(songName):
    conn = sqlite3.connect('/db/musicSQL.db')
    return conn.execute("SELECT MuseScoreLink from Songs where Name = ?",(songName,)).fetchone()

# This searches musescore for a song that has the 
# same name and returns the link
def getSongURL(returnDict, songName, i):

    

    print(songName)

    # This needs to be changed as I believe I'm being rate limited
    searchURL = "https://musescore.com/sheetmusic?instrument=2&instrumentation=114&sort=relevance&text=" + urllib.parse.quote(songName, safe='') + "&type=non-official"

    # This is able to render the JS musescore requires
    with hrequests.render(searchURL) as page:

        if "No results for" in page.html.text:
            return
        
        response = page.html.find_all('a')

        links = []
        for link in response:
            url = list(link.absolute_links)[0]
            if ('user' in url and 'scores' in url):
                        links.append(url)



        if len(links)>0:
            returnDict[i]=[links[0], searchURL, songName]


def moveSongs():
    if not os.path.isdir('./Songs'):
        os.mkdir("./Songs")
    for fname in os.listdir("./"):
        if fname.lower().endswith(".pdf"):
            shutil.move(os.path.join("./", fname), "./Songs")

def DownloadMissing(logger):
    # Create the thread queue and list
    manager = multiprocessing.Manager()

    returnList = manager.dict()
    URLthreads = list()

    # Returns a list of all songs in the database that don't have a file associated with them
    # NOTE: this is for all users, not just one
    songs = getMissingSongs()
    i=-1
    # This is where we get the url of the song
    # It is an asyncrhronous function that looks for the 
    # song on musescore and passes back the url
    logger.info("Getting Musescore Links")
    for x in songs:
        i+=1
        x = x[0]

        # Check if the song has a musescore URL already
        # This will happen if a user manually inputs a link or if the request failed earlier
        existingUrl = checkExistingURL(x)
        if existingUrl[0] !=None:
            returnList[i] = [existingUrl[0], None, x]
            continue
        
        else:
            # This is where we try to get the URL if we have not previously gotten one 
            try:
                newThread = multiprocessing.Process(target=getSongURL, args = (returnList, x, i))
                URLthreads.append(newThread)
                logger.info(f"Got URL for: {x}")

            except Exception as e:
                logger.warning(e)
        

    # This limits the number of processes that are allowed to run at once
    max_processes=5
    i=0
    while i<len(URLthreads)-1:
        for x in range(max_processes):
            try:
                URLthreads[i+x].start()
            except:
                pass
        
        for x in range(max_processes):
            try:
                URLthreads[i+x].join()

            except:
                pass
        i+=max_processes
    

    # Grab all of the urls and turn them into a list that can be read
    print(returnList.items())
    # It also updates the SQL database so that the
    urls = []
    conn = sqlite3.connect('/db/musicSQL.db')
    for x in returnList.items():

            urls.append([x[1][0],x[1][2]])

            # This adds the musescore link to the database.
            # This is done so that in case the connection is later 
            # refused, it can still be used without creating a new connection
            # This saves network resources
            conn.execute("UPDATE Songs SET MuseScoreLink = ? WHERE Name =?",
                     (x[1][0],x[1][2],))
            conn.commit()

    # This is an asynchronous function that 
    # will download multiple songs at once

    i=0

    while i<len(urls):
        
        urlList = urls[i]
        logger.info(f"Downloading song: {urlList[0]}")
        paths = downloadScore(urlList[0])
        name = urlList[1]
        conn.execute("UPDATE Songs SET filePath = ? WHERE Name =?",
                    (paths, name))
        
            
        conn.commit()
        i+=1

        # by default songs are downloaded into the root directory
        # This will move them into the "Songs" folder
        # moveSongs()
    conn.close()

# def DownloadMissing(logger):
    
#     with hrequests.render('https://musescore.com/sheetmusic?instrument=2&instrumentation=114&sort=relevance&text=someone%20like%20you&type=non-official', 'https://musescore.com/sheetmusic?instrument=2&instrumentation=114&sort=relevance&text=shape%20of%20you&type=non-official') as page:
#         logger.info(page.html.absolute_links)
    


if __name__ == '__main__':
    DownloadMissing()
