import re
import os
from typing import Dict

class MetadataParser:
    @staticmethod
    def _clean_title(title: str) -> str:
        """Clean up title by removing common video/audio keywords"""
        # remove common suffixes
        title = re.sub(r'[_\s]*(official|video|audio|lyrics|remastered|hd|hq|feat\.?.*?)([_\s]*.*)?$', '', title, flags=re.IGNORECASE)
        # replace underscores with spaces and clean up
        title = title.replace('_', ' ')
        title = re.sub(r'\s+', ' ', title).strip()
        return title
    
    @staticmethod
    def parse_filename(filename: str) -> Dict[str, str]:
        name = os.path.splitext(filename)[0]
        name = re.sub(r'_[a-f0-9]{8}$', '', name)
        
        print(f"DEBUG - Cleaned filename: {name}")
        
        #algos for different patterns
        # Pattern 1: Artist_-_Title
        if '_-_' in name:
            parts = name.split('_-_', 1)
            if len(parts) == 2:
                artist = parts[0].strip()
                title = MetadataParser._clean_title(parts[1])
                
                print(f"DEBUG - Pattern 1 - Cleaned title: '{title}'")
                
                return {
                    'artist': artist,
                    'title': title,
                    'album': 'Unknown',
                    'genre': 'Unknown'
                }
        
        # Pattern 2: Artist - Title  
        if ' - ' in name:
            parts = name.split(' - ', 1)
            if len(parts) == 2:
                artist = parts[0].strip()
                title = MetadataParser._clean_title(parts[1])
                
                print(f"DEBUG - Pattern 2 - Cleaned title: '{title}'")
                
                return {
                    'artist': artist,
                    'title': title,
                    'album': 'Unknown',
                    'genre': 'Unknown'
                }
        
        # Pattern 3: Artist_Title (single underscore)
        if '_' in name and name.count('_') == 1:
            parts = name.split('_', 1)
            artist = parts[0].strip()
            title = MetadataParser._clean_title(parts[1])
            
            print(f"DEBUG - Pattern 3 - Cleaned title: '{title}'")
            
            return {
                'artist': artist,
                'title': title,
                'album': 'Unknown',
                'genre': 'Unknown'
            }
        
        # Pattern 4: Multiple underscores
        if '_' in name:
            parts = name.split('_')
            if len(parts) >= 2:
                first_part = parts[0]
                if (len(first_part) <= 15 and  
                    not any(word in first_part.lower() for word in ['official', 'video', 'remastered', 'lyrics', 'audio'])):
                    
                    title_parts = parts[1:]
                    title = MetadataParser._clean_title(' '.join(title_parts))
                    
                    print(f"DEBUG - Pattern 4 - Cleaned title: '{title}'")
                    
                    return {
                        'artist': first_part,
                        'title': title if title else ' '.join(parts[1:]),
                        'album': 'Unknown',
                        'genre': 'Unknown'
                    }
        
        # fallback
        title = MetadataParser._clean_title(name)
        words = title.split()
        
        if len(words) >= 2:
            return {
                'artist': words[0],
                'title': ' '.join(words[1:]),
                'album': 'Unknown',
                'genre': 'Unknown'
            }
        
        return {
            'artist': 'Unknown',
            'title': title if title else name,
            'album': 'Unknown',
            'genre': 'Unknown'
        }
    

