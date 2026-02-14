import { useEffect, useState } from 'react';
import { X, Share, PlusSquare } from 'lucide-react';

export function PwaPrompt() {
    const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
    const [showPrompt, setShowPrompt] = useState(false);
    const [isIOS, setIsIOS] = useState(false);

    useEffect(() => {
        // 1. Detect iOS
        const userAgent = window.navigator.userAgent.toLowerCase();
        const isIosDevice = /iphone|ipad|ipod/.test(userAgent);

        // 2. Check if already running in standalone mode (PWA installed)
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches || (window.navigator as any).standalone === true;

        if (isStandalone) {
            return; // Already installed, don't nag
        }

        if (isIosDevice) {
            setIsIOS(true);
            // Show prompt after a short delay on iOS to not be annoying immediately
            const timer = setTimeout(() => setShowPrompt(true), 3000);
            return () => clearTimeout(timer);
        }

        // 3. Listen for default install prompt (Chrome/Android)
        const handleBeforeInstallPrompt = (e: any) => {
            // Prevent the mini-infobar from appearing on mobile
            e.preventDefault();
            // Stash the event so it can be triggered later.
            setDeferredPrompt(e);
            // Update UI notify the user they can install the PWA
            setShowPrompt(true);
        };

        window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

        return () => {
            window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
        };
    }, []);

    const handleInstallClick = async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            if (outcome === 'accepted') {
                console.log('User accepted the install prompt');
                setDeferredPrompt(null);
            }
            setShowPrompt(false);
        }
    };

    if (!showPrompt) return null;

    return (
        <div className="fixed bottom-20 left-4 right-4 z-50 bg-primary text-primary-foreground p-4 rounded-xl shadow-xl flex flex-col gap-3 animate-in slide-in-from-bottom-5 border border-primary-foreground/20">
            <div className="flex items-start justify-between">
                <div>
                    <h3 className="font-semibold text-base mb-1">Install Smart Agriculture</h3>
                    <p className="text-xs opacity-90 leading-relaxed">
                        {isIOS
                            ? "Install inside Safari for offline access and a native app experience."
                            : "Install our app for offline access, faster loading, and a better experience."}
                    </p>
                </div>
                <button onClick={() => setShowPrompt(false)} className="opacity-70 hover:opacity-100 p-1">
                    <X className="w-5 h-5" />
                </button>
            </div>

            {isIOS ? (
                <div className="flex flex-col gap-2 text-xs bg-primary-foreground/10 p-2 rounded mt-1">
                    <div className="flex items-center gap-2">
                        <Share className="w-4 h-4" />
                        <span>1. Tap the <strong>Share</strong> button</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <PlusSquare className="w-4 h-4" />
                        <span>2. Scroll down & tap <strong>Add to Home Screen</strong></span>
                    </div>
                </div>
            ) : (
                <button
                    onClick={handleInstallClick}
                    className="w-full bg-background text-foreground text-sm font-bold py-2.5 rounded-lg shadow-sm hover:bg-muted transition-colors mt-1"
                >
                    Install App
                </button>
            )}
        </div>
    );
}
