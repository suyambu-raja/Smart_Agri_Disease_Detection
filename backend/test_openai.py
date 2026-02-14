import os
import sys
import django
from django.conf import settings
from openai import OpenAI

# Setup Django environment manually to access settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_agriculture.settings')
django.setup()

def test_key():
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        print("Error: OPENAI_API_KEY not found in settings.")
        return

    print(f"Testing OpenAI Key: {api_key[:5]}...{api_key[-5:]}")
    
    client = OpenAI(api_key=api_key)
    
    try:
        # Try a cheap/simple call
        response = client.models.list()
        print("Success! API Key is valid. Models list retrieved.")
        # print([m.id for m in response.data[:5]])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_key()
