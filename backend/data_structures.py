from collections import deque
from typing import List, Optional
import heapq
import json

class PlaylistManager:
    def create_playlist(structure_type: str, songs: List = None):
        if structure_type == 'list':
            return ListPlaylist(songs or [])
        elif structure_type == 'queue':
            return QueuePlaylist(songs or [])
        elif structure_type == 'stack':
            return StackPlaylist(songs or [])
        elif structure_type == 'priority':
            return PriorityPlaylist(songs or [])
        else:
            raise ValueError("Invalid playlist structure type")
        

class ListPlaylist:
    #vector style playlist
    def __init__(self, songs: List= None):
        self.songs = songs or []

    def add_song(self, song_id: int, position: Optional[int] = None):
        if position is None:
            self.songs.append(song_id)
        else:
            self.songs.insert(position, song_id)

    def remove_song(self, song_id: int):
        if song_id in self.songs:
            self.songs.remove(song_id)

    def get_next_song(self, current_index: int) -> Optional[int]:
        if current_index < len(self.songs) - 1:
            return self.songs[current_index + 1]
        else:
            return None
        
    def get_previous_song(self, current_index: int) -> Optional[int]:
        if current_index > 0:
            return self.songs[current_index - 1]
        else:
            return None
        
    def shuffle(self):
        import random
        random.shuffle(self.songs)

    def to_dict(self):
        return {'type': 'list', 'songs': self.songs}
    

class QueuePlaylist:
    #fifo queue style playlist
    def __init__(self, songs: List = None):
        self.songs = deque(songs or [])

    def add_song(self, song_id: int):
        self.songs.append(song_id)
        
    def get_next_song(self) -> Optional[int]:
        #dequeue operation
        if self.songs:
            return self.songs.popleft()
        else:
            return None
        
    def peek_next(self) -> Optional[int]:
        if self.songs:
            return self.songs[0]
        else:
            return None
        
    def to_dict(self):
        return {'type': 'queue', 'songs': list(self.songs)}
    

class StackPlaylist:
    #lifo stack style playlist
    def __init__(self, songs: List = None):
        self.songs = songs or []

    def add_song(self, song_id: int):
        self.songs.append(song_id)

    def remove_song(self) -> Optional[int]:
        if self.songs:
            return self.songs.pop()
        else:
            return None
        
    def get_next_song(self) -> Optional[int]:
        #pop operation
        if self.songs:
            return self.songs.pop()
        else:
            return None
        
    def peek_next(self) -> Optional[int]:
        if self.songs:
            return self.songs[-1]
        else:
            return None
        
    def to_dict(self):
        return {'type': 'stack', 'songs': self.songs}
    
class PriorityPlaylist:
    def __init__(self, songs: List = None):
        self.songs = songs or []
        if songs:
            for song in songs:
                self.add_song(song, priority = 0)

    def add_song(self, song_id: int, priority: int = 0):
        heapq.heappush(self.songs, (priority, song_id))

    def get_next_song(self) -> Optional[int]:
        if self.songs:
            priority, song_id = heapq.heappop(self.songs)
            return song_id
        else:
            return None

    def to_dict(self):
        return {'type': 'priority', 'songs': [song_id for priority, song_id in self.songs]}