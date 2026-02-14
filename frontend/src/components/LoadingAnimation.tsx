import React, { useState, useEffect } from 'react';
import { CloudRain } from 'lucide-react';

export function LoadingAnimation() {
    const [step, setStep] = useState(0);

    useEffect(() => {
        // Sequence timing
        const timers = [
            setTimeout(() => setStep(1), 500),   // Soil & Seed
            setTimeout(() => setStep(2), 1500),  // Rain
            setTimeout(() => setStep(3), 2800),  // Grow Stem
            setTimeout(() => setStep(4), 3400),  // Unfold Leaves
        ];
        return () => timers.forEach(clearTimeout);
    }, []);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-emerald-50 fixed inset-0 z-[60] overflow-hidden">
            <style>{`
        /* Seed Drop */
        @keyframes seedDrop {
          0% { transform: translateY(-100px); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateY(0); opacity: 1; }
        }

        /* Rain */
        @keyframes rainDrop {
          0% { transform: translateY(0); opacity: 1; }
          100% { transform: translateY(20px); opacity: 0; }
        }

        /* Plant Growth */
        @keyframes stemGrow {
          from { stroke-dashoffset: 60; }
          to { stroke-dashoffset: 0; }
        }

        @keyframes leafUnfoldLeft {
          from { transform: scale(0) rotate(45deg); }
          to { transform: scale(1) rotate(0deg); }
        }

        @keyframes leafUnfoldRight {
          from { transform: scale(0) rotate(-45deg); }
          to { transform: scale(1) rotate(0deg); }
        }

        /* Pulse Ring at the end */
        @keyframes pulseComplete {
          0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
          70% { transform: scale(1); box-shadow: 0 0 0 20px rgba(16, 185, 129, 0); }
          100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
      `}</style>

            {/* Animation Circle Container */}
            <div
                className={`relative w-56 h-56 bg-white rounded-full shadow-xl flex items-center justify-center mb-10 z-10 transition-all duration-500 ${step >= 4 ? 'ring-4 ring-emerald-100' : ''}`}
                style={{ animation: step >= 4 ? 'pulseComplete 2s infinite' : 'none' }}
            >

                {/* SCENE: SOIL & SEED (Step 1+) */}
                <div className="absolute bottom-10 flex flex-col items-center">
                    {/* Soil Mound */}
                    <div className={`w-16 h-4 bg-amber-800/20 rounded-[50%] blur-sm transition-opacity duration-700 ${step >= 1 ? 'opacity-100' : 'opacity-0'}`}></div>

                    {/* Seed */}
                    {step >= 1 && step < 3 && (
                        <div
                            className="w-3 h-3 bg-amber-700 rounded-full -mt-2 relative z-10"
                            style={{ animation: 'seedDrop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)' }}
                        ></div>
                    )}
                </div>

                {/* SCENE: RAIN (Step 2 Only) */}
                {step === 2 && (
                    <div className="absolute top-12 flex flex-col items-center animate-pulse">
                        <CloudRain className="w-10 h-10 text-blue-400 mb-1" />
                        <div className="flex gap-2">
                            <div className="w-0.5 h-3 bg-blue-400 rounded-full" style={{ animation: 'rainDrop 0.6s infinite' }}></div>
                            <div className="w-0.5 h-3 bg-blue-400 rounded-full" style={{ animation: 'rainDrop 0.6s infinite 0.2s' }}></div>
                            <div className="w-0.5 h-3 bg-blue-400 rounded-full" style={{ animation: 'rainDrop 0.6s infinite 0.4s' }}></div>
                        </div>
                    </div>
                )}

                {/* SCENE: PLANT GROWTH (Step 3+) */}
                {step >= 3 && (
                    <div className="absolute bottom-12 z-20">
                        <svg width="100" height="100" viewBox="0 0 100 100" className="overflow-visible">

                            {/* Stem: Grows upwards */}
                            <path
                                d="M50 100 Q50 70 50 40"
                                fill="none"
                                stroke="#10B981"
                                strokeWidth="6"
                                strokeLinecap="round"
                                strokeDasharray="60"
                                strokeDashoffset="0"
                                style={{ animation: 'stemGrow 1s ease-out forwards' }}
                            />

                            {/* Left Leaf: Unfolds from stem center */}
                            {step >= 4 && (
                                <g style={{ transformOrigin: '50px 50px', animation: 'leafUnfoldLeft 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards' }}>
                                    <path
                                        d="M50 50 Q30 50 20 30 Q40 20 50 50"
                                        fill="#10B981"
                                    />
                                </g>
                            )}

                            {/* Right Leaf: Unfolds from stem center */}
                            {step >= 4 && (
                                <g style={{ transformOrigin: '50px 50px', animation: 'leafUnfoldRight 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) 0.1s forwards' }}>
                                    <path
                                        d="M50 50 Q70 50 80 30 Q60 20 50 50"
                                        fill="#34D399"
                                    />
                                </g>
                            )}
                        </svg>
                    </div>
                )}
            </div>

            {/* Text Feedback */}
            <div className="h-16 flex flex-col items-center z-10 text-center">
                <h2 className="text-xl font-bold text-emerald-900 transition-all duration-300">
                    {step === 0 && "Initializing..."}
                    {step === 1 && "Sowing Data Seeds..."}
                    {step === 2 && "Hydrating Analysis..."}
                    {step >= 3 && "Growing Insights..."}
                </h2>

                {/* Progress Bar */}
                <div className="mt-4 w-48 h-1.5 bg-emerald-100 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-emerald-500 transition-all duration-700 ease-out"
                        style={{ width: `${(step / 4) * 100}%` }}
                    />
                </div>
            </div>

            {/* Decorative Background */}
            <div className="absolute bottom-0 w-full h-1/3 bg-gradient-to-t from-emerald-100 to-transparent opacity-50 pointer-events-none"></div>
        </div>
    );
}
