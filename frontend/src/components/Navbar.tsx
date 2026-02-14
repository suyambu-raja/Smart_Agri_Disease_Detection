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
      <header className="sticky top-0 z-50 bg-card/95 backdrop-blur-md border-b border-border shadow-sm">
        <div className="container flex items-center justify-between h-14 px-4">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full gradient-primary flex items-center justify-center">
              <Leaf className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="font-bold text-foreground text-sm">{t('app_name')}</span>
          </Link>
          <div className="flex items-center gap-3">
            <button
              onClick={toggleLanguage}
              className="text-xs font-medium px-3 py-1.5 rounded-full bg-secondary text-secondary-foreground hover:bg-primary hover:text-primary-foreground transition-colors"
            >
              {i18n.language === 'en' ? 'தமிழ்' : 'English'}
            </button>
            {user && !isAuthPage && (
              <>
                <span className="text-xs text-muted-foreground hidden sm:inline truncate max-w-[100px]">
                  {user.displayName || user.email}
                </span>
                <Link to="/settings">
                  <Settings className="w-5 h-5 text-muted-foreground hover:text-primary transition-colors" />
                </Link>
                <button
                  onClick={handleSignOut}
                  className="text-muted-foreground hover:text-destructive transition-colors"
                  title="Sign out"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </>
            )}
            {!user && isAuthPage && (
              <Link
                to="/login"
                className="text-xs font-medium px-3 py-1.5 rounded-full bg-primary text-primary-foreground"
              >
                {t('login')}
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Bottom navigation - only on app pages */}
      {user && !isAuthPage && (
        <nav className="fixed bottom-0 left-0 right-0 z-50 bg-card/95 backdrop-blur-md border-t border-border">
          <div className="flex items-center justify-around h-16 px-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex flex-col items-center justify-center gap-1 py-1 rounded-lg transition-colors flex-1 min-w-0 ${isActive
                    ? 'text-primary'
                    : 'text-muted-foreground hover:text-foreground'
                    }`}
                >
                  <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-primary' : ''}`} />
                  <span className="text-[10px] font-medium leading-tight text-center h-[32px] flex items-center justify-center w-full line-clamp-2 px-0.5">
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
