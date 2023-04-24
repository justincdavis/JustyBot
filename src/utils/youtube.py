from typing import Optional, Tuple

import requests
from youtube_dl import YoutubeDL

from ..classes import Song


def search_youtube_video(
    search: str,
) -> Tuple[str, Optional[str], str, str, Optional[str]]:
    """
    Gets the first youtube video from a search, returns a tuple of (title, artist, url, youtube_url, duration)
    If the top url found is a video it will get the video, if it is a playlist it will turn the playlist into a single track
    """
    if not isinstance(search, str):
        raise TypeError(f"Searchs must be a str, not a {type(search)}")
    with YoutubeDL(
        {
            "format": "bestaudio",
            "noplaylist": True,
            "logtostderr": False,
            "quiet": True,
            "no_warnings": True,
            "source_address": "0.0.0.0",
        }
    ) as ydl:
        try:
            requests.get(search)
        except:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)["entries"][0]
        else:
            info = ydl.extract_info(search, download=False)
    return (
        info["title"],
        info["uploader"],
        info["formats"][0]["url"],
        info["webpage_url"],
        info["duration"],
    )


def get_song_youtube(search) -> Song:
    title, artist, url, youtube_url, duration = search_youtube_video(search)
    return Song(title, artist, url, youtube_url, duration)
