import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Camera, X, Loader2, AlertCircle, CheckCircle2, Sprout } from 'lucide-react';
import { predictDisease, getRecommendation, type DiseaseResult, type RecommendationResult } from '@/lib/api';
import { useTTS } from '@/hooks/useTTS';

const DiseaseDetection = () => {
  const { t } = useTranslation();
  const { speak } = useTTS();
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DiseaseResult | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Crop filtering state
  const [selectedCrop, setSelectedCrop] = useState<string>('');

  const crops = [
    'Apple', 'Blueberry', 'Cherry', 'Corn', 'Grape', 'Orange',
    'Peach', 'Pepper', 'Potato', 'Raspberry', 'Soybean',
    'Squash', 'Strawberry', 'Tomato'
  ];

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setRecommendation(null);
      setError(null);
    }
  };

  const clearImage = () => {
    setImage(null);
    setPreview(null);
    setResult(null);
    setRecommendation(null);
    setError(null);
    setSelectedCrop('');
  };

  const handlePredict = async () => {
    if (!image) return;

    setLoading(true);
    setError(null);
    try {
      // Send selected crop to API for better accuracy
      const data = await predictDisease(image, selectedCrop || undefined);
      setResult(data);

      if (!data.success) {
        setError('Could not detect disease. Please try another image.');
        setLoading(false);
        return;
      }

      // Fetch recommendation
      const rec = await getRecommendation(data.disease_name);
      setRecommendation(rec);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 space-y-6 pb-20">
      <h1 className="text-xl font-bold text-foreground">{t('disease_detection')}</h1>

      {/* Image Upload Area */}
      <div className="bg-card rounded-2xl shadow-sm border border-border overflow-hidden">
        <AnimatePresence mode="wait">
          {!preview ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="p-8 flex flex-col items-center justify-center text-center space-y-4"
            >
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-2">
                <Camera className="w-8 h-8 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">
                  {t('upload_instruction')}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {t('upload_hint')}
                </p>
              </div>

              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="image-upload"
              />
              <label
                htmlFor="image-upload"
                onMouseEnter={() => speak(t('upload_instruction'))}
                className="w-full py-3 px-4 bg-secondary hover:bg-secondary/80 text-secondary-foreground rounded-xl text-sm font-medium cursor-pointer transition-colors flex items-center justify-center gap-2"
              >
                <Upload className="w-4 h-4" />
                {t('upload_gallery')}
              </label>
            </motion.div>
          ) : (
            <motion.div
              key="preview"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="relative"
            >
              <img
                src={preview}
                alt="Preview"
                className="w-full aspect-video object-cover"
              />
              <button
                onClick={clearImage}
                className="absolute top-2 right-2 p-2 bg-black/50 hover:bg-black/70 text-white rounded-full transition-colors backdrop-blur-sm"
              >
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Predict Button & Crop Filter */}
        {preview && !result && (
          <div className="p-4 space-y-4 bg-secondary/30">

            {/* Crop Selector */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-muted-foreground ml-1 uppercase tracking-wider">
                {t('select_crop_label')}
              </label>
              <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-1 px-1">
                {crops.map((crop) => (
                  <button
                    key={crop}
                    onClick={() => {
                      setSelectedCrop(crop === selectedCrop ? '' : crop);
                      speak(t(`crop_${crop.toLowerCase()}`));
                    }}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all border shadow-sm ${selectedCrop === crop
                      ? 'bg-primary text-primary-foreground border-primary ring-2 ring-primary/20'
                      : 'bg-background text-foreground border-border hover:border-primary/50'
                      }`}
                  >
                    {t(`crop_${crop.toLowerCase()}`)}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handlePredict}
              disabled={loading}
              className="w-full py-3 bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl font-semibold shadow-lg shadow-primary/20 transition-all active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {t('analyzing')}
                </>
              ) : (
                t('predict')
              )}
            </button>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 rounded-xl bg-destructive/10 text-destructive text-sm flex items-start gap-3"
        >
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p>{error}</p>
        </motion.div>
      )}

      {/* Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="bg-card rounded-2xl p-5 shadow-sm border border-border space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">{t('detected_disease')}</p>
                <h2 className="text-xl font-bold text-foreground leading-tight">
                  {result.disease_name}
                </h2>
              </div>
              <div
                className={`px-3 py-1 rounded-full text-xs font-bold ${result.is_healthy
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                  : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                  }`}
              >
                {result.is_healthy ? t('healthy') : t('diseased')}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className="h-2 flex-1 bg-secondary rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${result.confidence}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className={`h-full ${result.confidence > 80 ? 'bg-primary' : 'bg-yellow-500'
                    }`}
                />
              </div>
              <span className="text-xs font-medium text-muted-foreground w-12 text-right">
                {Math.round(result.confidence)}%
              </span>
            </div>

            {selectedCrop && result.disease_name.toLowerCase().includes(selectedCrop.toLowerCase()) && (
              <div className="flex items-center gap-2 text-xs text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 p-2 rounded-lg">
                <CheckCircle2 className="w-3 h-3" />
                {t('confirmed_match')} {t(`crop_${selectedCrop.toLowerCase()}`)}
              </div>
            )}
          </div>

          {/* Recommendations */}
          {recommendation && (
            <div className="space-y-3">
              <h3 className="font-semibold text-foreground flex items-center gap-2">
                <Sprout className="w-4 h-4 text-primary" />
                {t('recommendations')}
              </h3>

              {recommendation.preventive_measures.length > 0 && (
                <div className="bg-card rounded-xl p-4 border border-border text-sm">
                  <p className="font-medium mb-2 text-primary">{t('preventive_measures')}</p>
                  <ul className="space-y-1.5 list-disc pl-4 text-muted-foreground">
                    {recommendation.preventive_measures.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}

              {recommendation.organic_treatments.length > 0 && (
                <div className="bg-card rounded-xl p-4 border border-border text-sm">
                  <p className="font-medium mb-2 text-green-600 dark:text-green-400">{t('organic_treatment')}</p>
                  <ul className="space-y-1.5 list-disc pl-4 text-muted-foreground">
                    {recommendation.organic_treatments.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}

              {recommendation.fertilizers.length > 0 && (
                <div className="bg-card rounded-xl p-4 border border-border text-sm">
                  <p className="font-medium mb-2 text-blue-600 dark:text-blue-400">{t('fertilizers')}</p>
                  <ul className="space-y-1.5 list-disc pl-4 text-muted-foreground">
                    {recommendation.fertilizers.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {result.is_healthy && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-900 rounded-xl p-6 text-center">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-800 rounded-full flex items-center justify-center mx-auto mb-3">
                <CheckCircle2 className="w-6 h-6 text-green-600 dark:text-green-300" />
              </div>
              <h3 className="font-semibold text-green-800 dark:text-green-200 mb-1">{t('healthy_title')}</h3>
              <p className="text-sm text-green-600 dark:text-green-300">
                {t('healthy_msg')}
              </p>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default DiseaseDetection;
