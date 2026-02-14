import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell } from 'recharts';
import WeatherCard from '@/components/WeatherCard';
import { useAuth } from '@/hooks/useAuth';

const Dashboard = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const displayName = user?.displayName || user?.email?.split('@')[0] || t('farmer', 'Farmer');

  const pieData = [
    { name: t('pie_healthy'), value: 70, color: 'hsl(125, 55%, 33%)' },
    { name: t('pie_bacterial'), value: 10, color: 'hsl(45, 95%, 55%)' },
    { name: t('pie_fungal'), value: 15, color: 'hsl(30, 90%, 55%)' },
    { name: t('pie_viral'), value: 5, color: 'hsl(0, 72%, 51%)' },
  ];

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-40 font-sans relative">

      {/* 1. Header Section - Fixed with Vibrant Gradient */}
      <div className="relative w-full h-80 rounded-b-[40px] overflow-hidden shadow-2xl bg-gradient-to-b from-teal-400 via-emerald-500 to-green-900">

        {/* Decorative organic shapes */}
        <div className="absolute top-[-50%] left-[-20%] w-[80%] h-[200%] bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[150%] bg-green-900/20 rounded-full blur-2xl"></div>

        {/* Header Content */}
        <div className="relative z-10 px-6 pt-12 text-white">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center border border-white/30">
                <span className="font-bold text-lg">🌱</span>
              </div>
              <span className="font-semibold text-lg tracking-wide drop-shadow-md">{t('app_name')}</span>
            </div>
            <div className="text-xs font-medium space-x-2 opacity-90">
              <button
                onClick={() => changeLanguage('en')}
                className={`cursor-pointer hover:underline ${i18n.language === 'en' ? 'font-bold underline' : ''}`}
              >
                English
              </button>
              <button
                onClick={() => changeLanguage('ta')}
                className={`cursor-pointer hover:underline ${i18n.language === 'ta' ? 'font-bold underline' : ''}`}
              >
                தமிழ்
              </button>
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mt-8 text-center"
          >
            <h1 className="text-3xl font-extrabold tracking-tight drop-shadow-md">{t('welcome')}, {displayName}</h1>
            <p className="text-green-50 mt-2 text-sm font-medium tracking-wide drop-shadow-sm opacity-90">
              {t('welcome_subtitle')}
            </p>
          </motion.div>
        </div>
      </div>

      {/* Main Content Actions */}
      <div className="px-5 -mt-20 relative z-20 space-y-6">

        {/* 2. Weather Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="rounded-3xl shadow-xl overflow-hidden bg-white/20 backdrop-blur-md border border-white/30"
        >
          <div className="bg-white/90 backdrop-blur-sm p-1 rounded-3xl">
            <WeatherCard compact={true} />
          </div>
        </motion.div>

        {/* 3. Action Buttons */}
        <div className="grid grid-cols-2 gap-4">
          <Link to="/disease-detection" className="col-span-1 group">
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full h-full py-5 bg-gradient-to-r from-teal-400 to-emerald-500 text-white rounded-2xl shadow-lg shadow-green-500/30 flex flex-col items-center justify-center gap-1 transition-all"
            >
              <span className="text-sm font-bold tracking-wide">{t('detect_disease')}</span>
            </motion.div>
          </Link>
          <Link to="/yield-prediction" className="col-span-1 group">
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full h-full py-5 bg-gradient-to-r from-teal-400 to-emerald-500 text-white rounded-2xl shadow-lg shadow-green-500/30 flex flex-col items-center justify-center gap-1 transition-all"
            >
              <span className="text-sm font-bold tracking-wide">{t('predict_yield')}</span>
            </motion.div>
          </Link>
        </div>

        {/* 4. Disease Detection History */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-[2rem] p-6 pb-8 shadow-xl shadow-gray-200 mb-24"
        >
          <h3 className="text-gray-800 font-bold mb-4 text-base">{t('disease_history')}</h3>
          <div className="flex items-center gap-6">
            <PieChart width={120} height={120}>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={30} outerRadius={55} dataKey="value" stroke="none">
                {pieData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
            <div className="space-y-3 flex-1">
              {pieData.map((item, i) => (
                <div key={i} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full shadow-sm" style={{ background: item.color }} />
                    <span className="text-gray-700 font-medium">{item.name}</span>
                  </div>
                  <span className="text-gray-500 font-semibold">{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
