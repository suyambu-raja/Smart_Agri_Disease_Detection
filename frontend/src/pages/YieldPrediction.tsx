import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { Loader2 } from 'lucide-react';
import { predictYield } from '@/lib/api';
import { useTTS } from '@/hooks/useTTS';

const DISTRICTS = [
  'Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem',
  'Tirunelveli', 'Erode', 'Vellore', 'Thoothukudi', 'Dindigul',
  'Thanjavur', 'Ranipet', 'Sivagangai', 'Namakkal', 'Karur',
  'Cuddalore', 'Kanyakumari', 'Krishnagiri',
];

const SOIL_TYPES = [
  'Red Soil', 'Black Soil', 'Alluvial Soil', 'Laterite Soil',
  'Sandy Soil', 'Clay Soil', 'Loamy Soil',
];

const CROPS = [
  'Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton',
  'Groundnut', 'Millets', 'Pulses', 'Banana', 'Coconut',
  'Turmeric', 'Tea',
];

const chartData = [
  { month: 'Jan', yield: 30 }, { month: 'Feb', yield: 45 },
  { month: 'Mar', yield: 55 }, { month: 'Apr', yield: 38 },
  { month: 'May', yield: 60 }, { month: 'Jun', yield: 48 },
  { month: 'Jul', yield: 52 }, { month: 'Aug', yield: 70 },
];

