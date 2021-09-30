from youtube_dl import YoutubeDL
import requests

class Song:
    #Built in Methods
    def __init__(self, title, artist, url, duration):
        self.title = title
        self.artist = artist
        self.url = url
        self.duration = duration
    def __repr__(self):
        rep = 'Song(title: ' + self.title + ', artist: ' + self.artist
        return rep
    def __eq__(self, other):
        if isinstance(other, Song):
            return (self.url == other.url)
        return False
    #Getters/Setters 
    def get_title(self):
        return self.title
    def get_artist(self):
        if(self.artist != None):
            return self.artist
        return "Undefined"
    def get_url(self):
        return self.url
    def get_duration(self):
        if(self.duration != None):
            return self.duration
        return 999
    def set_title(self, title):
        self.title = title
    def set_artist(self, artist):
        self.artist = artist
    def set_url(self, url):
        self.url = url
    def set_duration(self, duration):
        self.duration = duration

def search_youtube_video(search):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True'}) as ydl:
        try: requests.get(search)
        except: info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
        else: info = ydl.extract_info(search, download=False)
    return (info['title'], info['uploader'], info['formats'][0]['url'], info['duration'])

def build_song(title, artist, url, duration):
    return Song(title, artist, url, duration)

def get_song(search):
    title, artist, url, duration = search_youtube_video(search)
    return Song(title, artist, url, duration)
