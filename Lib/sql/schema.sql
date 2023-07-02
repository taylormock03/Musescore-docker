CREATE TABLE IF NOT EXISTS Users  (
            UserId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, 
            password TEXT NOT NULL, 
            userName TEXT UNIQUE NOT NULL, 
            oauth TEXT, 
            playlistID TEXT);
        
        CREATE TABLE IF NOT EXISTS Songs (
            SongID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, 
            Name TEXT NOT NULL, 
            Artist TEXT, 
            MuseScoreLink TEXT, 
            YoutubeLink TEXT, 
            Thumbnail TEXT, 
            filePath TEXT);

        CREATE TABLE IF NOT EXISTS Catalog (
            UserID TEXT NOT NULL, 
            SongID TEXT NOT NULL, 
            FOREIGN KEY (UserID) References Users (UserID),
            FOREIGN KEY (SongID) References Songs (SongID)
            PRIMARY KEY (UserID, SongID));