from typing import Optional, Union, Tuple
from threading import Lock


class Song:
    """
    Represents a song with a title, artist, url, webpage url, and duration
    """

    def __init__(
        self,
        title: str,
        artist: Optional[str],
        url: str,
        webpage_url: str,
        duration: Optional[Union[int, str]],
    ) -> "Song":
        self._title: str = title
        self._artist: Optional[str] = artist
        self._url: str = url
        self._webpage_url: str = webpage_url
        self._duration: Optional[int] = (
            duration if isinstance(duration, int) or duration is None else int(duration)
        )

        self._edit_lock: Lock = Lock()

    def __str__(self) -> str:
        return f"Song(title: {self.title}; artist: {self.artist}"

    def __repr__(self) -> str:
        return f"Song(title: {self.title}; artist: {self.artist}"

    def __eq__(self, other) -> bool:
        if isinstance(other, Song):
            return self.url == other.url
        return False

    @property
    def title(self) -> str:
        """
        Get the title of the song
        """
        with self._edit_lock:
            return self._title

    @property.setter
    def title(self, title: str):
        """
        Set the title of the song
        """
        with self._edit_lock:
            if not isinstance(title, str):
                raise TypeError("Title must be a string")
            self._title = title

    @property
    def artist(self) -> Optional[str]:
        """
        Get the artist of the song
        """
        with self._edit_lock:
            return self._artist

    @property.setter
    def artist(self, artist: str):
        """
        Set the artist of the song
        """
        with self._edit_lock:
            if not isinstance(artist, str):
                raise TypeError("Artist must be a string")
            self._artist = artist

    @property
    def url(self) -> str:
        """
        Get the url of the song
        """
        with self._edit_lock:
            return self._url

    @property.setter
    def url(self, url: str):
        """
        Set the url of the song
        """
        with self._edit_lock:
            if not isinstance(url, str):
                raise TypeError("URL must be a string")
            self._url = url

    @property
    def webpage_url(self) -> str:
        """
        Get the webpage url of the song
        """
        with self._edit_lock:
            return self._webpage_url

    @property.setter
    def webpage_url(self, webpage_url: str):
        """
        Set the webpage url of the song
        """
        with self._edit_lock:
            if not isinstance(webpage_url, str):
                raise TypeError("Webpage URL must be a string")
            self._webpage_url = webpage_url

    @property
    def duration(self) -> Optional[int]:
        """
        Get the duration of the song
        """
        with self._edit_lock:
            return self._duration

    @property.setter
    def duration(self, duration: Union[int, str]):
        """
        Set the duration of the song
        """
        with self._edit_lock:
            if not isinstance(duration, (int, str)):
                raise TypeError("Duration must be an integer or string")
            if isinstance(duration, str):
                duration = int(duration)
            self._duration = duration

    def get_all_data(self) -> Tuple[str, str, Optional[str], Optional[int], str]:
        """
        Get all data of the song
        url, title, artist, duration, webpage_url
        """
        with self._edit_lock:
            return self.url, self.title, self.artist, self.duration, self.webpage_url
