from typing import Optional, List, Deque
from collections import deque
from threading import Lock

from .song import Song


class SongQueue:
    """
    A queue of songs to be played
    """

    def __init__(self, songs: Optional[List[Song]] = None) -> "SongQueue":
        self._songs: Deque[Song] = deque()
        if songs is not None:
            self._songs.append(songs)

        self._edit_lock: Lock = Lock()

    def __str__(self) -> str:
        return f"Song_Queue({self._songs})"

    def __repr__(self) -> str:
        return f"Song_Queue({self._songs})"

    def __len__(self) -> int:
        return len(self._songs)

    def print_discord(self) -> str:
        """
        Prints the queue in a discord friendly format
        """
        with self._edit_lock:
            if self.get_num_songs() == 0:
                return "`No songs in the queue`"
            dis_str = "`"
            total_time = 0
            for i in range(len(self.songs)):
                dis_str += str(i + 1) + ": "
                dis_str += self.songs[i].get_title()
                total_time += self.songs[i].get_duration()
                dis_str += "\n"
            dis_str += f"\nTotal play time of queue: {total_time}"
            dis_str += "`"
            return dis_str

    def get_next_song(self) -> Optional[Song]:
        """
        Gets the next song in the queue
        """
        with self._edit_lock:
            try:
                return self._songs.popleft()
            except IndexError:
                return None

    def add_song(self, song: Song) -> None:
        """
        Adds a song to the queue
        """
        with self._edit_lock:
            self._songs.append(song)

    def get_num_songs(self) -> int:
        """
        Gets the number of songs in the queue
        """
        return len(self._songs)

    def clear(self):
        """
        Clears the queue
        """
        with self._edit_lock:
            self._songs.clear()

    def remove_by_index(self, index: int) -> Optional[Song]:
        """
        Removes a song from the queue by index
        """
        with self._edit_lock:
            try:
                song = self._delete_nth(index)
                return song
            except ValueError:
                return None

    def _delete_nth(self, n: int) -> Song:
        """
        Deletes the nth item in the queue
        """
        if n < 0:
            raise ValueError("n must be >= 0")
        if n > len(self._songs):
            raise ValueError("n must be <= len(self._songs)")
        self._songs.rotate(-n)
        song = self._songs.popleft()
        self._songs.rotate(n)
        return song
