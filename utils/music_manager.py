import json
import os
from typing import List, Dict
import yt_dlp

class MusicManager:
    """Manages music queue and playback"""
    
    def __init__(self):
        self.queues: Dict[int, List[Dict]] = {}
        self.current_playing: Dict[int, Dict] = {}
        
    def add_to_queue(self, guild_id: int, track: Dict):
        """Add a track to the queue"""
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        self.queues[guild_id].append(track)
    
    def get_queue(self, guild_id: int) -> List[Dict]:
        """Get the queue for a guild"""
        return self.queues.get(guild_id, [])
    
    def skip_track(self, guild_id: int) -> Dict:
        """Skip to next track"""
        if guild_id in self.queues and self.queues[guild_id]:
            return self.queues[guild_id].pop(0)
        return None
    
    def clear_queue(self, guild_id: int):
        """Clear the queue"""
        if guild_id in self.queues:
            self.queues[guild_id] = []
    
    def set_current(self, guild_id: int, track: Dict):
        """Set current playing track"""
        self.current_playing[guild_id] = track
    
    def get_current(self, guild_id: int) -> Dict:
        """Get current playing track"""
        return self.current_playing.get(guild_id)

class PlaylistManager:
    """Manages user playlists"""
    
    def __init__(self, playlists_dir: str = "playlists"):
        self.playlists_dir = playlists_dir
        if not os.path.exists(playlists_dir):
            os.makedirs(playlists_dir)
    
    def create_playlist(self, user_id: int, playlist_name: str) -> bool:
        """Create a new playlist"""
        filepath = self._get_filepath(user_id, playlist_name)
        if os.path.exists(filepath):
            return False
        
        with open(filepath, 'w') as f:
            json.dump([], f)
        return True
    
    def add_to_playlist(self, user_id: int, playlist_name: str, track: Dict) -> bool:
        """Add a track to a playlist"""
        filepath = self._get_filepath(user_id, playlist_name)
        
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, 'r') as f:
            tracks = json.load(f)
        
        tracks.append(track)
        
        with open(filepath, 'w') as f:
            json.dump(tracks, f, indent=2)
        
        return True
    
    def get_playlist(self, user_id: int, playlist_name: str) -> List[Dict]:
        """Get all tracks in a playlist"""
        filepath = self._get_filepath(user_id, playlist_name)
        
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def remove_from_playlist(self, user_id: int, playlist_name: str, track_index: int) -> bool:
        """Remove a track from a playlist"""
        filepath = self._get_filepath(user_id, playlist_name)
        
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, 'r') as f:
            tracks = json.load(f)
        
        if 0 <= track_index < len(tracks):
            tracks.pop(track_index)
            with open(filepath, 'w') as f:
                json.dump(tracks, f, indent=2)
            return True
        
        return False
    
    def delete_playlist(self, user_id: int, playlist_name: str) -> bool:
        """Delete a playlist"""
        filepath = self._get_filepath(user_id, playlist_name)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def list_playlists(self, user_id: int) -> List[str]:
        """List all playlists for a user"""
        user_dir = os.path.join(self.playlists_dir, str(user_id))
        
        if not os.path.exists(user_dir):
            return []
        
        return [f[:-5] for f in os.listdir(user_dir) if f.endswith('.json')]
    
    def _get_filepath(self, user_id: int, playlist_name: str) -> str:
        """Get the filepath for a playlist"""
        user_dir = os.path.join(self.playlists_dir, str(user_id))
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return os.path.join(user_dir, f"{playlist_name}.json")


class YouTubeManager:
    """Manages YouTube search and download"""
    
    YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'default_search': 'ytsearch',
        'quiet': True,
        'no_warnings': True,
    }
    
    @staticmethod
    def search(query: str) -> Dict:
        """Search YouTube and get track info"""
        try:
            with yt_dlp.YoutubeDL(YouTubeManager.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(query, download=False)
                
                if 'entries' in info:
                    video = info['entries'][0]
                else:
                    video = info
                
                return {
                    'title': video.get('title', 'Unknown'),
                    'url': video.get('webpage_url', ''),
                    'duration': video.get('duration', 0),
                    'thumbnail': video.get('thumbnail', ''),
                    'uploader': video.get('uploader', 'Unknown'),
                }
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None
    
    @staticmethod
    def get_audio_url(url: str) -> str:
        """Get the audio stream URL"""
        try:
            with yt_dlp.YoutubeDL(YouTubeManager.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('url', '')
        except Exception as e:
            print(f"Error getting audio URL: {e}")
            return None
