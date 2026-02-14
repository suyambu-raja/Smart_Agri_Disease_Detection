import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Camera, BarChart3, CloudSun, Globe, Leaf } from 'lucide-react';
import { motion } from 'framer-motion';
import heroBg from '@/assets/hero-bg.jpg';

const Landing = () => {
  const { t } = useTranslation();

  const features = [
    { icon: Camera, label: t('feature_disease'), color: 'text-primary' },
    { icon: CloudSun, label: t('feature_weather'), color: 'text-chart-blue' },
    { icon: BarChart3, label: t('feature_yield'), color: 'text-chart-orange' },
    { icon: Leaf, label: t('feature_soil'), color: 'text-primary' },
    { icon: Globe, label: t('feature_language'), color: 'text-chart-yellow' },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <section className="relative min-h-[70vh] flex items-end overflow-hidden">
        <div className="absolute inset-0">
          <img src={heroBg} alt="Agriculture" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-foreground/90 via-foreground/50 to-transparent" />
        </div>
        <div className="relative z-10 p-6 pb-10 w-full">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-3xl font-bold text-primary-foreground leading-tight mb-3">
              {t('hero_title')}
            </h1>
            <p className="text-sm text-primary-foreground/80 mb-6 leading-relaxed">
              {t('hero_subtitle')}
            </p>
            <div className="flex gap-3">
              <Link
                to="/login"
                className="flex-1 gradient-primary text-primary-foreground font-semibold py-3 rounded-xl text-center text-sm shadow-elevated hover:opacity-90 transition-opacity"
              >
                {t('detect_disease')}
              </Link>
              <Link
                to="/login"
                className="flex-1 bg-accent text-accent-foreground font-semibold py-3 rounded-xl text-center text-sm shadow-card hover:opacity-90 transition-opacity"
              >
                {t('predict_yield')}
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="p-6 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          {features.map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.1 }}
              className="bg-card rounded-2xl shadow-card p-4 flex flex-col items-center gap-2 text-center"
            >
              <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
                <feature.icon className={`w-5 h-5 ${feature.color}`} />
              </div>
              <span className="text-xs font-medium text-foreground leading-tight">{feature.label}</span>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="p-6 pt-0">
        <div className="flex gap-3">
          <Link
            to="/login"
            className="flex-1 gradient-primary text-primary-foreground font-semibold py-3 rounded-xl text-center text-sm"
          >
            {t('login')}
          </Link>
          <Link
            to="/register"
            className="flex-1 bg-card border border-primary text-primary font-semibold py-3 rounded-xl text-center text-sm"
          >
            {t('register')}
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Landing;
