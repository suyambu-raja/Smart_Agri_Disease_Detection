import { useState, useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

export const useTTS = () => {
    const { i18n } = useTranslation();
    const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [fallbackToBrowser, setFallbackToBrowser] = useState(false);

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

        // Try API first (unless we already switched to browser mode due to consistent errors)
        if (!fallbackToBrowser) {
            try {
                const lang = i18n.language === 'ta' ? 'ta' : 'en';

                const response = await fetch('/api/tts/generate/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, lang })
                });

                if (!response.ok) {
                    console.warn(`TTS API failed with status ${response.status}. Switching to browser TTS fallback.`);
                    setFallbackToBrowser(true); // Switch to browser TTS for future calls in this session
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
                console.error("TTS API Error (using fallback):", error);
                // Fallback continues below
            }
        }

        // Fallback: Browser Speech Synthesis
        try {
            const utterance = new SpeechSynthesisUtterance(text);
            const langCode = i18n.language === 'ta' ? 'ta-IN' : 'en-US';
            utterance.lang = langCode;

            // Try to set a matching voice if available
            const voices = window.speechSynthesis.getVoices();
            const voice = voices.find(v => v.lang.includes(langCode));
            if (voice) utterance.voice = voice;

            utterance.onend = () => setIsPlaying(false);
            utterance.onstart = () => setIsPlaying(true);

            window.speechSynthesis.speak(utterance);
        } catch (e) {
            console.error("Browser TTS also failed:", e);
        }

    }, [i18n.language, audio, fallbackToBrowser]);

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
