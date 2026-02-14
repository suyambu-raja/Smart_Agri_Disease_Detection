import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Camera, CheckCircle2, ChevronRight, Loader2, X, AlertCircle, Sprout, ShieldCheck, Beaker } from 'lucide-react';
import { predictDisease, getRecommendation, getDiseaseHistory, type DiseaseResult, type RecommendationResult, type DiseaseHistoryItem } from '@/lib/api';
import { useTTS } from '@/hooks/useTTS';

const DiseaseDetection = () => {
  const { t, i18n } = useTranslation();
  const { speak } = useTTS();
  const navigate = useNavigate();

  // Create refs for camera handling
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DiseaseResult | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastPrediction, setLastPrediction] = useState<DiseaseHistoryItem | null>(null);

  // Camera UI state
  const [isCameraOpen, setIsCameraOpen] = useState(false);

  // Crop filtering state
  const [selectedCrop, setSelectedCrop] = useState<string>('');
  const crops = [
    'Apple', 'Blueberry', 'Cherry', 'Corn', 'Grape', 'Orange',
    'Peach', 'Pepper', 'Potato', 'Raspberry', 'Soybean',
    'Squash', 'Strawberry', 'Tomato'
  ];

  // Fetch recommendation whenever result or language changes
  useEffect(() => {
    if (result && !result.is_healthy) {
      getRecommendation(result.disease_name, i18n.language)
        .then(setRecommendation)
        .catch(err => console.error("Failed to fetch recommendation", err));
    } else {
      setRecommendation(null);
    }
  }, [result, i18n.language]);

  useEffect(() => {
    // Fetch last prediction for the UI
    getDiseaseHistory().then(res => {
      if (res.data && res.data.length > 0) {
        setLastPrediction(res.data[0]);
      }
    }).catch(err => console.error("Failed to fetch history", err));
  }, []);

  // Camera Logic
  const startCamera = async () => {
    setIsCameraOpen(true);
    setError(null);
  };

  const stopCamera = () => {
    const stream = videoRef.current?.srcObject as MediaStream;
    stream?.getTracks().forEach(track => track.stop());
    setIsCameraOpen(false);
  };

  useEffect(() => {
    if (isCameraOpen) {
      navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(stream => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        })
        .catch(err => {
          console.error("Camera error", err);
          setError("Unable to access camera. Please use upload.");
          setIsCameraOpen(false);
        });
    }
    return () => {
      // Cleanup on unmount or close
      const stream = videoRef.current?.srcObject as MediaStream;
      stream?.getTracks().forEach(track => track.stop());
    };
  }, [isCameraOpen]);

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
            setImage(file);
            setPreview(URL.createObjectURL(file));
            setResult(null);
            setRecommendation(null);
            setError(null);
            stopCamera();
          }
        }, 'image/jpeg');
      }
    }
  };

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
      const data = await predictDisease(image, selectedCrop || undefined);
      setResult(data);

      if (!data.success) {
        setError('Could not detect disease. Please try another image.');
        setLoading(false);
        return;
      }

      // Recommendation will be fetched by useEffect


      // Refresh last prediction after successful new one
      getDiseaseHistory().then(res => {
        if (res.data && res.data.length > 0) setLastPrediction(res.data[0]);
      });

    } catch (err: any) {
      setError(err.message || 'Failed to analyze image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24 font-sans px-4 pt-4">

      {/* LIVE CAMERA OVERLAY */}
      {isCameraOpen && (
        <div className="fixed inset-0 z-50 bg-black flex flex-col">
          <div className="relative flex-1 bg-black">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="absolute inset-0 w-full h-full object-cover"
            />

            {/* Overlay Guides */}
            <div className="absolute inset-0 border-[2px] border-white/30 m-8 rounded-lg pointer-events-none">
              <div className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-white"></div>
              <div className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-white"></div>
              <div className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-white"></div>
              <div className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-white"></div>
            </div>

            <button
              onClick={stopCamera}
              className="absolute top-4 right-4 p-3 bg-black/50 text-white rounded-full z-50"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <div className="h-32 bg-black flex items-center justify-center gap-8 pb-8 pt-4">
            <button
              onClick={capturePhoto}
              className="w-20 h-20 rounded-full border-4 border-white flex items-center justify-center active:scale-95 transition-transform"
            >
              <div className="w-16 h-16 bg-white rounded-full"></div>
            </button>
          </div>
          <canvas ref={canvasRef} className="hidden" />
        </div>
      )}


      <div className="max-w-md md:max-w-7xl mx-auto space-y-6">
        <h1 className="text-xl font-bold text-gray-900">{t('disease_detection')}</h1>

        {/* MAIN ACTION CARD */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
          {/* LEFT COLUMN */}
          <div className="md:col-span-7 lg:col-span-8 space-y-6">
            <div className="bg-white rounded-[2rem] p-6 shadow-sm border border-gray-100 text-center relative overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-b from-teal-50/50 via-green-50/50 to-transparent pointer-events-none"></div>

              <div className="relative z-10">
                <div className="w-20 h-20 bg-gradient-to-br from-teal-100 to-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Camera className="w-10 h-10 text-[#4a7a40]" />
                </div>

                <h2 className="text-lg font-bold text-gray-900 mb-4">{t('Take Photo or upload')}</h2>

                {/* Filters */}
                <div className="mb-6 overflow-x-auto pb-2 -mx-2 px-2 scrollbar-hide">
                  <div className="flex gap-2 justify-center min-w-max">
                    {crops.map((crop) => (
                      <button
                        key={crop}
                        onClick={() => {
                          setSelectedCrop(crop === selectedCrop ? '' : crop);
                          speak(crop);
                        }}
                        className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all ${selectedCrop === crop
                          ? 'bg-gradient-to-r from-teal-400 to-emerald-500 text-white shadow-md shadow-green-500/20 border-none'
                          : 'bg-white text-gray-700 border border-gray-200 hover:border-green-400'
                          }`}
                      >
                        {t(`crop_${crop.toLowerCase()}`) || crop}
                      </button>
                    ))}
                  </div>
                </div>

                {!preview ? (
                  <div className="space-y-3">
                    {/* Hidden Inputs */}
                    <input type="file" accept="image/*" id="gallery-input" onChange={handleImageUpload} className="hidden" />

                    {/* Buttons : Live Camera Trigger */}
                    <button
                      onClick={startCamera}
                      className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-teal-400 to-emerald-500 hover:from-teal-600 hover:to-green-700 text-white font-bold py-3.5 rounded-xl cursor-pointer shadow-lg shadow-green-500/30 active:scale-[0.98] transition-all"
                    >
                      <Camera className="w-5 h-5" />
                      {t('take_photo') || 'Take Photo'}
                    </button>

                    <label htmlFor="gallery-input" className="w-full flex items-center justify-center gap-2 bg-white border border-gray-300 text-gray-800 font-bold py-3.5 rounded-xl cursor-pointer hover:bg-gray-50 active:scale-[0.98] transition-all">
                      <Upload className="w-5 h-5 text-gray-600" />
                      {t('upload_gallery')}
                    </label>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="relative rounded-xl overflow-hidden shadow-md">
                      <img src={preview} alt="Preview" className="w-full h-48 object-cover" />
                      <button onClick={clearImage} className="absolute top-2 right-2 p-1.5 bg-black/60 text-white rounded-full backdrop-blur-sm">
                        <X className="w-4 h-4" />
                      </button>
                    </div>

                    {!result && (
                      <button
                        onClick={handlePredict}
                        disabled={loading}
                        className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-teal-400 to-emerald-500 hover:from-teal-600 hover:to-green-700 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-green-500/30 active:scale-[0.98] transition-all"
                      >
                        {loading ? <Loader2 className="animate-spin w-5 h-5" /> : t('predict')}
                      </button>
                    )}
                  </div>
                )}

                <p className="text-xs text-gray-500 mt-4 font-semibold">
                  {t('upload_hint') || 'Ensure the leaf is clearly visible and well-lit'}
                </p>
              </div>
            </div>

          </div>


          {/* RIGHT COLUMN */}
          <div className="md:col-span-5 lg:col-span-4 space-y-6">

            {/* TIPS SECTION */}
            <div className="bg-[#F8FAF9] rounded-[1.5rem] p-6 border border-gray-200">
              <h3 className="font-bold text-gray-800 mb-4">{t('tips') || 'Tips'}</h3>
              <ul className="space-y-3">
                {[
                  'tip_visible',
                  'tip_shadows',
                  'tip_lighting'
                ].map((tip, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-green-600 shrink-0 mt-0.5" />
                    <span className="text-sm text-gray-700 font-medium leading-tight">{t(tip) || tip}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* PREDICTION RESULT - DETAILED VIEW */}
            <AnimatePresence>
              {result && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="fixed inset-0 z-50 bg-gray-50 md:bg-black/60 md:backdrop-blur-sm md:flex md:items-center md:justify-center overflow-y-auto md:overflow-hidden"
                >
                  <div className="w-full h-full md:h-auto md:max-h-[90vh] md:max-w-2xl bg-gray-50 md:rounded-3xl md:shadow-2xl md:overflow-hidden flex flex-col relative">
                    {/* Header */}
                    <div className="bg-white p-4 shadow-sm flex items-center justify-between sticky top-0 z-10">
                      <button onClick={clearImage} className="p-2 -ml-2 text-gray-600 hover:bg-gray-100 rounded-full">
                        <X className="w-6 h-6" />
                      </button>
                      <h2 className="font-bold text-gray-800">Result</h2>
                      <div className="w-8"></div>
                    </div>

                    <div className="p-5 max-w-md mx-auto space-y-6">
                      {/* Summary Card */}
                      <div className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100 text-center">
                        <div className={`w-20 h-20 mx-auto rounded-full flex items-center justify-center mb-4 ${result.is_healthy ? 'bg-green-100' : 'bg-red-50'}`}>
                          {result.is_healthy ? <CheckCircle2 className="w-10 h-10 text-green-600" /> : <AlertCircle className="w-10 h-10 text-red-500" />}
                        </div>
                        <h2 className="text-2xl font-extrabold text-gray-900 leading-tight mb-2">{result.disease_name}</h2>
                        <div className="flex items-center justify-center gap-3">
                          <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-lg text-sm font-bold border border-gray-200">
                            Conf: {Math.round(result.confidence)}%
                          </span>
                          {!result.is_healthy && (
                            <span className="px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm font-bold">
                              Action Needed
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Show Image */}
                      {preview && (
                        <div className="rounded-2xl overflow-hidden shadow-sm border border-gray-200">
                          <img src={preview} alt="Analyzed" className="w-full h-48 object-cover" />
                        </div>
                      )}

                      {/* Detailed Recommendations */}
                      {recommendation && !result.is_healthy && (
                        <div className="space-y-6">
                          {/* Treatment */}
                          <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
                            <h3 className="font-bold text-gray-900 flex items-center gap-2 text-lg mb-3">
                              <div className="bg-green-100 p-1.5 rounded-lg"><Sprout className="w-5 h-5 text-green-700" /></div>
                              {t('treatment')}
                            </h3>
                            <div className="space-y-3">
                              {recommendation.organic_treatments.length > 0 && (
                                <div>
                                  <p className="text-xs font-bold text-green-600 uppercase tracking-wider mb-2">Organic</p>
                                  <ul className="space-y-2">
                                    {recommendation.organic_treatments.map((item, i) => (
                                      <li key={i} className="text-sm text-gray-800 flex gap-2">
                                        <span className="text-green-500 mt-1">•</span> {item}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              {recommendation.pesticides && recommendation.pesticides.length > 0 && (
                                <div className="pt-2 border-t border-gray-100 mt-2">
                                  <p className="text-xs font-bold text-orange-600 uppercase tracking-wider mb-2 mt-2">Chemical</p>
                                  <ul className="space-y-2">
                                    {recommendation.pesticides.map((item, i) => (
                                      <li key={i} className="text-sm text-gray-800 flex gap-2">
                                        <span className="text-orange-500 mt-1">•</span> {item}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Prevention */}
                          {recommendation.preventive_measures.length > 0 && (
                            <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
                              <h3 className="font-bold text-gray-900 flex items-center gap-2 text-lg mb-3">
                                <div className="bg-blue-100 p-1.5 rounded-lg"><ShieldCheck className="w-5 h-5 text-blue-700" /></div>
                                {t('prevention')}
                              </h3>
                              <ul className="space-y-2">
                                {recommendation.preventive_measures.map((item, i) => (
                                  <li key={i} className="text-sm text-gray-800 flex gap-2">
                                    <CheckCircle2 className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                                    {item}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Fertilizers */}
                          {recommendation.fertilizers.length > 0 && (
                            <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
                              <h3 className="font-bold text-gray-900 flex items-center gap-2 text-lg mb-3">
                                <div className="bg-purple-100 p-1.5 rounded-lg"><Beaker className="w-5 h-5 text-purple-700" /></div>
                                {t('fertilizers')}
                              </h3>
                              <ul className="space-y-2">
                                {recommendation.fertilizers.map((item, i) => (
                                  <li key={i} className="text-sm text-gray-800 flex gap-2">
                                    <span className="text-purple-500 mt-1">•</span> {item}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}

                      {result.is_healthy && (
                        <div className="bg-white p-8 rounded-3xl text-center shadow-sm border border-green-100">
                          <p className="text-lg text-gray-700 font-medium">Your plant looks healthy! Keep up the good work.</p>
                        </div>
                      )}

                      <button
                        onClick={clearImage}
                        className="w-full py-4 bg-gradient-to-r from-teal-400 to-emerald-500 text-white font-bold text-lg rounded-2xl shadow-lg shadow-green-500/30 active:scale-[0.98] transition-all"
                      >
                        {t('done')}
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* LAST PREDICTION */}
            {lastPrediction && !result && !preview && (
              <div
                onClick={() => navigate('/history')}
                className="bg-white rounded-[1.5rem] p-5 shadow-sm border border-gray-100 cursor-pointer hover:shadow-md transition-all active:scale-[0.98]"
              >
                <h3 className="text-sm font-bold text-gray-500 mb-3 uppercase tracking-wider">{t('last_prediction') || 'Last Prediction'}</h3>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-14 h-14 rounded-full flex items-center justify-center shrink-0 border-2 ${lastPrediction.is_healthy ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'}`}>
                      {lastPrediction.image_url ? (
                        <img src={lastPrediction.image_url} className="w-full h-full object-cover rounded-full" alt="" />
                      ) : (
                        <Sprout className={`w-6 h-6 ${lastPrediction.is_healthy ? 'text-green-600' : 'text-red-500'}`} />
                      )}
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900 text-base">{lastPrediction.disease_name}</h4>
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-xs text-gray-600 font-semibold">{t('confidence')}: <span className="text-gray-900">{lastPrediction.confidence}%</span></span>
                        {!lastPrediction.is_healthy && (
                          <span className="text-[10px] bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-bold">High Risk</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="text-gray-400 w-5 h-5" />
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div >
  );
};

export default DiseaseDetection;
