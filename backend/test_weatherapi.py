import requests

API_KEY = "11bd0afda4ca4334bd0152117261302"
CITY = "Chennai"
url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}&aqi=no"

try:
    print(f"Testing WeatherAPI.com with key: {API_KEY}")
    resp = requests.get(url, timeout=5)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print("Success!")
        print(f"Temp: {data['current']['temp_c']} C")
        print(f"Condition: {data['current']['condition']['text']}")
        print(f"Wind: {data['current']['wind_kph']} km/h")
        print(f"Humidity: {data['current']['humidity']} %")
        print(f"Location: {data['location']['name']}, {data['location']['country']}")
    else:
        print(f"Error: {resp.text}")
except Exception as e:
    print(f"Exception: {e}")
