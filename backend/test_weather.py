import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

API_KEY = os.getenv('OPENWEATHER_API_KEY')
CITY = 'Chennai'

print(f"Testing Weather API Key from environment...")
print(f"API Key: {API_KEY}")

if not API_KEY:
    print("Error: OPENWEATHER_API_KEY not found in .env")
    exit()

if len(API_KEY) != 32:
    print(f"ERROR: Key length is {len(API_KEY)}. OpenWeatherMap keys must be 32 characters.")
    print("Common issue: Copy-paste error missing first or last character.")
else:
    print("Key length is correct (32 characters).")

try:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    print(f"Requesting: {url.replace(API_KEY, 'HIDDEN')}")
    resp = requests.get(url)
    print(f"Status Code: {resp.status_code}")
    
    if resp.status_code == 200:
        print("Success! Real weather data received:")
        print(resp.json())
    else:
        print(f"Failed: {resp.text}")
        
except Exception as e:
    print(f"Connection Error: {e}")
