import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Cloud, Droplets, Wind, Thermometer, MapPin } from 'lucide-react';
import { apiFetch } from '@/lib/api';

interface WeatherCardProps {
  compact?: boolean;
}

interface WeatherData {
  temp: number;
  humidity: number;
  wind: number;
  rainfall: number;
  condition: string;
  location: string;
}

const WeatherCard = ({ compact = false }: WeatherCardProps) => {
  const { t } = useTranslation();

  const [targetCity, setTargetCity] = useState('Chennai');
  const [inputCity, setInputCity] = useState('Chennai');
  const [isEditing, setIsEditing] = useState(false);

  // Initialize with default values
  const [weather, setWeather] = useState({
    temp: 32,
    humidity: 84,
    wind: 12,
    rainfall: 29,
    condition: t('overcast_clouds'),
    location: 'Chennai, India',
  });

  useEffect(() => {
    // Fetch user profile settings (district) on mount
    apiFetch<any>('/users/profile/', {}, true)
      .then(res => {
        if (res.data?.location) {
          setTargetCity(res.data.location);
          setInputCity(res.data.location);
        }
      })
      .catch((e) => console.log("Defaulting to Chennai (unauthenticated or no profile)", e));
  }, []);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const data = await apiFetch<WeatherData>(`/weather/current/?city=${encodeURIComponent(targetCity)}`, {}, false);

        setWeather({
          temp: Math.round(data.temp),
          humidity: data.humidity,
          wind: Math.round(data.wind),
          rainfall: data.rainfall || 0,
          condition: data.condition,
          location: data.location || targetCity,
        });
      } catch (error) {
        console.error("Weather sync error:", error);
      }
    };

    fetchWeather();
    const interval = setInterval(fetchWeather, 5000);
    return () => clearInterval(interval);
  }, [t, targetCity]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (inputCity.trim()) {
      const newCity = inputCity.trim();
      setTargetCity(newCity);
      setIsEditing(false);

      // Save preference to profile
      try {
        await apiFetch('/users/profile/', {
          method: 'PATCH',
          body: JSON.stringify({ location: newCity })
        }, true);
      } catch (e) {
        console.error("Failed to save location preference", e);
      }
    }
  };

  if (compact) {
    return (
      <div className="gradient-primary rounded-2xl p-4 text-primary-foreground">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-1 opacity-80 cursor-pointer hover:underline" onClick={() => setIsEditing(true)}>
              <MapPin size={12} />
              {!isEditing && <p className="text-xs">{weather.location}</p>}
              {isEditing && (
                <form onSubmit={handleSubmit} className="inline-block">
                  <input
                    value={inputCity}
                    onChange={(e) => setInputCity(e.target.value)}
                    onBlur={() => setIsEditing(false)}
                    className="text-xs text-black rounded px-1 w-24 ml-1"
                    autoFocus
                  />
                </form>
              )}
            </div>

            <div className="flex items-baseline gap-1 mt-1">
              <span className="text-4xl font-bold">{weather.temp}°C</span>
            </div>
            <p className="text-xs opacity-80 mt-1">{weather.condition}</p>
          </div>
          <div className="text-right space-y-2">
            <div className="flex items-center gap-1.5 text-xs opacity-90">
              <Droplets className="w-3.5 h-3.5" />
              <span>{weather.humidity}%</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs opacity-90">
              <Wind className="w-3.5 h-3.5" />
              <span>{weather.wind} km/h</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs opacity-90">
              <Cloud className="w-3.5 h-3.5" />
              <span>{weather.rainfall} mm</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-card rounded-2xl shadow-card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-foreground">{t('current_weather')}</h3>

        {isEditing ? (
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <input
              value={inputCity}
              onChange={(e) => setInputCity(e.target.value)}
              className="text-sm border rounded px-2 py-1 bg-background text-foreground w-40"
              autoFocus
              placeholder="Enter city..."
              onBlur={() => {
                // Small delay to allow button click to register
                setTimeout(() => setIsEditing(false), 200);
              }}
            />
            <button type="submit" className="text-xs bg-primary text-primary-foreground px-2 py-1 rounded">
              Save
            </button>
          </form>
        ) : (
          <div
            className="flex items-center gap-2 text-sm text-muted-foreground cursor-pointer hover:text-primary transition-colors"
            onClick={() => setIsEditing(true)}
            title="Click to change location"
          >
            <MapPin size={16} />
            <span>{weather.location}</span>
          </div>
        )}
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-baseline">
          <Thermometer className="w-8 h-8 text-primary mr-2" />
          <span className="text-5xl font-bold text-foreground">{weather.temp}°C</span>
        </div>
        <p className="text-sm text-muted-foreground">{weather.condition}</p>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-secondary rounded-xl p-3 text-center">
          <Droplets className="w-5 h-5 text-primary mx-auto mb-1" />
          <p className="text-xs text-muted-foreground">{t('humidity')}</p>
          <p className="font-semibold text-foreground">{weather.humidity}%</p>
        </div>
        <div className="bg-secondary rounded-xl p-3 text-center">
          <Wind className="w-5 h-5 text-primary mx-auto mb-1" />
          <p className="text-xs text-muted-foreground">{t('wind_speed')}</p>
          <p className="font-semibold text-foreground">{weather.wind} km/h</p>
        </div>
        <div className="bg-secondary rounded-xl p-3 text-center">
          <Cloud className="w-5 h-5 text-primary mx-auto mb-1" />
          <p className="text-xs text-muted-foreground">{t('rainfall')}</p>
          <p className="font-semibold text-foreground">{weather.rainfall} mm</p>
        </div>
      </div>
    </div>
  );
};

export default WeatherCard;
