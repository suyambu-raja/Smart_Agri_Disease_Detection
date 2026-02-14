import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Camera, BarChart3, History, Settings } from 'lucide-react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import WeatherCard from '@/components/WeatherCard';
import { useAuth } from '@/hooks/useAuth';

const Dashboard = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const displayName = user?.displayName || user?.email?.split('@')[0] || 'Farmer';

  const pieData = [
    { name: t('pie_healthy'), value: 70, color: 'hsl(125, 55%, 33%)' },
    { name: t('pie_bacterial'), value: 10, color: 'hsl(45, 95%, 55%)' },
    { name: t('pie_fungal'), value: 15, color: 'hsl(30, 90%, 55%)' },
    { name: t('pie_viral'), value: 5, color: 'hsl(0, 72%, 51%)' },
  ];

  const quickActions = [
    { icon: Camera, label: t('detect_disease'), path: '/disease-detection', gradient: true },
    { icon: BarChart3, label: t('predict_yield'), path: '/yield-prediction', gradient: true },
    { icon: History, label: t('view_history'), path: '/history', gradient: false },
    { icon: Settings, label: t('settings'), path: '/settings', gradient: false },
  ];

  return (
    <div className="min-h-screen bg-background pb-20">
      <div className="p-4 space-y-5">
        {/* Welcome */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-xl font-bold text-foreground">{t('welcome')}, {displayName}</h1>
          <p className="text-sm text-muted-foreground">{t('welcome_subtitle')}</p>
        </motion.div>

        {/* Weather */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <WeatherCard compact />
        </motion.div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-3">
          {quickActions.map((action, i) => (
            <motion.div
              key={action.path}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.05 }}
            >
              <Link
                to={action.path}
                className={`flex items-center gap-3 p-4 rounded-2xl font-medium text-sm transition-all ${action.gradient
                  ? 'gradient-primary text-primary-foreground shadow-elevated'
                  : 'bg-card text-foreground shadow-card border border-border'
                  }`}
              >
                <action.icon className="w-5 h-5" />
                {action.label}
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Disease Chart */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-card rounded-2xl shadow-card p-4"
        >
          <h3 className="font-semibold text-foreground mb-3">{t('disease_history')}</h3>
          <div className="flex items-center gap-4">
            <ResponsiveContainer width={120} height={120}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={30} outerRadius={55} dataKey="value">
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2 flex-1">
              {pieData.map((item, i) => (
                <div key={i} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ background: item.color }} />
                    <span className="text-foreground">{item.name}</span>
                  </div>
                  <span className="text-muted-foreground">{item.value}%</span>
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
