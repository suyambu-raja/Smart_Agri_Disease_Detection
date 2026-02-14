import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Leaf, BarChart3, Calendar, ChevronRight, Loader2, AlertTriangle, RefreshCw, X, Sprout, ImageOff } from 'lucide-react';
import { getDiseaseHistory, getYieldHistory, type DiseaseHistoryItem, type YieldHistoryItem } from '@/lib/api';

type TabType = 'disease' | 'yield';

const HistoryPage = () => {
  const { t } = useTranslation();
  const [tab, setTab] = useState<TabType>('disease');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [diseaseHistory, setDiseaseHistory] = useState<DiseaseHistoryItem[]>([]);
  const [yieldHistory, setYieldHistory] = useState<YieldHistoryItem[]>([]);

  // Selected item for detail view
  const [selectedDisease, setSelectedDisease] = useState<DiseaseHistoryItem | null>(null);

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
    } catch (err: any) {
      console.error(err);
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
      return date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100/50 pb-24 font-sans relative">

      {/* 1. Header Background Image Section */}
      <div className="relative w-full h-64 rounded-b-[2rem] overflow-hidden shadow-lg">
        <img
          src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2832&auto=format&fit=crop"
          alt="Agriculture Background"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 to-black/60"></div>

        {/* Title positioned over the image */}
        <div className="absolute top-8 left-6 z-10">
          <h1 className="text-3xl font-bold text-white drop-shadow-md tracking-tight">{t('history')}</h1>
          <p className="text-white/80 text-sm mt-1 font-medium">Track your farm's health and yield over time</p>
        </div>
      </div>

      {/* 2. Main Content Container - Floating upwards */}
      <div className="px-5 -mt-20 relative z-20">

        {/* Tabs */}
        <div className="bg-white/90 backdrop-blur-md p-1.5 rounded-2xl shadow-xl flex gap-2 mb-6 border border-white/50">
          <button
            onClick={() => setTab('disease')}
            className={`flex-1 py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-all ${tab === 'disease'
              ? 'bg-gradient-to-r from-teal-400 to-emerald-500 text-white shadow-lg shadow-green-500/20'
              : 'bg-transparent text-gray-500 hover:bg-gray-50 hover:text-gray-900'
              }`}
          >
            <Leaf className="w-4 h-4" />
            Disease ({diseaseHistory.length})
          </button>
          <button
            onClick={() => setTab('yield')}
            className={`flex-1 py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-all ${tab === 'yield'
              ? 'bg-gradient-to-r from-teal-400 to-emerald-500 text-white shadow-lg shadow-green-500/20'
              : 'bg-transparent text-gray-500 hover:bg-gray-50 hover:text-gray-900'
              }`}
          >
            <BarChart3 className="w-4 h-4" />
            Yield ({yieldHistory.length})
          </button>
        </div>

        {/* Section Title */}
        <h3 className="font-bold text-gray-800 text-lg mb-4 pl-1 flex items-center justify-between">
          {tab === 'disease' ? 'Disease Reports' : 'Yield Predictions'}
          <span className="text-xs font-normal text-gray-400 bg-white px-2 py-1 rounded-lg border border-gray-100">Sorted by Date</span>
        </h3>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="animate-spin text-green-600 w-8 h-8" /></div>
        ) : (
          <div className="space-y-4 pb-10">
            <AnimatePresence mode="wait">
              {tab === 'disease' ? (
                diseaseHistory.length === 0 ? (
                  <div className="text-center py-16 bg-white rounded-3xl border border-gray-100 shadow-sm">
                    <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Leaf className="text-gray-300 w-8 h-8" />
                    </div>
                    <p className="text-gray-500 font-medium">No disease history yet.</p>
                    <button className="mt-4 text-sm font-bold text-green-600 hover:underline">Start Detection</button>
                  </div>
                ) : (
                  diseaseHistory.map((item) => (
                    <motion.div
                      key={item.id}
                      layoutId={`card-${item.id}`}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      onClick={() => setSelectedDisease(item)}
                      className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 flex items-center justify-between cursor-pointer active:scale-[0.98] transition-all hover:shadow-md group"
                    >
                      <div className="flex items-center gap-4">
                        {/* Icon Circle */}
                        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 transition-colors ${item.is_healthy ? 'bg-green-50 group-hover:bg-green-100' : 'bg-red-50 group-hover:bg-red-100'}`}>
                          {item.image_url ? (
                            <img src={item.image_url} alt="" className="w-full h-full object-cover rounded-2xl" />
                          ) : (
                            item.is_healthy ? <Leaf className="text-green-600 w-6 h-6" /> : <AlertTriangle className="text-red-500 w-6 h-6" />
                          )}
                        </div>

                        <div>
                          <h4 className="font-bold text-gray-900 text-base leading-tight mb-1">
                            {item.disease_name}
                          </h4>

                          <div className="flex items-center gap-2">
                            <span className={`text-[10px] px-2 py-0.5 rounded-md font-bold uppercase tracking-wider ${item.is_healthy ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                              {item.is_healthy ? 'Healthy' : 'Risk'}
                            </span>
                            <span className="text-xs text-gray-400 font-medium flex items-center gap-1">
                              <Calendar className="w-3 h-3" /> {formatDate(item.created_at)}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center group-hover:bg-gray-100 transition-colors">
                        <ChevronRight className="text-gray-400 w-4 h-4" />
                      </div>
                    </motion.div>
                  ))
                )
              ) : (
                yieldHistory.length === 0 ? (
                  <div className="text-center py-16 bg-white rounded-3xl border border-gray-100 shadow-sm">
                    <p className="text-gray-500 font-medium">No yield predictions found.</p>
                  </div>
                ) : (
                  yieldHistory.map((item) => (
                    <div key={item.id} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center shrink-0">
                            <Sprout className="text-blue-600 w-5 h-5" />
                          </div>
                          <div>
                            <h4 className="font-bold text-gray-900">{item.crop}</h4>
                            <p className="text-xs text-gray-500">{item.district}</p>
                          </div>
                        </div>
                        <span className={`text-[10px] px-2 py-1 rounded-full font-bold border ${item.risk_level === 'Low' ? 'bg-green-50 text-green-700 border-green-100' : 'bg-yellow-50 text-yellow-700 border-yellow-100'
                          }`}>
                          {item.risk_level} Risk
                        </span>
                      </div>

                      <div className="flex items-end gap-2 mt-4 bg-gray-50 p-3 rounded-xl border border-gray-100 border-dashed">
                        <div>
                          <p className="text-[10px] text-gray-400 font-bold uppercase tracking-wider mb-1">Estimated Yield</p>
                          <p className="text-lg font-extrabold text-gray-900 leading-none">
                            {item.predicted_yield} <span className="text-xs font-bold text-gray-500">{item.unit}</span>
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )
              )}
            </AnimatePresence>
          </div>
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
              className="fixed inset-x-4 top-[15%] bottom-[15%] md:inset-y-12 md:max-w-md md:mx-auto z-50 bg-white rounded-[2rem] shadow-2xl overflow-hidden flex flex-col"
            >
              <div className="relative h-72 bg-gray-100 shrink-0">
                {selectedDisease.image_url ? (
                  <img src={selectedDisease.image_url} alt="" className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gray-50">
                    <ImageOff className="text-gray-300 w-12 h-12" />
                  </div>
                )}

                <button
                  onClick={() => setSelectedDisease(null)}
                  className="absolute top-4 right-4 p-2 bg-black/30 hover:bg-black/50 text-white rounded-full backdrop-blur-md transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>

                <div className="absolute bottom-0 inset-x-0 h-32 bg-gradient-to-t from-black/60 to-transparent flex flex-col justify-end p-6">
                  <h2 className="text-2xl font-bold text-white leading-tight">{selectedDisease.disease_name}</h2>
                  <p className="text-white/80 text-sm font-medium">{formatDate(selectedDisease.created_at)}</p>
                </div>
              </div>

              <div className="p-6 flex-1 overflow-y-auto">
                <div className="bg-gray-50 p-5 rounded-2xl mb-6 border border-gray-100">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-bold text-gray-500 uppercase tracking-wider">Confidence Level</span>
                    <span className="text-lg font-black text-gray-900">{selectedDisease.confidence}%</span>
                  </div>
                  <div className="h-3 w-full bg-gray-200 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${selectedDisease.confidence}%` }}
                      transition={{ duration: 1, delay: 0.2 }}
                      className={`h-full rounded-full ${selectedDisease.is_healthy ? 'bg-green-500' : 'bg-gradient-to-r from-orange-400 to-red-500'}`}
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-bold text-gray-900 border-l-4 border-green-500 pl-3">Analysis Details</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    Based on the image analysis, the system has detected {selectedDisease.is_healthy ? 'no signs of disease' : `signs of ${selectedDisease.disease_name}`}.
                    {selectedDisease.is_healthy && " The plant appears to be in good health."}
                  </p>
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
