from youtube_dl import YoutubeDL
import requests
from .song import Song

# stores songs in a queue
class Song_Queue:
    # built in methods
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
    # formatting for printing in discord
    def print_discord(self):
        dis_str = "`"
        for i in range(len(self.songs)):
            dis_str += str(i+1) + ": "
            dis_str += self.songs[i].get_title()
            if i != len(self.songs) - 1:
                dis_str += "\n"
        dis_str += "`"
        return dis_str
    # get/add operations
    def get_next_song(self):
        if(self.count > 0):
            self.count -= 1
            return self.songs.pop(0)
        return None
    def add_song(self, song):
        self.count += 1
        self.songs.append(song)
    # misc methods
    def get_num_songs(self):
        return self.count
    def clear(self):
        self.songs.clear()
    def remove_by_index(self, index):
        if(index < 0 or index >= self.get_num_songs()):
            return None
        return self.songs.pop(index)

#TODO
# IMPLEMENT OTHER SONG SOURCES APART FROM YOUTUBE
# THESE COULD SIMPLY BE EXPANDING OF THE search_SOURCE_song and get_song_SOURCE formats
# Music cog would implement these functions based on commands and default 'mode'

#If the top url found is a video it will get the video, if it is a playlist it will turn the playlist into a single track
def search_youtube_video(search):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':True, 'logtostderr':False, 'quiet':True, 'no_warnings':True, 'source_address': '0.0.0.0'}) as ydl:
        try: requests.get(search)
        except: info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
        else: info = ydl.extract_info(search, download=False)
    return (info['title'], info['uploader'], info['formats'][0]['url'], info['webpage_url'], info['duration'])



def build_song(title, artist, url, youtube_url, duration):
    return Song(title, artist, url, youtube_url, duration)

def get_song_youtube(search):
    title, artist, url, youtube_url, duration = search_youtube_video(search)
    return build_song(title, artist, url, youtube_url, duration)
