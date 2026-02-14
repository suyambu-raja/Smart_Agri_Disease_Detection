import os
import sys
import django
import hashlib
from pathlib import Path

# Setup Django environment manually
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_agriculture.settings')
django.setup()

from django.conf import settings
from openai import OpenAI

def test_tts():
    text = "Testing TTS integration"
    lang = "en"
    
    file_hash = hashlib.md5(f"{text}-{lang}".encode('utf-8')).hexdigest()
    file_name = f"{file_hash}.mp3"
    
    tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
    os.makedirs(tts_dir, exist_ok=True)
    file_path = os.path.join(tts_dir, file_name)
    
    print(f"Target File Path: {file_path}")
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        print("Calling OpenAI TTS API...")
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        print("Response received successfully.")
        
        # Save to file
        response.stream_to_file(file_path)
        print(f"Saved audio file to: {file_path}")
        
        if os.path.exists(file_path):
            print(f"File exists! Size: {os.path.getsize(file_path)} bytes")
        else:
            print("Error: File was not created.")
            
    except Exception as e:
        print(f"TTS Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tts()
