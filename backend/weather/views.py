from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from .models import WeatherLog
from django.utils import timezone
import requests
import datetime

class WeatherView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        city = request.query_params.get('city', 'Chennai')
        
        # Check cache
        last_log = WeatherLog.objects.filter(city__istartswith=city).first()
        should_fetch = False
        
        if not last_log:
            should_fetch = True
        else:
            time_diff = timezone.now() - last_log.timestamp
            # Update every 10 minutes
            if time_diff.total_seconds() > 600:
                should_fetch = True
        
        api_key = getattr(settings, 'WEATHER_API_KEY', None)
        if not api_key:
             should_fetch = False
             print("Weather API Key missing.")

        if should_fetch:
            try:
                # Use WeatherAPI.com
                url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    current = data['current']
                    location = data['location']
                    
                    WeatherLog.objects.create(
                        city=location['name'],
                        temperature=current['temp_c'],
                        humidity=current['humidity'],
                        pressure=current['pressure_mb'],
                        wind_speed=current['wind_kph'],
                        description=current['condition']['text'],
                        rainfall=current.get('precip_mm', 0.0),
                        clouds=current.get('cloud', 0)
                    )
            except Exception as e:
                print(f"Weather Fetch Error: {e}")

        latest = WeatherLog.objects.filter(city__istartswith=city).first()
        
        if not latest:
            # Fallback mock
            return Response({
                "temp": 32,
                "humidity": 84,
                "wind": 12,
                "rainfall": 29,
                "condition": "Overcast (Mock)",
                "location": city,
                "mock": True
            })

        return Response({
            "temp": latest.temperature,
            "humidity": latest.humidity,
            "wind": latest.wind_speed,
            "rainfall": latest.rainfall,
            "condition": latest.description,
            "location": latest.city,
            "timestamp": latest.timestamp,
            "mock": False
        })
