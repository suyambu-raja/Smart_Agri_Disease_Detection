import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Globe, MapPin, LogOut, Trash2 } from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { useNavigate } from 'react-router-dom';

const DISTRICTS = [
  'Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem',
  'Tirunelveli', 'Erode', 'Vellore', 'Thoothukudi', 'Dindigul',
];

const SettingsPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [selectedDistrict, setSelectedDistrict] = useState('Chennai');

  useEffect(() => {
    // Load persisted settings
    apiFetch<any>('/users/profile/')
      .then(res => {
        if (res.data) {
          if (res.data.location) {
            setSelectedDistrict(res.data.location);
          }
          if (res.data.language) {
            if (i18n.language !== res.data.language) {
              i18n.changeLanguage(res.data.language);
            }
          }
        }
      })
      .catch(err => console.error("Could not load settings", err));
  }, []);

  const handleLanguageChange = async () => {
    const newLang = i18n.language === 'en' ? 'ta' : 'en';
    i18n.changeLanguage(newLang);

    try {
      await apiFetch('/users/profile/', {
        method: 'PATCH',
        body: JSON.stringify({ language: newLang })
      });
    } catch (error) {
      console.error("Failed to save language", error);
    }
  };

  const handleDistrictChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newDistrict = e.target.value;
    setSelectedDistrict(newDistrict);
    try {
      await apiFetch('/users/profile/', {
        method: 'PATCH',
        body: JSON.stringify({ location: newDistrict }),
      });
    } catch (error) {
      console.error("Failed to update district", error);
    }
  };

  return (
    <div className="min-h-screen bg-background pb-20 relative overflow-hidden">

      {/* Background image: middle to bottom */}
      <div className="absolute left-0 right-0 bottom-0 h-[55%] z-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-b from-background via-background/60 to-transparent z-10" />
        <img
          src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2832&auto=format&fit=crop"
          alt=""
          className="w-full h-full object-cover"
        />
      </div>

      <div className="p-4 space-y-5 relative z-10">
        {/* Title */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-xl font-bold text-foreground">{t('settings')}</h1>
        </motion.div>

        {/* Language */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="bg-card rounded-2xl shadow-card p-4 border border-border"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Globe className="w-5 h-5 text-primary" />
              <span className="font-medium text-foreground">{t('language')}</span>
            </div>
            <button
              onClick={handleLanguageChange}
              className="px-4 py-2 rounded-xl text-sm font-semibold gradient-primary text-primary-foreground shadow-elevated transition-all active:scale-95"
            >
              {i18n.language === 'en' ? 'தமிழ்' : 'English'}
            </button>
          </div>
        </motion.div>

        {/* District */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-card rounded-2xl shadow-card p-4 border border-border"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <MapPin className="w-5 h-5 text-primary" />
              <span className="font-medium text-foreground">{t('district_label') || 'District'}</span>
            </div>
            <select
              value={selectedDistrict}
              onChange={handleDistrictChange}
              className="bg-secondary text-foreground text-sm rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 border border-border"
            >
              {DISTRICTS.map((d) => (
                <option key={d} value={d}>{t(`district_${d.toLowerCase()}`)}</option>
              ))}
            </select>
          </div>
        </motion.div>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="space-y-3 pt-4"
        >
          <button
            onClick={() => navigate('/login')}
            className="w-full flex items-center justify-center gap-2 p-4 rounded-2xl font-medium text-sm gradient-primary text-primary-foreground shadow-elevated transition-all active:scale-[0.98]"
          >
            <LogOut className="w-5 h-5" />
            {t('logout')}
          </button>

          <button className="w-full flex items-center justify-center gap-2 p-4 rounded-2xl font-medium text-sm bg-card text-destructive border border-border shadow-card transition-all active:scale-[0.98]">
            <Trash2 className="w-5 h-5" />
            {t('delete_account')}
          </button>
        </motion.div>
      </div>
    </div>
  );
};

export default SettingsPage;
