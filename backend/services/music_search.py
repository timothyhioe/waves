import requests
import yt_dlp
import os
from typing import List, Dict, Optional
import musicbrainzngs

class MusicSearchService:
    def __init__(self):
        musicbrainzngs.set_useragent("Waves", "0.1", "https://github.com/timothyhioe/waves")

    def search_songs_online(self, query: str, limit: int = 10) -> List[Dict]:
        results = []

        #youtube search
        youtube_results = self._search_youtube(query, limit - len(results))
        results.extend(youtube_results)

        #musicbrainz search
        musicbrainz_results = self._search_musicbrainz(query, limit//2)
        results.extend(musicbrainz_results)
        
        return results


    
    def _search_musicbrainz(self, query: str, limit: int) -> List[Dict]:
        try:
            results = musicbrainzngs.search_recordings(
                query=query, 
                limit=limit
            )

            songs = []
            for recording in results.get('recording-list', []):
                artist = recording.get('artist-credit', [{}])[0].get('artist', {}).get('name', 'Unknown')
                title = recording.get('title', 'Unknown')
                releases = recording.get('release-list', [])
                album = releases[0].get('title', 'Unknown') if releases else 'Unknown'

                songs.append({
                    'id': recording.get('id'),
                    'title': title,
                    'artist': artist,
                    'album': album,
                    'duration': recording.get('length', 0),
                    'source': 'MusicBrainz',
                    'youtube_url': None
                })
            
            return songs
        
        except Exception as e:
            print(f"MusicBrainz search error: {e}")
            return []
        
    def _search_youtube(self, query: str, limit: int) -> List[Dict]:
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(
                    f"ytsearch{limit}:{query}", 
                    download=False
                )

                songs = []
                for entry in search_results.get('entries', []):
                    #parsing title to get artist and song title
                    title_parts = self._parse_youtube_title(entry.get('title', ''))

                    songs.append({
                        'id': entry.get('id'),
                        'title': title_parts.get('title', entry.get('title', 'Unknown')),
                        'artist': title_parts.get('artist', 'Unknown'),
                        'album': 'Unknown',
                        'duration': entry.get('duration', 0),
                        'source': 'youTube',
                        'youtube_url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'thumbnail': entry.get('thumbnail')
                    })

                return songs
            
        except Exception as e:
            print(f"YouTube search error: {e}")
            return []


    def _parse_youtube_title(self, title: str) -> Dict[str, str]:
        separators = [' - ', ' – ', ' — ', ': ', ' ~ ',' by ']

        for sep in separators:
            if sep in title:
                parts = title.split(sep, 1)
                if len(parts) == 2:
                    if sep == ' by ':
                        return {'title': parts[0].strip(), 'artist': parts[1].strip()}
                    else:
                        return {'artist': parts[0].strip(), 'title': parts[1].strip()}

        return {'title': title.strip(), 'artist': 'Unknown'}
    

    def download_from_youtube(self, youtube_url: str, output_dir: str) -> Optional[str]:
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                filename = ydl.prepare_filename(info)
                #replace video file extension with .mp3
                filename = filename.rsplit('.', 1)[0] + '.mp3'
                return filename
                
        except Exception as e:
            print(f"YouTube download error: {e}")
            return None    

