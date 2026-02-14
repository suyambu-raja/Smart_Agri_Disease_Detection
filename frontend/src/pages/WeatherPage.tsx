import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, LabelList, Cell, CartesianGrid
} from 'recharts';
import {
  MapPin, Droplets, Wind, CloudRain, Thermometer
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { useTTS } from '@/hooks/useTTS';

const forecastData = [
  { day: 'Mon', temp: 32 },
  { day: 'Tue', temp: 28 },
  { day: 'Wed', temp: 29 },
  { day: 'Thu', temp: 32 },
  { day: 'Fri', temp: 32 },
  { day: 'Sat', temp: 31 },
  { day: 'Sun', temp: 29 },
];

interface WeatherData {
  temp: number;
  humidity: number;
  wind: number;
  rainfall: number;
  condition: string;
  location: string;
}

const WeatherPage = () => {
  const { t } = useTranslation();
  const { speak } = useTTS();

  // State for weather data
  const [targetCity, setTargetCity] = useState('Chennai');
  const [inputCity, setInputCity] = useState('Chennai');
  const [isEditing, setIsEditing] = useState(false);
  const [weather, setWeather] = useState({
    temp: 27,
    humidity: 54,
    wind: 15,
    rainfall: 0,
    condition: 'Mist',
    location: 'Coimbatore',
  });

  useEffect(() => {
    apiFetch<any>('/users/profile/', {}, true)
      .then(res => {
        if (res.data?.location) {
          setTargetCity(res.data.location);
          setInputCity(res.data.location);
        }
      })
      .catch(() => console.log("Using default location"));
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
    const interval = setInterval(fetchWeather, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, [targetCity]);

  const handleCitySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (inputCity.trim()) {
      const newCity = inputCity.trim();
      setTargetCity(newCity);
      setIsEditing(false);
      try {
        await apiFetch('/users/profile/', {
          method: 'PATCH',
          body: JSON.stringify({ location: newCity })
        }, true);
      } catch (e) {
        console.error("Failed to save location", e);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50/50 pb-24 font-sans flex flex-col items-center pt-2 md:pt-8 w-full">

      <div className="w-full max-w-7xl px-4 md:px-8 space-y-6 md:space-y-8">

        {/* Header */}
        <div className="flex items-center justify-between pt-2">
          <h1 className="text-xl md:text-3xl font-bold text-gray-900 tracking-tight">{t('weather_dashboard')}</h1>
          <div className="text-xs md:text-sm font-medium text-gray-500 bg-white px-3 py-1.5 md:px-4 md:py-2 rounded-full shadow-sm border border-gray-100 hidden sm:block">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'long' })}
          </div>
        </div>

        {/* 1. HERO SECTION */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative w-full rounded-[2rem] overflow-hidden shadow-2xl bg-white group min-h-[30rem] md:min-h-0 md:h-[24rem] transition-all"
        >
          {/* Background Image */}
          <div className="absolute inset-0 z-0">
            <img
              src="https://images.unsplash.com/photo-1472214103451-9374bd1c798e?q=80&w=2000&auto=format&fit=crop"
              alt="Landscape"
              className="w-full h-full object-cover transform md:scale-105 transition-transform duration-[20s] ease-linear"
            />

            {/* Gradient Overlays */}
            <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/80 md:hidden"></div>
            <div className="hidden md:block absolute inset-0 bg-gradient-to-r from-black/40 via-transparent to-black/20"></div>
          </div>

          {/* Content Layer */}
          <div className="relative z-10 p-6 md:p-10 flex flex-col md:flex-row h-full justify-between text-white md:text-gray-800">

            {/* Left: Main Metrics */}
            <div className="flex flex-col justify-start md:justify-center h-full space-y-8 md:space-y-0 text-white drop-shadow-md pt-4 md:pt-0">

              {/* Location Picker */}
              <div className="flex items-center gap-2 self-start cursor-pointer bg-black/20 md:bg-white/10 px-4 py-2 rounded-full transition-colors backdrop-blur-md border border-white/20" onClick={() => setIsEditing(true)}>
                <MapPin size={18} className="text-white" />
                {isEditing ? (
                  <form onSubmit={handleCitySubmit}>
                    <input
                      value={inputCity}
                      onChange={(e) => setInputCity(e.target.value)}
                      onBlur={() => setIsEditing(false)}
                      onFocus={() => speak(t('enter_city') || 'Enter city name')}
                      autoFocus
                      className="w-32 bg-transparent border-b-2 border-white focus:outline-none text-base font-bold text-white placeholder-white/70"
                    />
                  </form>
                ) : (
                  <span className="font-bold text-lg tracking-wide">{weather.location}</span>
                )}
              </div>

              {/* Big Temp */}
              <div className="mt-auto md:mt-0">
                <div className="flex flex-col md:flex-row md:items-center gap-0 md:gap-4">
                  <span className="text-[6rem] md:text-[7rem] font-bold leading-none tracking-tighter">
                    {weather.temp}°
                  </span>
                  <div className="flex flex-col gap-1 mt-2 md:mt-4">
                    <span className="text-2xl md:text-2xl font-medium opacity-90">{weather.condition}</span>
                    <span className="text-base md:text-base opacity-75">{t('feels_like', { temp: weather.temp + 2 })}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Glass Metrics Grid */}
            <div className="grid grid-cols-3 gap-3 md:gap-4 w-full md:w-auto mt-8 md:mt-auto md:mb-2">
              {[
                { icon: Droplets, label: t('humidity'), value: `${weather.humidity}%` },
                { icon: Wind, label: t('wind'), value: `${weather.wind} km/h` },
                { icon: CloudRain, label: t('rainfall'), value: `${weather.rainfall} mm` }
              ].map((item, i) => (
                <div key={i} className="bg-white/10 backdrop-blur-md md:bg-white/30 rounded-2xl p-3 md:p-5 flex flex-col items-center justify-center border border-white/20 shadow-lg md:w-32">
                  <item.icon className="w-5 h-5 md:w-6 md:h-6 text-white mb-2" />
                  <span className="text-[10px] md:text-xs font-bold uppercase tracking-wider text-white/80">{item.label}</span>
                  <span className="text-sm md:text-lg font-bold text-white mt-0.5 text-center leading-tight">{item.value}</span>
                </div>
              ))}
            </div>

          </div>
        </motion.div>


        {/* 2. ANALYTICS SECTION */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">

          {/* Forecast Chart */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-[2rem] shadow-sm border border-gray-100 p-6 md:p-8 lg:col-span-2 flex flex-col h-[20rem] md:h-[24rem]"
          >
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="font-bold text-gray-900 text-lg md:text-xl">{t('forecast_7day')}</h3>
                <p className="text-xs md:text-sm text-gray-500 mt-1">{t('predicted_temperature_trends')}</p>
              </div>
            </div>

            <div className="flex-1 w-full min-h-0 relative">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={forecastData} barSize={24} margin={{ top: 20, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#0ea5e9" stopOpacity={1} /> {/* Cyan/Blue */}
                      <stop offset="100%" stopColor="#22c55e" stopOpacity={0.9} /> {/* Green */}
                    </linearGradient>
                  </defs>
                  <CartesianGrid vertical={false} stroke="#E5E7EB" strokeDasharray="3 3" />
                  <XAxis
                    dataKey="day"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#6B7280', fontSize: 12, fontWeight: 600 }}
                    dy={15}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#9CA3AF', fontSize: 11 }}
                    domain={[15, 40]}
                    tickCount={5}
                  />
                  <Bar
                    dataKey="temp"
                    radius={[6, 6, 6, 6]}
                    fill="url(#chartGradient)"
                  >
                    {forecastData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill="url(#chartGradient)" />
                    ))}
                    <LabelList
                      dataKey="temp"
                      position="top"
                      className="hidden sm:block"
                      formatter={(val: number) => `${val}°`}
                      style={{ fill: '#374151', fontSize: 12, fontWeight: 'bold' }}
                      dy={-10}
                    />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Extra Stats */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-[2rem] shadow-sm border border-gray-100 p-6 md:p-8 flex flex-col h-auto md:h-[24rem]"
          >
            <h3 className="font-bold text-gray-900 text-lg md:text-xl mb-6">{t('details')}</h3>

            <div className="space-y-4 md:space-y-6 flex-1 overflow-y-auto pr-2 custom-scrollbar">
              {[
                { label: t('uv_index'), value: 'Moderate (4)', color: 'text-orange-500', bg: 'bg-orange-50' },
                { label: t('pressure'), value: '1012 hPa', color: 'text-blue-500', bg: 'bg-blue-50' },
                { label: t('visibility'), value: '10 km', color: 'text-purple-500', bg: 'bg-purple-50' },
                { label: t('dew_point'), value: '21°C', color: 'text-teal-500', bg: 'bg-teal-50' },
              ].map((stat, i) => (
                <div key={i} className="flex items-center justify-between p-3 md:p-4 rounded-2xl bg-gray-50/50 hover:bg-gray-50 transition-colors">
                  <span className="text-gray-500 font-medium text-sm">{stat.label}</span>
                  <div className={`px-3 py-1 rounded-lg ${stat.bg} ${stat.color} font-bold text-sm`}>
                    {stat.value}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

        </div>

      </div>
    </div>
  );
};

export default WeatherPage;
