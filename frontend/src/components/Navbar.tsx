import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Leaf, Home, Camera, BarChart3, Cloud, History, Settings, LogOut } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

const Navbar = () => {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { user, signOut } = useAuth();

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === 'en' ? 'ta' : 'en');
  };

  const handleSignOut = async () => {
    await signOut();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', icon: Home, label: t('dashboard') },
    { path: '/disease-detection', icon: Camera, label: t('detect_disease') },
    { path: '/yield-prediction', icon: BarChart3, label: t('predict_yield') },
    { path: '/weather', icon: Cloud, label: t('weather') },
    { path: '/history', icon: History, label: t('history') },
  ];

  const isAuthPage = ['/', '/login', '/register'].includes(location.pathname);

  return (
    <>
      {/* Top navbar */}
      <header className="sticky top-0 z-50 bg-[#1e3c2f] shadow-lg shadow-emerald-900/10">
        <div className="container flex items-center justify-between h-14 px-4">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center border border-white/20">
              <Leaf className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-white text-base tracking-wide">{t('app_name')}</span>
          </Link>
          <div className="flex items-center gap-3">
            <button
              onClick={toggleLanguage}
              className="text-xs font-medium px-3 py-1.5 rounded-lg bg-white/10 text-white/90 hover:bg-white/20 transition-all active:scale-95 border border-white/10"
            >
              {i18n.language === 'en' ? 'தமிழ்' : 'English'}
            </button>
            {user && !isAuthPage && (
              <>
                <Link to="/settings" className="p-2 rounded-full hover:bg-white/10 transition-colors">
                  <Settings className="w-5 h-5 text-white/80" />
                </Link>
                <button
                  onClick={handleSignOut}
                  className="p-2 rounded-full hover:bg-white/10 transition-colors"
                  title="Sign out"
                >
                  <LogOut className="w-5 h-5 text-white/80" />
                </button>
              </>
            )}
            {!user && isAuthPage && (
              <Link
                to="/login"
                className="text-xs font-bold px-5 py-2 rounded-full bg-white text-[#1e3c2f] hover:bg-gray-100 shadow-md transition-all active:scale-95"
              >
                {t('login')}
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Bottom navigation - only on app pages */}
      {user && !isAuthPage && (
        <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-t border-gray-100 shadow-[0_-4px_20px_rgba(0,0,0,0.05)] pb-[env(safe-area-inset-bottom)]">
          <div className="flex items-center justify-around h-16 pt-1 px-4">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className="flex flex-col items-center justify-center gap-1.5 py-1 flex-1 min-w-0 active:scale-95 transition-transform"
                >
                  <item.icon
                    className={`w-6 h-6 flex-shrink-0 transition-all ${isActive ? 'text-emerald-600 stroke-[2.5px]' : 'text-gray-400 stroke-[1.5px]'}`}
                  />
                  <span className={`text-[10px] font-medium leading-tight text-center ${isActive ? 'text-emerald-700' : 'text-gray-400'} transition-colors`}>
                    {item.label}
                  </span>
                  {isActive && <div className="absolute top-0 w-8 h-1 bg-emerald-500 rounded-b-full" />}
                </Link>
              );
            })}
          </div>
        </nav>
      )}
    </>
  );
};

export default Navbar;
