import requests
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

BROKEN_KEY = '11bd0afda4ca4334bd0152117261302'
CITY = 'Chennai' 
HEX_CHARS = '0123456789abcdef'

print(f"Broken Key: {BROKEN_KEY} (Len: {len(BROKEN_KEY)})")
print("Brute-forcing missing character at all positions...")

found_key = None

def check_candidate(candidate):
    global found_key
    if found_key: return None # Stop if already found
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={candidate}&units=metric"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            return candidate
    except:
        pass
    return None

# Generate all candidates (32 positions * 16 chars = 512)
candidates = []
for i in range(len(BROKEN_KEY) + 1):
    for char in HEX_CHARS:
        candidate = BROKEN_KEY[:i] + char + BROKEN_KEY[i:]
        candidates.append(candidate)

print(f"Testing {len(candidates)} candidates with 20 threads...")

with ThreadPoolExecutor(max_workers=20) as executor:
    future_to_cand = {executor.submit(check_candidate, cand): cand for cand in candidates}
    for future in as_completed(future_to_cand):
        result = future.result()
        if result:
            found_key = result
            print(f"\nSUCCESS! Found valid key: {result}")
            
            # Update .env immediately
            env_path = '.env'
            try:
                content = ""
                if os.path.exists(env_path):
                    with open(env_path, 'r') as f:
                        lines = f.readlines()
                    
                    updated = False
                    with open(env_path, 'w') as f:
                        for line in lines:
                            if line.startswith('OPENWEATHER_API_KEY='):
                                f.write(f"OPENWEATHER_API_KEY={found_key}\n")
                                updated = True
                            else:
                                f.write(line)
                        if not updated:
                            f.write(f"\nOPENWEATHER_API_KEY={found_key}\n")
                    print("Updated .env file.")
                else:
                    print("No .env file found.")
            except Exception as e:
                print(f"Error updating .env: {e}")
            
            # Exit loop and script
            os._exit(0)

print("\nFailed to find valid key.")
