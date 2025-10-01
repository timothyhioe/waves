from .metadata_parser import MetadataParser
from .online_lookup import MusicDBLookup
from typing import Dict


class MetadataEnhancer:
    def __init__(self):
        self.parser = MetadataParser()  
        self.lookup_service = MusicDBLookup()

    def _needs_enhancement(self, metadata: Dict) -> bool:
        return (metadata.get('title') == 'Unknown' or 
                metadata.get('artist') == 'Unknown' or
                metadata.get('album') == 'Unknown' or
                metadata.get('genre') == 'Unknown')
    
    def enhance_metadata(self, metadata: Dict, filename: str) -> Dict:
        """Enhance metadata using filename parsing and online lookup"""
        print(f"DEBUG - enhance_metadata called with filename: {filename}")
        print(f"DEBUG - Input metadata: {metadata}")
        
        enhanced = metadata.copy()
        
        needs_enhancement = self._needs_enhancement(metadata)
        print(f"DEBUG - Needs enhancement: {needs_enhancement}")
        
        if needs_enhancement:
            parsed = self.parser.parse_filename(filename)
            print(f"DEBUG - Parsed filename: {parsed}")
            
            for key, value in parsed.items():
                if enhanced.get(key) == 'Unknown' and value != 'Unknown':
                    print(f"DEBUG - Updating {key}: {enhanced.get(key)} -> {value}")
                    enhanced[key] = value
                elif key == 'title' and value != 'Unknown' and enhanced.get(key) != 'Unknown':
                    print(f"DEBUG - Updating title from parsed: {enhanced.get(key)} -> {value}")
                    enhanced[key] = value
            
            print(f"DEBUG - After filename parsing: {enhanced}")
            
            # online lookup if we have artist + title
            if (enhanced.get('artist') != 'Unknown' and 
                enhanced.get('title') != 'Unknown'):
                
                print(f"DEBUG - Attempting online lookup for: {enhanced['artist']} - {enhanced['title']}")
                
                
                # Try online lookup with original artist/title
                online_result = self.lookup_service.search_track(
                    artist=enhanced.get('artist'),
                    title=enhanced.get('title')
                )
                
                print(f"DEBUG - Online lookup result: {online_result}")   

                # try swapping artist/title if no result
                if (not online_result and 
                    enhanced.get('artist') != 'Unknown' and 
                    enhanced.get('title') != 'Unknown'):
                    
                    print(f"DEBUG - Original lookup failed, trying reversed...")
                    
                    reversed_result = self.lookup_service.search_track(
                        artist=enhanced.get('title'),   
                        title=enhanced.get('artist')    
                    )
                    
                    if reversed_result:
                        print(f"DEBUG - Reverse lookup succeeded! Using swapped metadata")
                        online_result = reversed_result
                        enhanced['artist'] = reversed_result['artist']
                        enhanced['title'] = reversed_result['title']
                
                # apply online result if found
                if online_result:
                    # Prefer online data over parsed data (more accurate)
                    for key, value in online_result.items():
                        if value != 'Unknown':
                            print(f"DEBUG - Online update {key}: {enhanced.get(key)} -> {value}")
                            enhanced[key] = value
            else:
                print(f"DEBUG - Skipping online lookup - missing artist or title")
        
        print(f"DEBUG - Final enhanced metadata: {enhanced}")
        return enhanced