import os
import hashlib
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from openai import OpenAI

class TextToSpeechView(APIView):
    """
    Generate speech from text using OpenAI TTS.
    Caches the result to avoid repeated API calls and costs.
    """
    # Allow any user (even unauthenticated) to hear UI elements
    # But for tighter security in production, you might want IsAuthenticated
    permission_classes = [AllowAny]

    def post(self, request):
        text = request.data.get('text')
        lang = request.data.get('lang', 'en') # 'en' or 'ta'
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)

        # Create unique filename based on text & language
        # We use MD5 hash ensuring same text always gets same file
        # Using a hash ensures we don't store duplicate files
        file_hash = hashlib.md5(f"{text}-{lang}".encode('utf-8')).hexdigest()
        file_name = f"{file_hash}.mp3"
        
        # Ensure media/tts directory exists
        tts_dir = os.path.join(settings.MEDIA_ROOT, 'tts')
        os.makedirs(tts_dir, exist_ok=True)
        
        file_path = os.path.join(tts_dir, file_name)
        
        # Construct absolute URL
        # request.build_absolute_uri() ensures full domain is prepended
        file_url = f"{settings.MEDIA_URL}tts/{file_name}"
        full_url = request.build_absolute_uri(file_url)

        # 1. Check Cache
        if os.path.exists(file_path):
            return JsonResponse({'audio_url': full_url, 'cached': True})

        # 2. Call OpenAI API if not cached
        try:
            if not settings.OPENAI_API_KEY:
                 return JsonResponse({'error': 'Server missing OpenAI API Key'}, status=500)

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Use 'alloy' (neutral) or 'shimmer' (clearer)
            # tts-1 is faster (low latency), tts-1-hd is higher quality
            # For UI interactions, speed is key -> tts-1
            response = client.audio.speech.create(
                model="tts-1",
                voice="shimmer",
                input=text
            )
            
            # Save to file
            # In latest OpenAI SDK, stream_to_file is available method on the response wrapper
            response.stream_to_file(file_path)
            
            return JsonResponse({'audio_url': full_url, 'cached': False})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
