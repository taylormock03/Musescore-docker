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


# This is the musescore function that 
# asynchronously downloads all scores passed to it
def downloadScore(urls):

    outputs: List[Optional[Path]] = [None] * len(urls)
    def set_output(i: int, task: asyncio.Task) -> None:
        outputs[i] = task.result()

    async def run():
        tasks: List[asyncio.Task] = []

        async with AsyncMuseScraper() as ms:
            for i in range(len(urls)):
                task: asyncio.Task = asyncio.create_task(ms.to_pdf(urls[i]))
                task.add_done_callback(partial(set_output, i))
                tasks.append(task)

            result = await asyncio.gather(*tasks)

        return result


    return asyncio.get_event_loop().run_until_complete(run())

# This gets all songs that DON'T currently have a file associated with it
def getMissingSongs():
    conn = sqlite3.connect('Lib\sql\musicSQL.db')
    
    return conn.execute('SELECT Name FROM Songs where filePath IS NULL').fetchall()
    # return [[("Howl's Moving Castle")]]


# This searches musescore for a song that has the 
# same name and returns the link
def getSongURL(returnDict, songName, i):
    # This needs to be changed as I believe I'm being rate limited
    searchURL = "https://musescore.com/sheetmusic?instrument=2&instrumentation=114&sort=relevance&text=" + urllib.parse.quote(songName, safe='') + "&type=non-official"

    # This is able to render the JS musescore requires
    session = HTMLSession()
    r = session.get(searchURL)
    r.html.render(timeout=30)
    # print(r.html.text)
    if "No results for" in r.html.text:
        return
    
    response = r.html.find('a', first=False)

    r.close()
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

def museScoreMain():
    # Create the thread queue and list
    manager = multiprocessing.Manager()

    returnList = manager.dict()
    URLthreads = list()

    # Returns a list of all songs in the database
    # NOTE: this is for all users, not just one
    songs = getMissingSongs()
    i=0
    for x in songs[10:11]:
        # This is where we get the url of the song
        # It is an asyncrhronous function that looks for the 
        # song on musescore and passes back the url
        x = x[0]
        print(x)
        try:
            newThread = multiprocessing.Process(target=getSongURL, args = (returnList, x, i))
            URLthreads.append(newThread)
            newThread.start()
        except Exception as e:
            print(e)
        i+=1

    for index, thread in enumerate(URLthreads):
        thread.join()
    

    # Grab all of the urls and turn them into a list that can be read
    print(returnList.items())
    # It also updates the SQL database so that the
    urls = []
    for x in returnList.items():
        urls.append(x[1][0])

    # This is an asynchronous function that 
    # will download all the songs at once
    paths = downloadScore(urls)

    conn = sqlite3.connect('Lib\sql\musicSQL.db')
    i = 0
    for x in paths:
        conn.execute("UPDATE Songs SET filePath = ?, MuseScoreLink = ? WHERE Name =?",
                     ("./Songs/" +x.stem+".pdf", returnList[i][0], returnList[i][2]))
        
    conn.commit()
    conn.close()
    

    # by default songs are downloaded into the root directory
    # This will move them into the "Songs" folder
    moveSongs()

if __name__ == '__main__':
    museScoreMain()