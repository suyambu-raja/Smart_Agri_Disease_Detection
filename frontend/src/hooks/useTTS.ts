import { useState, useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

// Global flag to track backend availability across the session
// If the API fails once, we switch to browser TTS for the entire session
let hasServerFailed = false;

export const useTTS = () => {
    const { i18n } = useTranslation();
    const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);

    // Clean up audio on unmount
    useEffect(() => {
        return () => {
            if (audio) {
                audio.pause();
                audio.currentTime = 0;
            }
            window.speechSynthesis.cancel();
        };
    }, [audio]);

    const speak = useCallback(async (text: string) => {
        if (!text) return;

        // Stop current audio/speech
        if (audio) {
            audio.pause();
            audio.currentTime = 0;
        }
        window.speechSynthesis.cancel();
        setIsPlaying(false);

        // Try API first (unless we already switched to browser mode globally)
        if (!hasServerFailed) {
            try {
                const lang = i18n.language === 'ta' ? 'ta' : 'en';
                const controller = new AbortController();
                // 2-second timeout to prevent "late" response perception
                const timeoutId = setTimeout(() => controller.abort(), 2000);

                const response = await fetch('/api/tts/generate/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, lang }),
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    console.warn(`TTS API failed with status ${response.status}. Switching to browser TTS fallback globally.`);
                    hasServerFailed = true; // Global switch
                    throw new Error(`API Error ${response.status}`);
                }

                const data = await response.json();

                if (data.audio_url) {
                    const newAudio = new Audio(data.audio_url);
                    newAudio.onended = () => setIsPlaying(false);
                    const playPromise = newAudio.play();
                    if (playPromise !== undefined) {
                        playPromise
                            .then(() => setIsPlaying(true))
                            .catch(e => console.error("Audio play error:", e));
                    }
                    setAudio(newAudio);
                    return; // Success, exit function
                }
            } catch (error) {
                if ((error as Error).name === 'AbortError') {
                    console.warn("TTS API timed out. Switching to browser TTS fallback globally.");
                } else {
                    console.error("TTS API Error (using fallback):", error);
                }
                hasServerFailed = true;
                // Fallback continues below
            }
        }

        // Fallback: Browser Speech Synthesis
        try {
            const utterance = new SpeechSynthesisUtterance(text);
            const langCode = i18n.language === 'ta' ? 'ta-IN' : 'en-US';
            utterance.lang = langCode;
            utterance.rate = 0.9; // Make it slightly slower and more natural
            utterance.pitch = 1.0;

            // Improve voice selection
            const voices = window.speechSynthesis.getVoices();
            // Prioritize higher quality voices if available (e.g. Google, Microsoft)
            const voice = voices.find(v => v.lang === langCode && (v.name.includes('Google') || v.name.includes('Microsoft')))
                || voices.find(v => v.lang.includes(langCode));

            if (voice) {
                utterance.voice = voice;
                // console.log("Using voice:", voice.name);
            }

            utterance.onend = () => setIsPlaying(false);
            utterance.onstart = () => setIsPlaying(true);
            utterance.onerror = (e) => console.error("TTS Error:", e);

            window.speechSynthesis.speak(utterance);
        } catch (e) {
            console.error("Browser TTS also failed:", e);
        }

    }, [i18n.language, audio]);

    const stop = useCallback(() => {
        if (audio) {
            audio.pause();
            audio.currentTime = 0;
        }
        window.speechSynthesis.cancel();
        setIsPlaying(false);
    }, [audio]);

    return { speak, stop, isPlaying };
};
