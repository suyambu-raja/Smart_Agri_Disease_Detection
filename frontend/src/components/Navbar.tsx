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
      <header className="sticky top-0 z-50 bg-[#0f291e] backdrop-blur-md border-b border-[#1e4535] shadow-sm">
        <div className="container flex items-center justify-between h-14 px-4">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 group-hover:bg-emerald-500/20 transition-colors">
              <Leaf className="w-4 h-4 text-emerald-400" />
            </div>
            <span className="font-bold text-gray-100 text-sm group-hover:text-emerald-400 transition-colors tracking-tight">{t('app_name')}</span>
          </Link>
          <div className="flex items-center gap-3">
            <button
              onClick={toggleLanguage}
              className="text-xs font-semibold px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-gray-300 hover:bg-emerald-500/20 hover:text-emerald-300 hover:border-emerald-500/30 transition-all active:scale-95"
            >
              {i18n.language === 'en' ? 'தமிழ்' : 'English'}
            </button>
            {user && !isAuthPage && (
              <>
                <span className="text-xs text-gray-400 hidden sm:inline truncate max-w-[100px]">
                  {user.displayName || user.email}
                </span>
                <Link to="/settings">
                  <Settings className="w-5 h-5 text-gray-400 hover:text-emerald-400 transition-colors" />
                </Link>
                <button
                  onClick={handleSignOut}
                  className="text-gray-400 hover:text-red-400 transition-colors"
                  title="Sign out"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </>
            )}
            {!user && isAuthPage && (
              <Link
                to="/login"
                className="text-xs font-medium px-4 py-2 rounded-full bg-emerald-600 text-white hover:bg-emerald-500 shadow-lg shadow-emerald-500/20 transition-all active:scale-95"
              >
                {t('login')}
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Bottom navigation - only on app pages */}
      {user && !isAuthPage && (
        <nav className="fixed bottom-0 left-0 right-0 z-50 bg-[#0f291e] backdrop-blur-md border-t border-[#1e4535] shadow-[0_-4px_20px_rgba(0,0,0,0.1)] pb-safe">
          <div className="flex items-center justify-around h-16 px-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex flex-col items-center justify-center gap-1 py-1 rounded-xl transition-all duration-300 flex-1 min-w-0 active:scale-95 ${isActive
                    ? 'text-emerald-400 bg-white/5'
                    : 'text-gray-400 hover:text-emerald-200 hover:bg-white/5'
                    }`}
                >
                  <item.icon className={`w-5 h-5 flex-shrink-0 transition-transform duration-300 ${isActive ? 'scale-110 drop-shadow-[0_0_8px_rgba(52,211,153,0.5)]' : ''}`} />
                  <span className={`text-[10px] font-medium leading-tight text-center h-[16px] flex items-center justify-center w-full px-0.5 transition-colors ${isActive ? 'text-emerald-400' : 'text-gray-400'}`}>
                    {item.label}
                  </span>
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
