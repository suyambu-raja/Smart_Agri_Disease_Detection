import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import WeatherCard from '@/components/WeatherCard';

const forecastData = [
  { day: 'Mon', temp: 31 }, { day: 'Tue', temp: 29 },
  { day: 'Wed', temp: 30 }, { day: 'Thu', temp: 28 },
  { day: 'Fri', temp: 32 }, { day: 'Sat', temp: 33 },
  { day: 'Sun', temp: 30 },
];

const WeatherPage = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-background pb-20">
      <div className="p-4 space-y-5">
        <h1 className="text-xl font-bold text-foreground">{t('weather')}</h1>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <WeatherCard />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-card rounded-2xl shadow-card p-4"
        >
          <h3 className="font-semibold text-foreground mb-3">{t('forecast_7day')}</h3>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={forecastData}>
              <XAxis dataKey="day" tick={{ fontSize: 11 }} stroke="hsl(120,10%,45%)" />
              <YAxis tick={{ fontSize: 11 }} stroke="hsl(120,10%,45%)" domain={[25, 35]} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="temp"
                stroke="hsl(125, 55%, 33%)"
                strokeWidth={2}
                dot={{ fill: 'hsl(125, 55%, 33%)', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </div>
  );
};

export default WeatherPage;