const YieldPrediction = () => {
  const { t } = useTranslation();
  const { speak } = useTTS();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [district, setDistrict] = useState('Coimbatore');
  const [soilType, setSoilType] = useState('Black Soil');
  const [crop, setCrop] = useState('Rice');
  const [rainfall, setRainfall] = useState(120);
  const [temperature, setTemperature] = useState(30);
  const [landArea, setLandArea] = useState(5);

  const [result, setResult] = useState<null | {
    yield_per_acre: number;
    total: number;
    risk: string;
    suggestion: string;
    weather_impact: string;
  }>(null);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await predictYield({
        district,
        soil_type: soilType,
        crop,
        rainfall,
        temperature,
      });

      // Calculate total based on land area
      const yieldPerAcre = Math.round(res.predicted_yield);
      const total = Math.round(yieldPerAcre * landArea);

      // Generate contextual suggestions
      let suggestion = '';
      if (res.risk_level === 'High') {
        suggestion = t('suggestion_high_risk');
      } else if (res.risk_level === 'Medium') {
        suggestion = t('suggestion_medium_risk');
      } else {
        suggestion = t('suggestion_low_risk');
      }

      const weatherImpact = temperature > 35
        ? t('impact_high_temp')
        : temperature < 20
          ? t('impact_low_temp')
          : t('impact_optimal', { rainfall, temperature, crop: t(`crop_${crop.toLowerCase()}`) });

      setResult({
        yield_per_acre: yieldPerAcre,
        total,
        risk: res.risk_level,
        suggestion,
        weather_impact: weatherImpact,
      });
    } catch (err: any) {
      setError(err.message || t('error_analyze'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      <div className="p-4 space-y-5">
        <h1 className="text-xl font-bold text-foreground">{t('yield_prediction')}</h1>

        <form onSubmit={handlePredict} className="bg-card rounded-2xl shadow-card p-4 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-muted-foreground font-medium mb-1 block">{t('district')}</label>
              <select
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                onFocus={() => speak(t('select_district') || 'Select district')}
                className="w-full px-3 py-3 bg-background border border-border rounded-xl text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-green-500/30 appearance-none"
              >
                {DISTRICTS.map((d) => <option key={d} value={d}>{t(`district_${d.toLowerCase()}`)}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-muted-foreground font-medium mb-1 block">{t('soil_type')}</label>
              <select
                value={soilType}
                onChange={(e) => setSoilType(e.target.value)}
                onFocus={() => speak(t('select_soil_type') || 'Select soil type')}
                className="w-full px-3 py-3 bg-background border border-border rounded-xl text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-green-500/30 appearance-none"
              >
                {SOIL_TYPES.map((s) => {
                  // Clean string for key: "Red Soil" -> "soil_red"
                  const key = `soil_${s.split(' ')[0].toLowerCase()}`;
                  return <option key={s} value={s}>{t(key)}</option>;
                })}
              </select>
            </div>
            <div>
              <label className="text-xs text-muted-foreground font-medium mb-1 block">{t('crop_type')}</label>
              <select
                value={crop}
                onChange={(e) => setCrop(e.target.value)}
                onFocus={() => speak(t('select_crop_type') || 'Select crop type')}
                className="w-full px-3 py-3 bg-background border border-border rounded-xl text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-green-500/30 appearance-none"
              >
                {CROPS.map((c) => <option key={c} value={c}>{t(`crop_${c.toLowerCase()}`)}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-muted-foreground font-medium mb-1 block">{t('rainfall_mm')}</label>
              <input
                type="number"
                value={rainfall}
                onChange={(e) => setRainfall(Number(e.target.value))}
                onFocus={() => speak(t('enter_rainfall') || 'Enter rainfall')}
                className="w-full px-3 py-3 bg-background border border-border rounded-xl text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-green-500/30"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-muted-foreground font-medium mb-1 block">{t('temperature_c')}</label>
              <input
                type="number"
                value={temperature}
                onChange={(e) => setTemperature(Number(e.target.value))}
                onFocus={() => speak(t('enter_temperature') || 'Enter temperature')}
                className="w-full px-3 py-3 bg-background border border-border rounded-xl text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-green-500/30"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground font-medium mb-1 block">{t('land_area')}</label>
              <input
                type="number"
                value={landArea}
                onChange={(e) => setLandArea(Number(e.target.value))}
                onFocus={() => speak(t('enter_land_area') || 'Enter land area')}
                className="w-full px-3 py-3 bg-background border border-border rounded-xl text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-green-500/30"
              />
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-destructive/10 text-destructive p-3 rounded-xl text-sm">
              ⚠️ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            onFocus={() => speak(t('predict'))}
            className="w-full bg-gradient-to-r from-teal-400 to-emerald-500 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-green-500/30 disabled:opacity-60 flex items-center justify-center gap-2 active:scale-[0.98] transition-all"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> {t('predicting')}
              </>
            ) : (
              t('predict')
            )}
          </button>
        </form>

        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <div className="bg-card rounded-2xl shadow-card p-4 space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-secondary rounded-xl p-3 text-center">
                    <p className="text-xs text-muted-foreground">{t('predicted_yield')}</p>
                    <p className="text-xl font-bold text-primary">{result.yield_per_acre} kg/acre</p>
                  </div>
                  <div className="bg-secondary rounded-xl p-3 text-center">
                    <p className="text-xs text-muted-foreground">{t('total_yield')}</p>
                    <p className="text-xl font-bold text-foreground">{result.total} kg</p>
                  </div>
                </div>
                <div className="bg-secondary rounded-xl p-3 flex items-center justify-between">
                  <p className="text-xs font-medium text-muted-foreground">{t('risk_level_label')}</p>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${result.risk === 'Low' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                    result.risk === 'Medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                      'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}>
                    {t(result.risk.toLowerCase())}
                  </span>
                </div>
                <div className="bg-secondary rounded-xl p-3">
                  <p className="text-xs font-medium text-muted-foreground mb-1">{t('improvement')}</p>
                  <p className="text-sm text-foreground">{result.suggestion}</p>
                </div>
                <div className="bg-secondary rounded-xl p-3">
                  <p className="text-xs font-medium text-muted-foreground mb-1">{t('weather_impact')}</p>
                  <p className="text-sm text-foreground">{result.weather_impact}</p>
                </div>
              </div>

              <div className="bg-card rounded-2xl shadow-card p-4">
                <h3 className="font-semibold text-foreground mb-3">{t('yield_history')}</h3>
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart data={chartData}>
                    <XAxis dataKey="month" tick={{ fontSize: 11 }} stroke="hsl(120,10%,45%)" />
                    <YAxis tick={{ fontSize: 11 }} stroke="hsl(120,10%,45%)" />
                    <Tooltip />
                    <Bar dataKey="yield" fill="url(#yieldGradient)" radius={[4, 4, 0, 0]} />
                    <defs>
                      <linearGradient id="yieldGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#0ea5e9" stopOpacity={1} />
                        <stop offset="100%" stopColor="#22c55e" stopOpacity={0.8} />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default YieldPrediction;
