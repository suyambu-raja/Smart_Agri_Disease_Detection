import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { apiFetch } from '@/lib/api';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogOut, Trash2, ChevronRight } from 'lucide-react';

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
            // Update language if different
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
    <div className="min-h-screen bg-background pb-20">
      <div className="p-4 space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-lg">✓</span>
          </div>
          <h1 className="text-xl font-bold text-foreground">{t('settings')}</h1>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-card rounded-2xl shadow-card divide-y divide-border"
        >
          {/* Language */}
          <div className="p-4 flex items-center justify-between">
            <span className="text-sm font-medium text-foreground">{t('change_language')}: {i18n.language === 'en' ? 'English' : 'தமிழ்'}</span>
            <button
              onClick={handleLanguageChange}
              className="text-sm text-primary font-medium flex items-center gap-1"
            >
              {i18n.language === 'en' ? 'தமிழ்' : 'English'}
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {/* District */}
          <div className="p-4 flex items-center justify-between">
            <span className="text-sm font-medium text-foreground">{t('change_district')}: {selectedDistrict}</span>
            <select
              value={selectedDistrict}
              onChange={handleDistrictChange}
              className="text-sm text-primary font-medium bg-transparent focus:outline-none"
            >
              {DISTRICTS.map((d) => <option key={d} value={d}>{t(`district_${d.toLowerCase()}`)}</option>)}
            </select>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="space-y-3"
        >
          <button
            onClick={() => navigate('/login')}
            className="w-full bg-destructive/10 text-destructive font-semibold py-3.5 rounded-xl flex items-center justify-center gap-2"
          >
            <LogOut className="w-4 h-4" /> {t('logout')}
          </button>
          <button className="w-full bg-card border border-destructive/30 text-destructive font-medium py-3.5 rounded-xl flex items-center justify-center gap-2">
            <Trash2 className="w-4 h-4" /> {t('delete_account')}
          </button>
        </motion.div>
      </div>
    </div>
  );
};

export default SettingsPage;
