import os
from mutagen import File
from werkzeug.utils import secure_filename
import hashlib
from typing import Dict, Optional

class AudioFileManager:
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'}

    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder

    def allowed_file(self, filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def save_file(self, file, custom_filename:str = None) -> Optional[str]:
        if not self.allowed_file(file.filename):
            raise ValueError("Unsupported file type")
        
        #generate secure filename
        original_filename = file.filename

        if custom_filename:
            filename = secure_filename(custom_filename)
        else:
            filename = secure_filename(original_filename)

        # create unique filename to avoid collisions
        file_hash = hashlib.md5(file.read()).hexdigest()[:8]
        file.seek(0)  # reset file pointer after reading

        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{file_hash}{ext}"
        file_path = os.path.join(self.upload_folder, unique_filename)

        #save file
        file.save(file_path)

        #extract metadata
        metadata = self.extract_metadata(file_path)
        metadata['file_path'] = file_path
        metadata['original_filename'] = original_filename

        return metadata


    def extract_metadata(self, file_path: str) -> Dict:
        try:
            audio_file = File(file_path)
            if audio_file is None:
                raise ValueError("Unsupported or corrupted audio file")
            
            # Debug: Print all available tags
            print(f"Debug - All tags in file: {dict(audio_file)}")
            print(f"Debug - File info: {audio_file.info}")
            
            #tag values handler
            def get_tag_value(audio_file, tag_key, default='Unknown'):
                tag = audio_file.get(tag_key)
                print(f"Debug - Tag {tag_key}: {tag}")  # Add this debug line back
                if tag is None:
                    return default
                
                #different tag formats handler
                if isinstance(tag, list):
                    if len(tag) > 0:
                        value = tag[0]
                        if hasattr(value, 'text'):
                            return str(value.text[0]) if  value.text else default
                        return str(value)
                    else:
                        return default
                    
                #direct string value
                if hasattr(tag, 'text'):
                    return str(tag.text[0]) if tag.text else default
                return str(tag)

            metadata = {
                'title': get_tag_value(audio_file, 'TIT2') 
                    if get_tag_value(audio_file, 'TIT2') != 'Unknown' 
                    else os.path.splitext(os.path.basename(file_path))[0],
                'artist': get_tag_value(audio_file, 'TPE1'), 
                'album': get_tag_value(audio_file, 'TALB'),
                'genre': get_tag_value(audio_file, 'TCON'),
                'duration': getattr(audio_file.info, 'length', 0),
                'bitrate': getattr(audio_file.info, 'bitrate', 0),
                'format': os.path.splitext(file_path)[1][1:].lower(),
                'file_size': os.path.getsize(file_path)
            }
            print(f"Debug - Extracted metadata: {metadata}")
            return metadata
        
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {
                'title': os.path.splitext(os.path.basename(file_path))[0],
                'artist': 'Unknown',
                'album': 'Unknown',
                'duration': 0,
                'bitrate': 0,
                'format': os.path.splitext(file_path)[1][1:].lower(),
                'file_size': os.path.getsize(file_path)
            }
        
    def delete_file(self, file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            else:
                print("File does not exist")
                return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

