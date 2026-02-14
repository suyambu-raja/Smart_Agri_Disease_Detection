import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Leaf, BarChart3, Calendar, ChevronRight, Loader2, AlertTriangle, RefreshCw, X, Sprout, ImageOff } from 'lucide-react';
import { getDiseaseHistory, getYieldHistory, type DiseaseHistoryItem, type YieldHistoryItem } from '@/lib/api';

type TabType = 'disease' | 'yield';

const HistoryPage = () => {
  const { t } = useTranslation();
  const [tab, setTab] = useState<TabType>('disease');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [diseaseHistory, setDiseaseHistory] = useState<DiseaseHistoryItem[]>([]);
  const [yieldHistory, setYieldHistory] = useState<YieldHistoryItem[]>([]);

  // Selected item for detail view
  const [selectedDisease, setSelectedDisease] = useState<DiseaseHistoryItem | null>(null);
  const [selectedYield, setSelectedYield] = useState<YieldHistoryItem | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const [diseaseRes, yieldRes] = await Promise.allSettled([
        getDiseaseHistory(),
        getYieldHistory(),
      ]);

      if (diseaseRes.status === 'fulfilled') {
        setDiseaseHistory(diseaseRes.value.data || []);
      }
      if (yieldRes.status === 'fulfilled') {
        setYieldHistory(yieldRes.value.data || []);
      }

      if (diseaseRes.status === 'rejected' && yieldRes.status === 'rejected') {
        setError('Failed to load history. Please make sure you are logged in.');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  const filteredDisease = diseaseHistory.filter((item) =>
    item.disease_name.toLowerCase().includes(search.toLowerCase())
  );

  const filteredYield = yieldHistory.filter((item) =>
    item.crop.toLowerCase().includes(search.toLowerCase()) ||
    item.district.toLowerCase().includes(search.toLowerCase())
  );

  const riskBadge = (risk: string) => {
    const colors = {
      'Low': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'Medium': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'High': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    };
    return colors[risk as keyof typeof colors] || colors['Medium'];
  };

  return (
    <div className="min-h-screen bg-background pb-20 relative">
      <div className="p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-foreground">{t('history')}</h1>
          <button
            onClick={fetchHistory}
            disabled={loading}
            className="p-2 rounded-lg bg-secondary text-muted-foreground hover:text-primary transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search history..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-card border border-border rounded-xl text-foreground text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
          />
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setTab('disease')}
            className={`flex-1 py-2.5 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all ${tab === 'disease'
              ? 'gradient-primary text-primary-foreground shadow-elevated'
              : 'bg-card text-muted-foreground border border-border'
              }`}
          >
            <Leaf className="w-4 h-4" />
            Disease ({diseaseHistory.length})
          </button>
          <button
            onClick={() => setTab('yield')}
            className={`flex-1 py-2.5 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all ${tab === 'yield'
              ? 'gradient-primary text-primary-foreground shadow-elevated'
              : 'bg-card text-muted-foreground border border-border'
              }`}
          >
            <BarChart3 className="w-4 h-4" />
            Yield ({yieldHistory.length})
          </button>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
          </div>
        )}

        {!loading && (
          <AnimatePresence mode="wait">
            {tab === 'disease' ? (
              <motion.div
                key="disease"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                className="space-y-3"
              >
                {filteredDisease.length === 0 ? (
                  <div className="text-center py-12">
                    <Leaf className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-40" />
                    <p className="text-muted-foreground text-sm">
                      {search ? t('no_results') : t('no_disease_history')}
                    </p>
                    <p className="text-muted-foreground text-xs mt-1">
                      {t('go_detect_msg')}
                    </p>
                  </div>
                ) : (
                  filteredDisease.map((item) => (
                    <motion.div
                      key={item.id}
                      layoutId={`card-${item.id}`}
                      onClick={() => setSelectedDisease(item)}
                      className="bg-card rounded-xl shadow-card p-4 border border-border cursor-pointer active:scale-[0.98] transition-transform"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {item.is_healthy ? (
                            <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                              <Leaf className="w-4 h-4 text-green-600 dark:text-green-300" />
                            </div>
                          ) : (
                            <div className="w-8 h-8 rounded-full bg-orange-100 dark:bg-orange-900 flex items-center justify-center">
                              <AlertTriangle className="w-4 h-4 text-orange-600 dark:text-orange-300" />
                            </div>
                          )}
                          <div>
                            <p className="font-semibold text-foreground text-sm">{item.disease_name}</p>
                            <p className="text-xs text-muted-foreground">{t('confidence')}: {item.confidence}%</p>
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-muted-foreground" />
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Calendar className="w-3 h-3" />
                        {formatDate(item.created_at)}
                      </div>
                    </motion.div>
                  ))
                )}
              </motion.div>
            ) : (
              <motion.div key="yield" className="space-y-3">
                {filteredYield.length === 0 ? (
                  <div className="text-center py-12">
                    <BarChart3 className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-40" />
                    <p className="text-muted-foreground text-sm">
                      {search ? t('no_results') : t('no_yield_history')}
                    </p>
                    <p className="text-muted-foreground text-xs mt-1">
                      {t('go_yield_msg')}
                    </p>
                  </div>
                ) : (
                  filteredYield.map((item) => (
                    <div key={item.id} className="bg-card rounded-xl p-4 border border-border">
                      <div className="flex justify-between items-center">
                        <p className="font-bold">{item.crop}</p>
                        <span className={`px-2 py-0.5 rounded text-xs ${riskBadge(item.risk_level)}`}>{item.risk_level}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{t('predicted_yield')}: {item.predicted_yield} {item.unit}</p>
                    </div>
                  ))
                )}
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </div>

      {/* DETAILED VIEW MODAL */}
      <AnimatePresence>
        {selectedDisease && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedDisease(null)}
              className="fixed inset-0 bg-black/60 z-40 backdrop-blur-sm"
            />
            <motion.div
              layoutId={`card-${selectedDisease.id}`}
              className="fixed inset-x-4 top-[10%] bottom-[10%] md:inset-[20%] z-50 bg-card rounded-2xl shadow-2xl border border-border overflow-hidden flex flex-col"
            >
              <div className="relative h-48 sm:h-64 bg-secondary flex items-center justify-center overflow-hidden">
                {selectedDisease.image_url ? (
                  <img
                    src={selectedDisease.image_url}
                    alt={selectedDisease.disease_name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="text-center text-muted-foreground">
                    <ImageOff className="w-12 h-12 mx-auto mb-2 opacity-30" />
                    <p className="text-xs">{t('no_image')}</p>
                  </div>
                )}
                <button
                  onClick={(e) => { e.stopPropagation(); setSelectedDisease(null); }}
                  className="absolute top-2 right-2 p-2 bg-black/50 text-white rounded-full hover:bg-black/70 backdrop-blur-sm"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="p-6 flex-1 overflow-y-auto">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-2xl font-bold text-foreground leading-tight mb-1">
                      {selectedDisease.disease_name}
                    </h2>
                    <p className="text-sm text-muted-foreground flex items-center gap-2">
                      <Calendar className="w-3 h-3" />
                      {formatDate(selectedDisease.created_at)}
                    </p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-bold ${selectedDisease.is_healthy ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {selectedDisease.is_healthy ? t('healthy') : t('diseased')}
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-secondary/30 p-4 rounded-xl">
                    <p className="text-sm font-medium mb-2">{t('ai_confidence')}</p>
                    <div className="flex items-center gap-2">
                      <div className="h-2 flex-1 bg-secondary rounded-full overflow-hidden">
                        <div
                          className={`h-full ${selectedDisease.confidence > 80 ? 'bg-primary' : 'bg-yellow-500'}`}
                          style={{ width: `${selectedDisease.confidence}%` }}
                        />
                      </div>
                      <span className="text-xs font-bold">{selectedDisease.confidence}%</span>
                    </div>
                  </div>

                  {!selectedDisease.is_healthy && (
                    <div className="p-4 border border-border rounded-xl bg-card">
                      <h3 className="font-semibold mb-2 flex items-center gap-2">
                        <Sprout className="w-4 h-4 text-primary" />
                        {t('treatment')}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {t('view_treatment_msg')}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default HistoryPage;
