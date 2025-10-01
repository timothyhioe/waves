import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

class MusicDBLookup:
    def __init__(self):
        self.base_url = "https://musicbrainz.org/ws/2"
        self.headers = {'User-Agent': 'Waves/0.1 (https://github.com/timothyhioe/waves)'}
        self.last_request = 0
        self.lastfm_api_key = os.getenv('LASTFM_API_KEY')
    
    def search_track(self, artist: str = None, title: str = None, query: str = None):
        """Search using MusicBrainz for metadata + Last.fm for genre"""
        print(f"DEBUG - Hybrid search for: {artist} - {title}")
        
        #get basic metadata from MusicBrainz
        musicbrainz_data = self._search_musicbrainz(artist, title, query)
        print(f"DEBUG - MusicBrainz result: {musicbrainz_data}")
        
        #get genre from Last.fm
        if musicbrainz_data and musicbrainz_data.get('artist') != 'Unknown':
            print(f"DEBUG - Attempting Last.fm lookup...")
            lastfm_genre = self._search_lastfm_genre(
                musicbrainz_data['artist'], 
                musicbrainz_data['title']
            )
            print(f"DEBUG - Last.fm genre result: {lastfm_genre}")
            musicbrainz_data['genre'] = lastfm_genre
        else:
            print(f"DEBUG - Skipping Last.fm - no valid MusicBrainz data")
    
        return musicbrainz_data
    
    def _search_musicbrainz(self, artist: str = None, title: str = None, query: str = None):
        """Get basic metadata from MusicBrainz"""
        self._rate_limit()
        
        if query:
            search_query = query
        elif artist and title:
            search_query = f'artist:"{artist}" AND recording:"{title}"'
        else:
            return None
        
        params = {
            'query': search_query,
            'fmt': 'json',
            'limit': 1,
            'inc': 'artist-credits+releases' 
        }
        
        try:
            response = requests.get(f"{self.base_url}/recording", params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('recordings'):
                    return self._parse_musicbrainz_recording(data['recordings'][0])
        except Exception as e:
            print(f"MusicBrainz error: {e}")
        
        return None
    
    def _parse_musicbrainz_recording(self, recording):
        """Parse MusicBrainz recording (without genre)"""
        artist = 'Unknown'
        if recording.get('artist-credit'):
            artist = recording['artist-credit'][0]['name']
        
        album = 'Unknown'
        if recording.get('releases'):
            for release in recording['releases']:
                title = release['title']
                if title and len(title.encode('ascii', errors='ignore').decode('ascii')) / len(title) > 0.7:
                    album = title
                    break
            else:
                album = recording['releases'][0]['title']
        
        return {
            'title': recording.get('title', 'Unknown'),
            'artist': artist,
            'album': album,
            'genre': 'Unknown' 
        }
    
    def _search_lastfm_genre(self, artist: str, title: str):
        """Get genre from Last.fm with proper genre filtering"""
        print(f"DEBUG - Last.fm API call for: {artist} - {title}")
        
        if not self.lastfm_api_key:
            print("DEBUG - No Last.fm API key found")
            return 'Unknown'
    
        valid_genres = {
            'rock', 'pop', 'indie', 'alternative', 'electronic', 'hip hop', 'rap',
            'jazz', 'classical', 'folk', 'country', 'blues', 'metal', 'punk',
            'reggae', 'soul', 'funk', 'r&b', 'disco', 'house', 'techno',
            'ambient', 'experimental', 'progressive', 'psychedelic', 'garage',
            'grunge', 'indie pop', 'indie rock', 'dream pop', 'shoegaze',
            'post-punk', 'new wave', 'synthpop', 'britpop', 'lo-fi',
            'bedroom pop', 'chillwave', 'downtempo', 'trip hop', 'drum and bass',
            'dubstep', 'trap', 'k-pop', 'j-pop', 'c-pop', 'latin', 'salsa',
            'tango', 'flamenco', 'bluegrass', 'gospel', 'ska', 'emo', 'hardcore',
            'industrial', 'folk rock', 'country rock', 'soft rock', 'classic rock',
            'baroque pop', 'art pop', 'art rock', 'post-rock', 'math rock', 'noise rock',
            'surf rock', 'rock and roll', 'doo-wop', 'motown', 'funk rock', 'psytrance',
            'vaporwave', 'synthwave', 'new age', 'world', 'afrobeat', 'bossa nova',
            'flamenco', 'fado', 'celtic', 'medieval', 'renaissance', 'baroque', 'romantic',
            'modern classical', 'contemporary classical', 'minimalism', 'avant-garde', 'soundtrack', 'musical theater',
            'video game music', 'chiptune', 'anime', 'children\'s music', 'holiday', 'christmas', 'easter', 'halloween',
            'worship', 'chant', 'spiritual', 'new wave of british heavy metal', 'post-hardcore',
            'screamo', 'grindcore', 'mathcore', 'sludge metal', 'doom metal', 'black metal', 'death metal',
            'thrash metal', 'power metal', 'folk metal', 'viking metal', 'symphonic metal',
            'gothic metal', 'nu metal', 'rap metal', 'rap rock', 'funk metal', 'crossover thrash'
        }
        
        url = "http://ws.audioscrobbler.com/2.0/"
        params = {
            'method': 'track.getTopTags',
            'artist': artist,
            'track': title,
            'api_key': self.lastfm_api_key,
            'format': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('toptags') and data['toptags'].get('tag'):
                    tags = data['toptags']['tag']
                    if isinstance(tags, list):
                        print(f"DEBUG - All Last.fm tags: {[tag['name'] for tag in tags[:10]]}") 
                        
                        #find first valid genre
                        for tag in tags:
                            tag_name = tag['name'].lower().strip()
                            
                            if tag_name in valid_genres:
                                print(f"DEBUG - Found valid genre: {tag['name']}")
                                return tag['name'].title()
                            
                            # partial match
                            for genre in valid_genres:
                                if genre in tag_name or tag_name in genre:
                                    print(f"DEBUG - Found partial genre match: {tag['name']}")
                                    return tag['name'].title()
                    
                    print("DEBUG - No valid genres found in Last.fm tags")

        except Exception as e:
            print(f"Last.fm error: {e}")
        
        return 'Unknown'
    
    def _rate_limit(self):
        elapsed = time.time() - self.last_request
        if elapsed < 1:
            time.sleep(1 - elapsed)
        self.last_request = time.time()