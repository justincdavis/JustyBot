#Stores title, artist, url and duration for songs acquired through YoutubeDL
class Song:
    #Built in Methods
    def __init__(self, title, artist, url, youtube_url, duration):
        self.title = title
        self.artist = artist
        self.url = url
        self.youtube_url = youtube_url
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
    def get_youtube_url(self):
        return self.youtube_url
    def get_duration(self):
        if(self.duration != None):
            return self.duration
        return 999
    def get_all_data(self):
        return self.get_url(), self.get_title(), self.get_artist(), self.get_duration(), self.get_youtube_url()
    def set_title(self, title):
        self.title = title
    def set_artist(self, artist):
        self.artist = artist
    def set_url(self, url):
        self.url = url
    def set_youtube_url(self, youtube_url):
        self.youtube_url = youtube_url
    def set_duration(self, duration):
        self.duration = duration