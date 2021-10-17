from youtube_dl import YoutubeDL
import requests

#Stores title, artist, url and duration for songs acquired through YoutubeDL
class Song:
    #Built in Methods
    def __init__(self, title, artist, url, duration):
        self.title = title
        self.artist = artist
        self.url = url
        self.duration = duration
    def __repr__(self):
        rep = 'Song(title: ' + self.title + '; artist: ' + self.artist
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
    def get_all_data(self):
        return self.get_url(), self.get_title(), self.get_artist(), self.get_duration()
    def set_title(self, title):
        self.title = title
    def set_artist(self, artist):
        self.artist = artist
    def set_url(self, url):
        self.url = url
    def set_duration(self, duration):
        self.duration = duration

#stores songs in a queue
class Song_Queue:
    #built in methods
    def __init__(self, songs):
        self.songs = songs
        self.count = len(self.songs)
    def __repr__(self):
        str_rep = "{"
        first = True
        for song in self.songs:
            str_rep += song.get_title()
            if(not first):
                str_rep += ', '
            first = False
        return str_rep + '}'
    #get/add operations
    def get_next_song(self):
        if(self.count > 0):
            self.count -= 1
            return self.songs.pop(0)
        return None
    def add_song(self, song):
        self.count += 1
        self.songs.append(song)
    #misc methods
    def get_num_songs(self):
        return self.count

#If the top url found is a video it will get the video, if it is a playlist it will turn the playlist into a single track
def search_youtube_video(search):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':True, 'logtostderr':False, 'quiet':True, 'no_warnings':True, 'source_address': '0.0.0.0'}) as ydl:
        try: requests.get(search)
        except: info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
        else: info = ydl.extract_info(search, download=False)
    return (info['title'], info['uploader'], info['formats'][0]['url'], info['duration'])

def get_song_youtube(search):
    title, artist, url, duration = search_youtube_video(search)
    return build_song(title, artist, url, duration)

def build_song(title, artist, url, duration):
    return Song(title, artist, url, duration)