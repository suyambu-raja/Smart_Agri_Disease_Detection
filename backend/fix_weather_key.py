import requests
import sys
import os

BROKEN_KEY = '11bd0afda4ca4334bd0152117261302'
CITY = 'Chennai'
HEX_CHARS = '0123456789abcdef'

print(f"Attempting to fix key: {BROKEN_KEY} (Length: {len(BROKEN_KEY)})")
print("Trying to find the missing character...")

def check_key(key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={key}&units=metric"
    try:
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            return True
    except:
        pass
    return False

found_key = None

# 1. Try appending at the end
print("Checking suffixes...")
for char in HEX_CHARS:
    candidate = BROKEN_KEY + char
    sys.stdout.write(f"\rTesting: ...{candidate[-5:]}")
    if check_key(candidate):
        print(f"\n\nSUCCESS! Found valid key: {candidate}")
        found_key = candidate
        break

# 2. Try prepending at the start (if not found)
if not found_key:
    print("\nChecking prefixes...")
    for char in HEX_CHARS:
        candidate = char + BROKEN_KEY
        sys.stdout.write(f"\rTesting: {candidate[:5]}...")
        if check_key(candidate):
            print(f"\n\nSUCCESS! Found valid key: {candidate}")
            found_key = candidate
            break

if found_key:
    # Update .env
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        with open(env_path, 'w') as f:
            updated = False
            for line in lines:
                if line.startswith('OPENWEATHER_API_KEY='):
                    f.write(f"OPENWEATHER_API_KEY={found_key}\n")
                    updated = True
                else:
                    f.write(line)
            if not updated:
                f.write(f"\nOPENWEATHER_API_KEY={found_key}\n")
        
        print("Updated .env file with the correct key.")
    else:
        print("Could not find .env file to update.")
else:
    print("\n\nFailed to recover key. It might be missing a character in the middle or have multiple errors.")
